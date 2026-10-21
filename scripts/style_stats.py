"""Compare writing-style statistics between texts (.txt or .docx).

Usage: python -I style_stats.py muestra.txt documento.docx [otro.txt ...]
Prints, per file: average sentence length, spread, share of long (>35) and short (<12) sentences,
connectors per 1000 words and the most common sentence openings.
"""
import collections, os, re, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_text import document_text

CONNECTORS = ['on the other hand', 'likewise', 'in addition', 'it should be mentioned', 'it should be noted',
              'in this sense', 'for this reason', 'thanks to', 'to this end', 'in this way', 'in order to',
              'the present study', 'therefore', 'however', 'moreover', 'furthermore', 'additionally',
              'although', 'because', 'since', 'given that', 'while']
sys.stdout.reconfigure(encoding='utf-8')

for path in sys.argv[1:]:
    text = document_text(path) if path.lower().endswith('.docx') else open(path, encoding='utf-8', errors='ignore').read()
    # stop at the reference list if there is one
    text = re.split(r'\n\s*(References|Referencias|Bibliography)\s*\n', text)[0]
    text = re.sub(r'\s+', ' ', text)
    sents = [s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z])', text) if len(s.split()) > 3]
    if not sents:
        print(f'== {path}: sin oraciones'); continue
    L = [len(s.split()) for s in sents]
    n = len(text.split())
    print(f'== {os.path.basename(path)}: {n} palabras, {len(sents)} oraciones')
    print(f'   largo medio {st.mean(L):.1f}  desviación {st.pstdev(L):.1f}  '
          f'>35 palabras {sum(l > 35 for l in L) / len(L):.0%}  <12 palabras {sum(l < 12 for l in L) / len(L):.0%}')
    low = text.lower()
    c = {k: round(len(re.findall(r'\b' + k + r'\b', low)) * 1000 / n, 1) for k in CONNECTORS}
    print('   conectores cada 1000 palabras:', {k: v for k, v in c.items() if v})
    starts = collections.Counter(' '.join(s.split()[:2]).strip(',') for s in sents)
    print('   comienzos más comunes:', starts.most_common(8))
