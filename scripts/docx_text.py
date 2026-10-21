"""Shared helpers: read word/document.xml from a .docx and walk its paragraphs."""
import zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W, 'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006'}
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'

# Single-character substitutions only, so string offsets stay identical after normalizing.
NORMALIZE = str.maketrans({' ': ' ', '’': "'", '‘': "'", '“': '"', '”': '"'})


def load(docx_path):
    """Return (zip entries as {name: bytes}, parsed document.xml tree)."""
    with zipfile.ZipFile(docx_path) as z:
        entries = {n: z.read(n) for n in z.namelist()}
    tree = etree.fromstring(entries['word/document.xml'])
    return entries, tree


def save(entries, tree, out_path):
    entries = dict(entries)
    entries['word/document.xml'] = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        names = list(entries)
        if '[Content_Types].xml' in names:  # keep it first, as Word does
            names.remove('[Content_Types].xml')
            names.insert(0, '[Content_Types].xml')
        for n in names:
            z.writestr(n, entries[n])


def paragraphs(tree):
    """Yield (paragraph element, list of its own w:t elements, concatenated text, in_table).

    Text boxes are stored twice by Word (mc:Choice and an mc:Fallback copy); the fallback copy is skipped.
    A paragraph that anchors a text box only gets its own text, not the text of the paragraphs nested inside it.
    """
    for p in tree.iter('{%s}p' % W):
        if p.xpath('ancestor::mc:Fallback', namespaces=NS):
            continue
        ts = [t for t in p.xpath('.//w:t', namespaces=NS) if t.xpath('ancestor::w:p[1]', namespaces=NS)[0] is p]
        text = ''.join(t.text or '' for t in ts)
        yield p, ts, text, bool(p.xpath('ancestor::w:tbl', namespaces=NS))


def document_text(docx_path, include_tables=False):
    _, tree = load(docx_path)
    return '\n'.join(text for _, _, text, tbl in paragraphs(tree) if text.strip() and (include_tables or not tbl))
