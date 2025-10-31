from src.cli.chrome_gemini import open_gemini_chrome

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=["chrome", "firefox"], default="chrome")
    parser.add_argument("query", nargs="?", default=None)
    parser.add_argument("url", nargs="?", default="https://gemini.google.com/app")
    args = parser.parse_args()

    open_gemini_chrome(url=args.url)

if __name__ == "__main__":
    main()
