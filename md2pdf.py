#!/usr/bin/env python3
"""
md2pdf — Convert Markdown files to PDF with GitHub-style rendering.

Usage:
    python md2pdf.py                  # interactive: scan CWD and pick files
    python md2pdf.py README.md        # convert specific file(s)
    python md2pdf.py *.md             # convert all .md files in CWD
"""

import argparse
import importlib.util
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------

def _require(package: str, install_hint: str) -> None:
    if importlib.util.find_spec(package) is None:
        print(f"[error] Missing package '{package}'. Install with: {install_hint}")
        sys.exit(1)

_require("markdown", "pip install markdown")
_require("weasyprint", "pip install weasyprint")
_require("pygments", "pip install pygments")

import markdown
from weasyprint import HTML, CSS  # noqa: E402

# ---------------------------------------------------------------------------
# Embedded GitHub-style CSS
# ---------------------------------------------------------------------------

GITHUB_CSS = """
*, *::before, *::after { box-sizing: border-box; }

html { font-size: 16px; }

body {
    font-family: Helvetica, Arial, "Noto Sans", sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #1f2328;
    background-color: #ffffff;
    max-width: 860px;
    margin: 0 auto;
    padding: 40px 48px;
}

/* ── Headings ─────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
    color: #1f2328;
}
h1 { font-size: 2em;   padding-bottom: 0.3em; border-bottom: 1px solid #d1d9e0; }
h2 { font-size: 1.5em; padding-bottom: 0.3em; border-bottom: 1px solid #d1d9e0; }
h3 { font-size: 1.25em; }
h4 { font-size: 1em; }
h5 { font-size: 0.875em; }
h6 { font-size: 0.85em;  color: #59636e; }

/* ── Paragraphs & spacing ─────────────────────────────────────────────── */
p  { margin-top: 0; margin-bottom: 16px; }
hr { height: 0.25em; padding: 0; margin: 24px 0; background-color: #d1d9e0; border: 0; }

/* ── Links ────────────────────────────────────────────────────────────── */
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }

/* ── Emphasis ─────────────────────────────────────────────────────────── */
strong { font-weight: 600; }
em     { font-style: italic; }
del    { text-decoration: line-through; color: #59636e; }

/* ── Blockquote ───────────────────────────────────────────────────────── */
blockquote {
    margin: 0 0 16px 0;
    padding: 0 1em;
    color: #59636e;
    border-left: 0.25em solid #d1d9e0;
}
blockquote > :first-child { margin-top: 0; }
blockquote > :last-child  { margin-bottom: 0; }

/* ── Lists ────────────────────────────────────────────────────────────── */
ul, ol {
    margin-top: 0;
    margin-bottom: 16px;
    padding-left: 2em;
}
li { margin-top: 0.25em; }
li > p { margin-top: 16px; }
li::marker { color: #1f2328; }
ul ul, ul ol, ol ol, ol ul { margin-bottom: 0; }

/* ── Task lists ───────────────────────────────────────────────────────── */
.task-list-item { list-style-type: none; }
.task-list-item input[type="checkbox"] { margin: 0 0.5em 0 -1.6em; }

/* ── Tables ───────────────────────────────────────────────────────────── */
table {
    border-spacing: 0;
    border-collapse: collapse;
    display: block;
    width: max-content;
    max-width: 100%;
    overflow: auto;
    margin-top: 0;
    margin-bottom: 16px;
}
thead { background-color: #f6f8fa; }
th, td {
    padding: 6px 13px;
    border: 1px solid #d1d9e0;
}
th { font-weight: 600; }
tr:nth-child(even) { background-color: #f6f8fa; }

/* ── Inline code ──────────────────────────────────────────────────────── */
code {
    font-family: Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 85%;
    padding: 0.2em 0.4em;
    margin: 0;
    background-color: #f6f8fa;
    border-radius: 6px;
    color: #e8337d;
}

/* ── Fenced code blocks ───────────────────────────────────────────────── */
pre {
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    color: #24292e;
    background-color: #f6f8fa;
    border-radius: 6px;
    margin-top: 0;
    margin-bottom: 16px;
    word-break: normal;
}
pre code {
    padding: 0;
    margin: 0;
    background-color: transparent;
    border: 0;
    word-break: normal;
    white-space: pre;
    color: #24292e;
}

/* ── Pygments highlight theme (GitHub-light) ──────────────────────────── */
.highlight .hll { background-color: #ffffcc; }
.highlight      { background: #f6f8fa; color: #24292e; }
.highlight .c   { color: #6a737d; font-style: italic }   /* Comment */
.highlight .cm  { color: #6a737d; font-style: italic }   /* Comment.Multiline */
.highlight .cp  { color: #6a737d }                        /* Comment.Preproc */
.highlight .c1  { color: #6a737d; font-style: italic }   /* Comment.Single */
.highlight .cs  { color: #6a737d; font-style: italic }   /* Comment.Special */
.highlight .k   { color: #d73a49; font-weight: bold }    /* Keyword */
.highlight .kc  { color: #005cc5; font-weight: bold }    /* Keyword.Constant */
.highlight .kd  { color: #d73a49; font-weight: bold }    /* Keyword.Declaration */
.highlight .kn  { color: #d73a49; font-weight: bold }    /* Keyword.Namespace */
.highlight .kp  { color: #d73a49 }                        /* Keyword.Pseudo */
.highlight .kr  { color: #d73a49; font-weight: bold }    /* Keyword.Reserved */
.highlight .kt  { color: #d73a49 }                        /* Keyword.Type */
.highlight .s   { color: #032f62 }                        /* Literal.String */
.highlight .sa  { color: #032f62 }                        /* String.Affix */
.highlight .sb  { color: #032f62 }                        /* String.Backtick */
.highlight .sc  { color: #032f62 }                        /* String.Char */
.highlight .dl  { color: #032f62 }                        /* String.Delimiter */
.highlight .sd  { color: #032f62; font-style: italic }   /* String.Doc */
.highlight .s2  { color: #032f62 }                        /* String.Double */
.highlight .se  { color: #032f62 }                        /* String.Escape */
.highlight .sh  { color: #032f62 }                        /* String.Heredoc */
.highlight .si  { color: #032f62 }                        /* String.Interpol */
.highlight .sx  { color: #032f62 }                        /* String.Other */
.highlight .sr  { color: #032f62 }                        /* String.Regex */
.highlight .s1  { color: #032f62 }                        /* String.Single */
.highlight .ss  { color: #032f62 }                        /* String.Symbol */
.highlight .m   { color: #005cc5 }                        /* Literal.Number */
.highlight .mb  { color: #005cc5 }                        /* Number.Bin */
.highlight .mf  { color: #005cc5 }                        /* Number.Float */
.highlight .mh  { color: #005cc5 }                        /* Number.Hex */
.highlight .mi  { color: #005cc5 }                        /* Number.Integer */
.highlight .mo  { color: #005cc5 }                        /* Number.Oct */
.highlight .na  { color: #6f42c1 }                        /* Name.Attribute */
.highlight .nb  { color: #005cc5 }                        /* Name.Builtin */
.highlight .nc  { color: #6f42c1; font-weight: bold }    /* Name.Class */
.highlight .nd  { color: #6f42c1 }                        /* Name.Decorator */
.highlight .ne  { color: #6f42c1; font-weight: bold }    /* Name.Exception */
.highlight .nf  { color: #6f42c1 }                        /* Name.Function */
.highlight .nl  { color: #6f42c1 }                        /* Name.Label */
.highlight .nn  { color: #6f42c1 }                        /* Name.Namespace */
.highlight .nt  { color: #22863a }                        /* Name.Tag */
.highlight .nv  { color: #e36209 }                        /* Name.Variable */
.highlight .o   { color: #d73a49 }                        /* Operator */
.highlight .ow  { color: #d73a49; font-weight: bold }    /* Operator.Word */
.highlight .p   { color: #24292e }                        /* Punctuation */
.highlight .w   { color: #bbbbbb }                        /* Text.Whitespace */

/* ── Images ───────────────────────────────────────────────────────────── */
img { max-width: 100%; height: auto; }

/* ── Print / page setup ───────────────────────────────────────────────── */
@page {
    margin: 1cm;
    size: A4;
}
pre, blockquote, table, figure { page-break-inside: avoid; }
h1, h2, h3, h4, h5, h6 { page-break-after: avoid; }
"""

