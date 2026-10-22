---
name: turnitin-ai-revision
description: |
  Revisa un documento académico en Word (.docx) para bajar el índice de IA que marca Turnitin,
  guiándose por el informe de IA de Turnitin y por una muestra de texto humano del mismo grupo.
  Úsala cuando el usuario comparta un .docx junto con un informe de Turnitin (PDF) y pida bajar
  el porcentaje de IA, "humanizar" el documento o reescribir los segmentos marcados.
license: MIT
metadata:
  version: "1.3.0"
  based-on: "blader/humanizer (patrones) + flujo probado en tres artículos de la UCH (81 %, 27 % y 31 % -> menos de 20 %)"
---

# Revisión de documentos marcados como IA por Turnitin

Este flujo bajó un artículo en inglés de **81 % a menos de 20 %** en cuatro rondas. Reescribir con un inglés
nativo "limpio" se estancó entre 35 y 45 %. Lo que funcionó al final fue **imitar el estilo de un texto escrito
por personas del mismo grupo**, aplicado **solo a los segmentos que Turnitin seguía marcando**.

Los scripts de apoyo están en `scripts/` dentro de esta skill. Para llamarlos, usa la ruta absoluta de esta carpeta.

## Reglas que no se negocian

1. **No inventar datos.** Nunca agregar nombres, cifras, fechas, lugares, equipos, citas ni resultados que no
   estén en el documento o que el usuario no haya dado. Quien pide la revisión suele ser un editor, no el autor,
   y no puede confirmar detalles del estudio.
2. **Conservar todas las citas y cifras.** `apply_replacements.py` lo verifica en cada cambio. Si falla, corrige
   el texto en lugar de forzarlo.
3. **No tocar lo que Turnitin ya no marca.** Si se reescribe, puede volver a aparecer marcado.
4. **No copiar frases de la muestra de estilo.** Esa muestra suele estar en el repositorio de Turnitin, así que
   copiarla sube la similitud. Imita el estilo, no el texto. El script avisa cuando hay secuencias de 6 palabras
   compartidas. Las fórmulas genéricas como "it should be mentioned that" se aceptan.
5. **Trabajar siempre sobre copias versionadas** (`v2`, `v3`, …). Nunca sobrescribir el original.
6. Si el texto es un trabajo académico, recuérdale al usuario **una sola vez** que revise la política de su
   institución sobre el uso de IA. No lo repitas.

## Qué pedir al inicio (en un solo mensaje)

- El **.docx** y el **informe de IA de Turnitin en PDF**.
- **Una muestra de texto humano**: un paper o informe del mismo grupo, laboratorio o universidad, redactado o
  parafraseado por personas, que en Turnitin haya salido con **0 % o menos de 20 % de IA**. Es lo que más ayuda.
  Pregunta cómo se hizo: si se parafraseó con QuillBot u otra herramienta no sirve, porque Turnitin detecta el
  parafraseo automático.
- Qué nivel de imitación prefiere: **moderado** (conectores y estructura del idioma de origen, gramática correcta;
  es el recomendado y el que funcionó) o **fuerte** (además, cierta torpeza de traducción).

## Paso 1: leer el informe

- Con `pdftotext` solo se obtiene el texto, sin los resaltados. Para ver qué está marcado hay que **leer las páginas
  del PDF como imagen** (Read con `pages`) y anotar qué oraciones están resaltadas en celeste.
- Anota el porcentaje y la cantidad de segmentos, y haz una lista de lo marcado y lo no marcado por sección. Los
  títulos de figuras y tablas y las celdas cortas también pueden aparecer marcados.
- Busca qué tienen en común los segmentos limpios. En el caso probado, el texto con datos concretos del propio
  estudio no se marcaba y el texto genérico de encuadre sí.

## Paso 2: corregir errores objetivos (copia "corregido")

Antes de reescribir, revisa y corrige en una copia:
- **Restos de búsqueda web de una IA** pegados en el texto: "Sage Journals", "Springer", "PubMed", "JMIR" en medio de
  oraciones o al final de referencias.
