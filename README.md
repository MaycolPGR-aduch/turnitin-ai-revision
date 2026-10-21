# turnitin-ai-revision

Skill para Claude Code que revisa documentos académicos en Word (.docx) para bajar el índice de IA de Turnitin.
Se guía por el informe de IA de Turnitin y por una muestra de texto humano del mismo grupo.

Es el flujo con el que un artículo en inglés pasó de **81 % a menos de 20 %** en cuatro rondas:

| Ronda | Qué se hizo | IA |
|---|---|---|
| Original | — | 81 % |
| A | Corrección de errores y reescritura general con patrones de IA | 43 % |
| B | Reescritura a fondo de los segmentos marcados | 36 % |
| C | Imitar una muestra humana del mismo laboratorio, solo en lo marcado | menos de 20 % |

## Instalación

**Desde GitHub** (desde la carpeta de tu proyecto):

```bash
git clone https://github.com/MaycolPGR-aduch/turnitin-ai-revision.git .claude/skills/turnitin-ai-revision
```

Para tenerla en todos tus proyectos, clónala en `~/.claude/skills/turnitin-ai-revision`.

**Manual:** copia la carpeta `turnitin-ai-revision` en uno de estos lugares:

- **Solo para un proyecto:** `<carpeta del proyecto>/.claude/skills/turnitin-ai-revision/`
- **Para todos tus proyectos:** `~/.claude/skills/turnitin-ai-revision/` (en Windows: `C:\Users\<usuario>\.claude\skills\`)

Abre una sesión nueva de Claude Code en esa carpeta. La skill aparece como `/turnitin-ai-revision` y también se
activa sola cuando pides bajar el porcentaje de IA de un documento.

**Recomendado:** instala también la skill [blader/humanizer](https://github.com/blader/humanizer), que tiene el
catálogo completo de patrones de IA. Esta skill incluye un resumen por si no está.

**Requisitos:** Python 3 con `lxml` (`pip install lxml`). Para revisar el formato en PDF hace falta Microsoft Word
en Windows (`scripts/export_pdf.ps1`); en otros sistemas se puede usar LibreOffice.

## Cómo usarla

Pon en la carpeta del proyecto el .docx, el informe de IA de Turnitin en PDF y, si la tienes, la muestra humana
(.doc, .docx o .pdf). Después escribe, por ejemplo:

```
/turnitin-ai-revision
Documento: articulo.docx
Informe de Turnitin: informe1.pdf
Muestra de estilo: paper_del_laboratorio.doc (escrito por personas, 0 % de IA)
Nivel: moderado
```

Claude va a leer el informe, corregir primero los errores objetivos, reescribir solo lo marcado y entregar una
nueva versión (`v2`, `v3`, …) con un archivo de comparación. Tú la pasas por Turnitin y le das el nuevo informe
para la siguiente ronda.

## Lo que más importa

1. **La muestra humana es lo que más funciona.** Debe ser un texto del mismo grupo, redactado o parafraseado por
   personas (no con QuillBot u otras herramientas) y con 0 % o menos de 20 % de IA en Turnitin.
2. **Solo se toca lo que Turnitin sigue marcando.** Lo que ya sale limpio queda igual.
3. **No se inventan datos y no se pierden citas ni cifras.** El script de reemplazos lo verifica.
4. **No se copian frases de la muestra**, porque subiría la similitud. Se imita el estilo y el script avisa si
   hay coincidencias.
5. "*%" en Turnitin significa que el puntaje está por debajo del 20 %.

Recuerda revisar la política de tu institución sobre el uso de IA en trabajos académicos.

## Contenido

```
turnitin-ai-revision/
├── SKILL.md                     instrucciones para Claude (flujo, reglas, estilo)
├── README.md                    este archivo
└── scripts/
    ├── docx_text.py             funciones compartidas para leer y guardar el .docx
    ├── extract_paragraphs.py    lista los párrafos con su texto exacto
    ├── apply_replacements.py    aplica cambios desde JSON con verificaciones
    ├── style_stats.py           compara el estilo de la muestra y el documento
    └── export_pdf.ps1           exporta a PDF con Word para revisar el formato
```
