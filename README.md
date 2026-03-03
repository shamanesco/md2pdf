# md2pdf

Convert Markdown files to PDF with GitHub-style rendering. No external binaries required.

## Features

- GitHub-style typography and colors (fully self-contained — no internet required at render time)
- Syntax-highlighted fenced code blocks via [Pygments](https://pygments.org/)
- Tables, blockquotes, footnotes, task lists, admonitions
- Interactive file selector when no arguments are given
- A4 page size with sensible print margins

## Requirements

- Python 3.10+
- [markdown](https://python-markdown.github.io/) — Markdown parser
- [weasyprint](https://weasyprint.org/) — HTML/CSS → PDF renderer
- [pygments](https://pygments.org/) — syntax highlighting

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Interactive mode (no arguments)

```bash
python md2pdf.py                    # scans the script's own directory
python md2pdf.py -d ~/docs          # scans a specific directory
python md2pdf.py --dir /some/path   # same, long form
```

Scans the target directory for `.md` files and presents a numbered menu:

```
Markdown files found:
    1. CHANGELOG.md
    2. CONTRIBUTING.md
    3. README.md

Select files to convert.
  Examples: 1  |  1,3,5  |  2-4  |  1,3-5,7  |  all

Your selection: 1,3
```

### Direct mode

```bash
python md2pdf.py README.md                  # single file
python md2pdf.py doc1.md doc2.md            # multiple files
python md2pdf.py *.md                       # glob
```

Each `.md` file produces a `.pdf` in the same directory:

```
README.md  →  README.pdf
doc1.md    →  doc1.pdf
```

## Supported Markdown syntax

| Feature | Syntax |
|---|---|
| Headings | `# H1` through `###### H6` |
| Bold / italic | `**bold**`, `_italic_` |
| Strikethrough | `~~text~~` |
| Inline code | `` `code` `` |
| Fenced code block | ` ```python ` … ` ``` ` |
| Table | `\| col \| col \|` |
| Blockquote | `> text` |
| Task list | `- [x] done` / `- [ ] todo` |
| Footnote | `text[^1]` … `[^1]: note` |
| Table of contents | `[TOC]` |
| Admonition | `!!! note "Title"` |

## Project structure

```
md2pdf/
├── md2pdf.py          # main script
├── requirements.txt   # pinned dependencies
└── README.md
```
