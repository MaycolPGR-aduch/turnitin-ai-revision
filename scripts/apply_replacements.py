"""Apply exact-text replacements to a .docx and check that nothing factual was lost.

Usage:
  python -I apply_replacements.py in.docx changes.json out.docx [--sample muestra.txt] [--report comparacion.md] [--force]

changes.json: [{"old": "exact text from the document", "new": "rewritten text"}, ...]
- "old" must appear exactly once in the document and inside a single paragraph. Non-breaking spaces and
  curly/straight quotes are treated as equal when matching.
- The text may be split across several runs; the replacement keeps the formatting of the first run it touches.
Checks per change: citations, numbered [n] or author-year (APA), must be identical (error unless --force), numbers (warning),
6-word sequences shared with the style sample (warning), em/en dashes introduced (warning).
"""
import argparse, collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_text import load, save, paragraphs, NORMALIZE, XML_SPACE, NS

ap = argparse.ArgumentParser()
ap.add_argument('docx_in'); ap.add_argument('changes'); ap.add_argument('docx_out')
ap.add_argument('--sample', help='plain-text style sample, to detect copied phrases')
ap.add_argument('--report', help='write a before/after Markdown comparison here')
ap.add_argument('--force', action='store_true', help='apply even if citations differ')
a = ap.parse_args()
sys.stdout.reconfigure(encoding='utf-8')

changes = json.load(open(a.changes, encoding='utf-8'))
entries, tree = load(a.docx_in)
paras = list(paragraphs(tree))
# Paragraphs of the fallback copies that Word keeps for text boxes (skipped by paragraphs()).
fallback = [[t for t in p.xpath('.//w:t', namespaces=NS) if t.xpath('ancestor::w:p[1]', namespaces=NS)[0] is p]
            for p in tree.xpath('//mc:Fallback//w:p', namespaces=NS)]

APA = re.compile(r"([A-Z][\w'’-]+)(?: et al\.)?(?:,| \(| (?:and|&) [A-Z][\w-]+,| (?:and|&) [A-Z][\w-]+ \()\s?((?:19|20)\d{2})")


def cites(s):
    """Numbered citations [n] plus author-year citations (surname, year), e.g. 'Turner et al., 2025'."""
    found = re.findall(r'\[\d+\]', s) + [f'{a} {y}' for a, y in APA.findall(s)]
    return collections.Counter(found)


nums = lambda s: collections.Counter(re.findall(r'\d+(?:[.,]\d+)?%?', s))
words = lambda s: re.findall(r"[a-z0-9']+", s.lower().translate(NORMALIZE))
grams = set()
if a.sample:
    sw = words(open(a.sample, encoding='utf-8', errors='ignore').read())
    grams = {tuple(sw[i:i + 6]) for i in range(len(sw) - 5)}


def replace_in_paragraph(ts, start, end, new):
    """Replace characters [start, end) of the paragraph text, spread over w:t nodes."""
    pos, first = 0, True
    for t in ts:
        txt = t.text or ''
        s, e = pos, pos + len(txt)
        pos = e
        if not (s < end and e > start):  # this node does not overlap the replaced span
            continue
        if first:
            tail = txt[end - s:] if end <= e else ''
            t.text = txt[:start - s] + new + tail
            first = False
        else:
            t.text = txt[end - s:] if end <= e else ''
        t.set(XML_SPACE, 'preserve')
        if end <= e:
            break


errors, warnings, report = 0, 0, ['# Comparación antes / después\n']
for k, ch in enumerate(changes, 1):
    old, new = ch['old'], ch['new']
    key = old.translate(NORMALIZE)
    hits = [(i, text.translate(NORMALIZE).find(key)) for i, (_, _, text, _) in enumerate(paras)
            if key in text.translate(NORMALIZE)]
    total = sum(paras[i][2].translate(NORMALIZE).count(key) for i, _ in hits)
    if total != 1:
        print(f'[{k}] ERROR: "old" aparece {total} veces (debe ser 1): {old[:80]}...')
        errors += 1
        continue
    if cites(old) != cites(new):
        print(f'[{k}] ERROR: las citas cambian {dict(cites(old))} -> {dict(cites(new))}')
        if not a.force:
            errors += 1
            continue
    if nums(old) != nums(new):
        print(f'[{k}] AVISO: cifras distintas, faltan {dict(nums(old) - nums(new))}, nuevas {dict(nums(new) - nums(old))}')
        warnings += 1
    nw = words(new)
    shared = sorted({' '.join(nw[i:i + 6]) for i in range(len(nw) - 5) if tuple(nw[i:i + 6]) in grams})
    if shared:
        print(f'[{k}] AVISO: frases de 6 palabras iguales a la muestra: {shared}')
        warnings += 1
    if re.search('[—–]', new) and not re.search('[—–]', old):
        print(f'[{k}] AVISO: el texto nuevo agrega guiones largos')
        warnings += 1
    i, start = hits[0]
    p, ts, text, tbl = paras[i]
    replace_in_paragraph(ts, start, start + len(old), new)
    paras[i] = (p, ts, ''.join(t.text or '' for t in ts), tbl)
    # Keep Word's fallback copy of a text box in sync with the edited main copy.
    for fts in fallback:
        ftext = ''.join(t.text or '' for t in fts).translate(NORMALIZE)
        if ftext.count(key) == 1:
            replace_in_paragraph(fts, ftext.find(key), ftext.find(key) + len(old), new)
            print(f'[{k}] también actualizado en la copia de respaldo del cuadro de texto')
    report += [f'## Cambio {k}\n', f'**Antes:** {old}\n', f'**Ahora:** {new}\n']

print(f'\nCambios: {len(changes)}  errores: {errors}  avisos: {warnings}')
if errors:
    sys.exit('No se guardó el documento: corrige los errores y vuelve a ejecutar.')
save(entries, tree, a.docx_out)
print('Guardado:', a.docx_out)
if a.report:
    open(a.report, 'w', encoding='utf-8').write('\n'.join(report))
    print('Comparación:', a.report)
