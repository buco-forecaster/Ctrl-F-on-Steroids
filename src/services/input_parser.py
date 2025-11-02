from pathlib import Path
from typing import Tuple, List, Dict, Optional
from config.settings import (
    QUERY_DELIMITER,
    FOLLOWUP_DELIMITER,
    DEFAULT_FOLLOWUP_BLOCK,
    VARIABLES_SEPARATOR,
    CONTENT_TEMPLATE_BEGIN,
    CONTENT_TEMPLATE_END,
    CONTENT_SEPARATOR,
)
import re

def read_queries_file(path: str = "queries.txt") -> Tuple[Optional[list], List[Dict[str, list]]]:
    """
    Strict structured-mode parser for templated batch queries.
    - Requires global ---CONTENT_TEMPLATE--- ... ---END_CONTENT_TEMPLATE---.
    - Each segment must have ---VARIABLES_SEPARATOR--- with a !OUTPUT_NAME=... directive.
    - Legacy (plain) mode is NOT supported or fallback anymore.

    Returns: (defaults, segments), where each segment is
        {"query": <final_prompt>, "followups": [], "output_name": <str>}
    """
    text = Path(path).read_text(encoding="utf-8").lstrip()

    # Check for required markers.
    if not (CONTENT_TEMPLATE_BEGIN in text and CONTENT_TEMPLATE_END in text):
        raise ValueError(
            f"The queries file must contain both {CONTENT_TEMPLATE_BEGIN} and {CONTENT_TEMPLATE_END}."
        )
    if VARIABLES_SEPARATOR not in text:
        raise ValueError(
            f"Each query segment must contain {VARIABLES_SEPARATOR} and a !OUTPUT_NAME directive."
        )

    defaults = None
    segments_part = text

    if text.startswith(DEFAULT_FOLLOWUP_BLOCK):
        parts = text.split(DEFAULT_FOLLOWUP_BLOCK, 1)[1]
        first_split = parts.split(QUERY_DELIMITER, 1)
        defaults_block = first_split[0]
        segments_part = first_split[1] if len(first_split) > 1 else ""
        defaults = [chunk.strip() for chunk in defaults_block.strip().split(FOLLOWUP_DELIMITER) if chunk.strip()]

    def extract_template_block(body):
        start = body.find(CONTENT_TEMPLATE_BEGIN)
        end = body.find(CONTENT_TEMPLATE_END)
        if start == -1 or end == -1:
            raise ValueError(
                f"Missing {CONTENT_TEMPLATE_BEGIN} ... {CONTENT_TEMPLATE_END} block."
            )
        tpl = body[start + len(CONTENT_TEMPLATE_BEGIN):end].strip()
        before = body[:start]
        after = body[end + len(CONTENT_TEMPLATE_END):]
        return tpl, before + after

    template, segments_body = extract_template_block(segments_part)
    # Everything after the template and DEFAULT_FOLLOWUP is split by QUERY_DELIMITER
    segments = [s.strip() for s in segments_body.split(QUERY_DELIMITER) if s.strip()]
    result = []
    output_name_pattern = re.compile(r"^!OUTPUT_NAME\s*=(.+)$", re.IGNORECASE)
    for i, seg in enumerate(segments):
        vars_block = ""
        seg_content = None

        # Find VARIABLES block
        if VARIABLES_SEPARATOR in seg:
            v_idx = seg.index(VARIABLES_SEPARATOR) + len(VARIABLES_SEPARATOR)
            next_marker_idx = min(
                [seg.find(marker, v_idx) if marker in seg[v_idx:] else len(seg) for marker in [
                    CONTENT_SEPARATOR, VARIABLES_SEPARATOR, CONTENT_TEMPLATE_BEGIN, CONTENT_TEMPLATE_END
                ]]
            )
            vars_block = seg[v_idx: v_idx + next_marker_idx].strip()
            seg_rest = seg[v_idx + next_marker_idx:]
        else:
            raise ValueError(
                f"Segment {i+1} is missing the required {VARIABLES_SEPARATOR} block."
            )

        # Check for CONTENT_SEPARATOR (overrides template)
        content_override = None
        if CONTENT_SEPARATOR in seg:
            co_idx = seg.index(CONTENT_SEPARATOR) + len(CONTENT_SEPARATOR)
            content_override = seg[co_idx:].strip()

        # Require !OUTPUT_NAME directive in vars_block
        output_name = None
        lines = [line.strip() for line in vars_block.splitlines()]
        preface_lines = []
        for line in lines:
            m = output_name_pattern.match(line)
            if m:
                output_name = m.group(1).strip()
            elif line and not line.startswith("!"):  # !-directives, skip from preface
                preface_lines.append(line)
        if not output_name:
            raise ValueError(
                f"Segment {i+1} missing required !OUTPUT_NAME=... directive in VARIABLES block."
            )

        # The prompt construction: preface + blank line + content (global template or override)
        prompt = ""
        if preface_lines:
            prompt += "\n".join(preface_lines) + "\n\n"
        prompt += content_override if content_override is not None else template

        result.append({
            "query": prompt.strip(),
            "followups": [],
            "output_name": output_name,
        })
    return defaults, result