# ---------------------------------------------------------------------------
# Markdown → HTML → PDF
# ---------------------------------------------------------------------------

MARKDOWN_EXTENSIONS = [
    "extra",          # tables, footnotes, attr_list, fenced_code, …
    "codehilite",     # syntax highlighting via Pygments
    "toc",            # [TOC] macro + anchor links
    "sane_lists",     # don't mix ordered/unordered list markers
    "nl2br",          # single newline → <br>
    "meta",           # YAML-ish front-matter (ignored in output)
    "admonition",     # !!! note / warning / tip blocks
]

EXTENSION_CONFIGS = {
    "codehilite": {
        "guess_lang": False,
        "css_class": "highlight",
        "linenums": False,
    },
    "toc": {
        "permalink": False,
    },
}

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
</head>
<body>
{body}
</body>
</html>
"""


def md_to_pdf(md_path: Path) -> Path:
    """Convert a single Markdown file to PDF. Returns the output PDF path."""
    md_text = md_path.read_text(encoding="utf-8")

    md = markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=EXTENSION_CONFIGS,
        output_format="html",
    )
    body_html = md.convert(md_text)

    full_html = HTML_TEMPLATE.format(
        title=md_path.stem,
        body=body_html,
    )

    pdf_path = md_path.with_suffix(".pdf")

    HTML(string=full_html, base_url=str(md_path.parent)).write_pdf(
        pdf_path,
        stylesheets=[CSS(string=GITHUB_CSS)],
    )
    return pdf_path


# ---------------------------------------------------------------------------
# Interactive file selection
# ---------------------------------------------------------------------------

def list_md_files(directory: Path) -> list[Path]:
    """Return sorted list of .md files in *directory* (non-recursive)."""
    return sorted(directory.glob("*.md"))


def prompt_selection(files: list[Path]) -> list[Path]:
    """Show a numbered menu and return the user-selected subset."""
    if not files:
        print("No .md files found in the current directory.")
        sys.exit(0)

    print()
    print("Markdown files found:")
    for i, f in enumerate(files, 1):
        print(f"  {i:>3}. {f.name}")
    print()
    print("Select files to convert.")
    print("  Examples: 1  |  1,3,5  |  2-4  |  1,3-5,7  |  all")
    print()

    while True:
        raw = input("Your selection: ").strip().lower()
        if not raw:
            print("  [!] Nothing selected, please try again.")
            continue
        if raw == "all":
            return files
        selected = _parse_selection(raw, len(files))
        if selected is None:
            print(f"  [!] Invalid input — use numbers 1–{len(files)}, ranges, or 'all'.")
            continue
        if not selected:
            print("  [!] Nothing selected, please try again.")
            continue
        return [files[i] for i in sorted(selected)]


def _parse_selection(raw: str, max_n: int) -> list[int] | None:
    """
    Parse a selection string like '1,3-5,7' into a list of 0-based indices.
    Returns None on parse error.
    """
    indices: set[int] = set()
    parts = raw.replace(" ", "").split(",")
    for part in parts:
        if not part:
            return None
        if "-" in part:
            bounds = part.split("-")
            if len(bounds) != 2:
                return None
            try:
                lo, hi = int(bounds[0]), int(bounds[1])
            except ValueError:
                return None
            if lo < 1 or hi > max_n or lo > hi:
                return None
            indices.update(range(lo - 1, hi))
        else:
            try:
                n = int(part)
            except ValueError:
                return None
            if n < 1 or n > max_n:
                return None
            indices.add(n - 1)
    return list(indices)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PDF (GitHub-style).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python md2pdf.py                        # interactive, scans CWD\n"
            "  python md2pdf.py -d ~/docs              # interactive, scans ~/docs\n"
            "  python md2pdf.py README.md              # convert one file\n"
            "  python md2pdf.py doc1.md doc2.md        # convert multiple files\n"
        ),
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help=".md file(s) to convert. If omitted, scans the directory.",
    )
    parser.add_argument(
        "-d", "--dir",
        metavar="DIR",
        default=None,
        help="Directory to scan for .md files (default: script's directory).",
    )
    args = parser.parse_args()

    if args.files:
        targets: list[Path] = []
        for name in args.files:
            p = Path(name)
            if not p.exists():
                print(f"[warn] File not found, skipping: {p}")
            elif p.suffix.lower() != ".md":
                print(f"[warn] Not a .md file, skipping: {p}")
            else:
                targets.append(p)
        if not targets:
            print("[error] No valid .md files provided.")
            sys.exit(1)
    else:
        scan_dir = Path(args.dir).expanduser().resolve() if args.dir else Path(__file__).parent.resolve()
        if not scan_dir.is_dir():
            print(f"[error] Not a directory: {scan_dir}")
            sys.exit(1)

        while True:
            print(f"Scanning: {scan_dir}")
            all_files = list_md_files(scan_dir)
            if all_files:
                break
            print(f"  No .md files found in {scan_dir}")
            raw = input("  Enter a directory to scan (or press Enter to quit): ").strip()
            if not raw:
                sys.exit(0)
            candidate = Path(raw).expanduser().resolve()
            if not candidate.is_dir():
                print(f"  [!] Not a valid directory: {candidate}")
            else:
                scan_dir = candidate

        targets = prompt_selection(all_files)

    print()
    errors: list[str] = []
    for md_path in targets:
        pdf_path = md_path.with_suffix(".pdf")
        if pdf_path.exists():
            answer = input(f"  {pdf_path.name} already exists. Overwrite? [y/N] ").strip().lower()
            if answer != "y":
                print(f"  Skipped  {md_path.name}")
                continue
        print(f"  Converting  {md_path.name} ...", end=" ", flush=True)
        try:
            md_to_pdf(md_path)
            print(f"→  {pdf_path.name}")
        except Exception as exc:  # noqa: BLE001
            print("FAILED")
            errors.append(f"    {md_path.name}: {exc}")

    print()
    if errors:
        print("Errors:")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        total = len(targets)
        noun = "file" if total == 1 else "files"
        print(f"Done. Converted {total} {noun}.")


if __name__ == "__main__":
    main()
