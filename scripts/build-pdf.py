#!/usr/bin/env python3
"""Build a PDF from a Hugo-rendered HTML file using WeasyPrint.

Usage:
    python scripts/build-pdf.py [<input.html> <output.pdf>]
    python scripts/build-pdf.py --input public/index.html --output public/resume.pdf

Defaults:
    input  → public/resume.html
    output → public/resume.pdf

Requirements:
    pip install weasyprint==69.0
"""

from __future__ import annotations

import argparse
import os
import sys

try:
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration
    from weasyprint import WeasyPrintError
except ImportError as exc:
    print(f"Error: WeasyPrint is not installed ({exc}).", file=sys.stderr)
    print("Install it with: pip install weasyprint==69.0", file=sys.stderr)
    sys.exit(1)


# ──────────────────────────────────────────────
# Path resolution
# ──────────────────────────────────────────────

def resolve_path(path: str, anchor: str) -> str:
    """Resolve *path* relative to the directory containing *anchor*.

    If *path* is already absolute it is returned unchanged.
    """
    if os.path.isabs(path):
        return path
    base = os.path.dirname(os.path.abspath(anchor))
    return os.path.normpath(os.path.join(base, path))


# ──────────────────────────────────────────────
# Argument parsing
# ──────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a Hugo-rendered HTML file to PDF via WeasyPrint.",
    )
    parser.add_argument(
        "input_html",
        nargs="?",
        default="public/resume.html",
        help="Path to the rendered HTML file (default: public/resume.html)",
    )
    parser.add_argument(
        "output_pdf",
        nargs="?",
        default="public/resume.pdf",
        help="Path for the generated PDF (default: public/resume.pdf)",
    )
    parser.add_argument(
        "--input",
        dest="input_flag",
        help="Input HTML file (overrides positional argument).",
    )
    parser.add_argument(
        "--output",
        dest="output_flag",
        help="Output PDF file (overrides positional argument).",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    ns = parser.parse_args(argv)

    # Flags override positional args, which override defaults.
    input_path = ns.input_flag if ns.input_flag is not None else ns.input_html
    output_path = ns.output_flag if ns.output_flag is not None else ns.output_pdf

    ns.input_path = input_path
    ns.output_path = output_path
    return ns


# ──────────────────────────────────────────────
# PDF rendering
# ──────────────────────────────────────────────

def render_pdf(input_path: str, output_path: str) -> None:
    """Render *input_path* HTML to *output_path* PDF via WeasyPrint."""

    abs_input = os.path.abspath(input_path)
    abs_output = os.path.abspath(output_path)

    # Validate input exists.
    if not os.path.isfile(abs_input):
        print(
            f"Error: input file not found — {abs_input}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Ensure output directory exists.
    output_dir = os.path.dirname(abs_output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # WeasyPrint may handle @font-face via FontConfiguration.
    # If the HTML references web fonts with @font-face, uncomment the
    # font_config argument below.  For most resume use-cases the system
    # fonts are sufficient, so it is left out by default.
    #
    #   font_config = FontConfiguration()
    #   doc.write_pdf(abs_output, font_config=font_config)
    #

    print(f"Rendering {abs_input} → {abs_output}")

    try:
        doc = HTML(filename=abs_input)
        doc.write_pdf(
            abs_output,
            presentational_hints=True,
            optimize_images=True,
        )
    except WeasyPrintError as exc:
        print(
            f"Error: WeasyPrint failed to process {abs_input} — {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    size = os.path.getsize(abs_output)
    print(f"Done: {abs_output} ({_format_size(size)})")


def _format_size(n_bytes: int) -> str:
    """Return a human-readable byte-size string."""
    if n_bytes < 1024:
        return f"{n_bytes} B"
    elif n_bytes < 1024**2:
        return f"{n_bytes / 1024:.1f} KiB"
    elif n_bytes < 1024**3:
        return f"{n_bytes / 1024**2:.1f} MiB"
    else:
        return f"{n_bytes / 1024**3:.2f} GiB"


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def main() -> None:
    ns = parse_args()
    render_pdf(ns.input_path, ns.output_path)


if __name__ == "__main__":
    main()