- Oraciones duplicadas, numeración de secciones inconsistente, títulos o tablas en otro idioma, fuentes distintas
  en una sección pegada desde otro lado.
- **Restos de traducción automática:** palabras pegadas o con letras de más ("assumptQions", "CRP-as"), términos
  cambiados ("gender" donde el resto dice "sex") y oraciones que **invierten el sentido** ("did not merely assess"
  donde la oración siguiente dice que *solo* se evaluó eso). Revisa cada oración contra su contexto.
- **Notas de un editor de IA pegadas al texto:** frases que hablan del documento y no del estudio ("the original
  manuscript", "the researcher pointed out", "new raster/values", "a figure that cannot be verified with the
  available material", "we have been able to verify"). En el tercer documento probado fueron lo que más marcó
  Turnitin. Conviértelas en limitaciones dichas por los autores y conserva lo que afirman, sin mencionar el
  manuscrito. Reduce también las salvedades repetidas ("does not by itself…", "does not constitute…").
- **Citas que apuntan a la referencia equivocada.** Compara cada afirmación con el título de la referencia. Corrige
  solo los casos claros y reporta los dudosos y las referencias que no se citan para que el usuario decida.

## Paso 3: rondas de reescritura

Usa `scripts/extract_paragraphs.py` para obtener el texto exacto de cada párrafo, escribe los reemplazos en un JSON
y aplícalos con `scripts/apply_replacements.py` (ver "Scripts").

**Si el porcentaje es moderado (menos de 40 %) y ya tienes la muestra humana,** salta directamente a la ronda C.
En el segundo documento probado (27 %), el texto ya alternaba conectores del español con oraciones cortas y
uniformes (desviación de 8 palabras) y abusaba de "Furthermore" y "However". Esos dos rasgos son los que hay que
corregir.

**Ronda A, solo si el porcentaje es muy alto (más de 60 %):** pasada general por sección con los patrones de la
skill `humanizer`, si está instalada; si no, con el resumen de abajo. En el caso probado bajó de 81 % a 43 %.

**Ronda B, solo lo marcado:** reescribe a fondo los segmentos resaltados. Cambia el orden del argumento, parte las
listas de 4 o más elementos y alterna oraciones cortas y largas. Bajó de 43 % a 36 %, y ahí se estancó.

**Ronda C, imitar la muestra humana (lo que funcionó):**
1. Mide la muestra y el documento con `scripts/style_stats.py`: largo medio de las oraciones, porcentaje de
   oraciones de más de 35 palabras, conectores cada 1000 palabras y comienzos de oración más comunes.
2. Reescribe **solo las oraciones todavía marcadas**. En un párrafo marcado a medias, reemplaza solo las oraciones
   resaltadas.
3. Acerca el estilo a la muestra. En el caso probado, la muestra (inglés pensado en español) tenía:
   - oraciones largas encadenadas, de unas 32 palabras de media, y casi ninguna de menos de 12;
   - comienzos como "On the other hand", "Likewise", "In addition", "In this sense", "It should be mentioned that",
     "For this reason", "Thanks to", "To this end", y expresiones como "the present study";
   - frases nominales al estilo del español: "the recognition of the marker", "the instructions of the procedure";
   - subordinadas encadenadas con "since", "given that", "while", "which", "whose".
4. Distribuye los conectores sin repetir el mismo en párrafos seguidos. Parte las oraciones de más de 60 palabras.
   Apunta a un largo medio cercano al de la muestra, sin superarlo en más de 5 palabras.
5. Nivel moderado: gramática correcta, sin errores de ortografía ni palabras equivocadas.

Tras cada ronda: genera una nueva versión, valídala, revísala en PDF y pide al usuario que la pase por Turnitin.
Con el nuevo informe, repite solo sobre lo que siga marcado.

## Si después piden bajar la similitud (informe de plagio)

1. Lee la lista de fuentes y las páginas resaltadas. En el caso probado (25 %), ninguna fuente pasaba del 3 % y había
   unas 95. Las dos principales eran **texto de la plantilla de la revista** compartido con otros estudiantes: textos
   de relleno de autores, "XXXX", numeración de líneas y títulos estándar. Explícale al usuario que eso no es plagio y
   pregúntale si quiere quitarlo. **No toques la plantilla sin su permiso.**
2. Reformula solo los **tramos coincidentes largos** (unas 8 palabras o más), con el mismo estilo que pasó el detector
   de IA. No cambies nombres de equipos, términos técnicos, puntos de corte, datos de tablas, referencias ni las
   declaraciones estándar (financiamiento, conflictos de interés, uso de IA).
3. Usa `--sample` también aquí. Si una frase nueva coincide con la muestra, que suele estar en el repositorio de
   Turnitin, cámbiala aunque sea genérica.
4. **Los cuadros de texto tienen altura fija.** Si reformulas el resumen de una plantilla, no lo alargues: revisa en
   el PDF que no se corte la última línea (Keywords).
5. Sugiere que quien configura Turnitin active "excluir coincidencias pequeñas" y que las versiones de prueba no se
   guarden en el repositorio. Si se guardan, la siguiente versión coincidirá con la anterior.

## Resumen de patrones de IA (si la skill humanizer no está instalada)

Quita o reformula: "not X but Y" y "X rather than Y" cuando solo agregan énfasis; cierres de una línea que repiten
lo dicho ("Taken together…", "Overall…"); introducciones antes del punto ("Several limitations should be
considered"); enumeraciones de tres por costumbre; guiones largos (—); palabras típicas de IA (crucial, pivotal,
robust, highlight, underscore, landscape, delve, additionally, valuable, enhance); "serves as" en lugar de "is";
"should not be interpreted as" repetido; párrafos finales que repiten el primero. **Excepción:** si la muestra
humana usa alguno de estos rasgos (por ejemplo, conectores al inicio), la muestra manda.

## Scripts (Python 3 con `lxml`; en Windows, Word para exportar a PDF)

```bash
# 1. Ver los párrafos (índice, sección, texto exacto) para preparar reemplazos
python -I scripts/extract_paragraphs.py documento.docx > parrafos.txt

# 2. Aplicar reemplazos desde JSON [{"old": "...", "new": "..."}] y generar la nueva versión
python -I scripts/apply_replacements.py entrada.docx cambios.json salida.docx \
    --sample muestra.txt --report comparacion.md

# 3. Comparar estilo (texto plano de la muestra contra el documento o los reemplazos)
python -I scripts/style_stats.py muestra.txt documento.docx

# 4. Exportar a PDF con Word para revisar el formato (Windows)
pwsh -File scripts/export_pdf.ps1 -Docx salida.docx -Pdf salida.pdf
```

`apply_replacements.py`:
- reemplaza el texto exacto aunque esté repartido entre varios fragmentos del XML;
- exige que cada `old` aparezca una sola vez;
- verifica que no cambien las citas, tanto numeradas `[n]` como de autor y año (APA: "Turner et al., 2025",
  "Kosovski et al. (2024)", "(Huwaikem & Bano, 2026)"), ni las cifras;
- en los cuadros de texto (por ejemplo, el resumen de una plantilla de revista), ignora la copia duplicada que Word
  guarda como respaldo (`mc:Fallback`) al buscar y **aplica el mismo cambio en las dos copias**;
- avisa de secuencias de 6 palabras compartidas con la muestra;
- escribe una comparación antes/después en Markdown.

Si un reemplazo cruza un fragmento con formato distinto (cursiva, negrita), todo el texto toma el formato del
primer fragmento. Revisa esos párrafos en el PDF.

Para obtener el texto de una muestra en `.doc` o `.pdf`: con Word, `SaveAs2` en formato 7 (texto Unicode,
codificación 65001); o `pdftotext muestra.pdf muestra.txt`.

## Qué reportar al usuario en cada ronda

Una tabla con el porcentaje de antes y de ahora, qué secciones dejaron de estar marcadas y cuáles siguen marcadas.
Agrega el resultado de las verificaciones (citas y cifras completas, sin frases copiadas de la muestra), la ruta
de la nueva versión y de la comparación, y los pendientes de contenido que debe decidir el usuario. Cuando Turnitin
muestra "*%", significa que el puntaje está por debajo del 20 %: ahí está la meta.
