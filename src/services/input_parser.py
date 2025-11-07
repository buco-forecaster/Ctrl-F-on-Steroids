from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Block headers and separator (can be imported from config if desired)
BLOCK_SEPARATOR = '---'
HDR_DEFAULTS = '@DEFAULT_FOLLOWUPS'
HDR_GLOBALS = '@GLOBALS'
HDR_SEGMENT = '@SEGMENT'
HDR_CONTENT = '@CONTENT'

def _split_blocks(text: str) -> List[str]:
    blocks, buf = [], []
    for line in text.splitlines():
        if line.strip() == BLOCK_SEPARATOR:
            if buf:
                blocks.append("\n".join(buf).strip())
                buf = []
        else:
            buf.append(line)
    if buf:
        blocks.append("\n".join(buf).strip())
    return blocks

def _parse_key_value_block(lines: List[str]) -> Dict[str, str]:
    result = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line:
            i += 1
            continue
        key, rest = line.split(":", 1)
        key = key.strip()
        value = rest.lstrip()
        if value == "|":
            i += 1
            multin = []
            # Collect all indented lines
            while i < len(lines):
                if lines[i].startswith("  ") or (lines[i].startswith("\t")):
                    multin.append(lines[i][2:] if lines[i].startswith("  ") else lines[i].lstrip("\t"))
                    i += 1
                elif lines[i].strip() == "":
                    multin.append("")
                    i += 1
                else:
                    break
            result[key] = "\n".join(multin).rstrip()
        else:
            result[key] = value.rstrip()
            i += 1
    return result

def _parse_defaults_block(block: str) -> Dict[str, str]:
    lines = block.splitlines()
    if not lines or not lines[0].strip().startswith(HDR_DEFAULTS):
        return {}
    return _parse_key_value_block(lines[1:])

def _parse_globals_block(block: str) -> List[str]:
    lines = block.splitlines()
    if not lines or not lines[0].strip().startswith(HDR_GLOBALS):
        return []
    return [ln for ln in lines[1:] if ln.strip()]

def _parse_segment_block(block: str, template: str, defaults: Dict[str, str], globals_preface: Optional[List[str]] = None) -> Dict[str, str]:
    lines = [ln for ln in block.splitlines()]
    if not lines or not lines[0].strip().startswith(HDR_SEGMENT):
        raise ValueError("Segment block must start with @SEGMENT")
    analysis_id: Optional[str] = None
    preface: List[str] = []
    local_followups: Dict[str, str] = {}
    in_followups = False
    followup_lines: List[str] = []

    for idx, raw in enumerate(lines[1:]):
        ln = raw.strip()
        if not ln:
            if not in_followups:
                preface.append(raw)
            continue
        if ln.upper().startswith("FOLLOWUPS:"):
            in_followups = True
            continue
        if not in_followups:
            kv = _parse_key_value_line(raw)
            if kv and kv[0].upper() == "ANALYSIS_ID":
                analysis_id = kv[1]
            else:
                preface.append(raw)
        else:
            followup_lines.append(raw)

    if in_followups and followup_lines:
        local_followups = _parse_key_value_block(followup_lines)

    if not analysis_id:
        raise ValueError("Segment is missing required ANALYSIS_ID: ... line")

    merged_followups = dict(defaults) if defaults else {}
    if local_followups:
        merged_followups.update(local_followups)

    prompt_parts: List[str] = []
    if globals_preface and any(s.strip() for s in globals_preface):
        prompt_parts.append("\n".join(globals_preface).strip())
    if any(s.strip() for s in preface):
        prompt_parts.append("\n".join(preface).strip())
    prompt_parts.append(template.strip())
    prompt = "\n\n".join(part for part in prompt_parts if part)

    return {
        "query": prompt,
        "followups": merged_followups,
        "analysis_id": analysis_id,
    }

def _parse_key_value_line(line: str) -> Optional[Tuple[str, str]]:
    if not line.strip() or ":" not in line:
        return None
    k, v = line.split(":", 1)
    return k.strip(), v.strip()

def read_queries_file(path: str = "queries.txt"):
    text = Path(path).read_text(encoding="utf-8").lstrip()
    blocks = _split_blocks(text)
    if not blocks:
        raise ValueError("Empty queries file")

    # CONTENT must be last block
    content_block = blocks[-1]
    content_lines = content_block.splitlines()
    if not content_lines or not content_lines[0].strip().startswith(HDR_CONTENT):
        raise ValueError("Last block must begin with @CONTENT")
    template = "\n".join(content_lines[1:]).strip()
    if not template:
        raise ValueError("CONTENT block is empty")

    idx = 0
    defaults = {}
    globals_preface = None

    if blocks[0].strip().startswith(HDR_DEFAULTS):
        defaults = _parse_defaults_block(blocks[0])
        idx += 1

    if idx < len(blocks)-1 and blocks[idx].strip().startswith(HDR_GLOBALS):
        globals_preface = _parse_globals_block(blocks[idx])
        idx += 1

    segments: List[Dict[str, str]] = []
    for b in blocks[idx:-1]:
        segments.append(_parse_segment_block(b, template, defaults, globals_preface))

    return (defaults if defaults else None), segments
