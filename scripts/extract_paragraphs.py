"""List the paragraphs of a .docx with their exact text, to prepare replacements.

Usage: python -I extract_paragraphs.py documento.docx [--tables]
Output: one block per paragraph: [index] (T = inside a table) text
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_text import load, paragraphs

ap = argparse.ArgumentParser()
ap.add_argument('docx')
ap.add_argument('--tables', action='store_true', help='include table cells')
a = ap.parse_args()
sys.stdout.reconfigure(encoding='utf-8')

_, tree = load(a.docx)
i = 0
for _, _, text, tbl in paragraphs(tree):
    if not text.strip() or (tbl and not a.tables):
        continue
    i += 1
    print(f"[{i}]{' T' if tbl else ''} {text}\n")
