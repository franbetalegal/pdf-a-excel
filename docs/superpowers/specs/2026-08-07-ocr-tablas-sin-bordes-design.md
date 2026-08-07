# PDF escaneados sin tablas marcadas — OCR local — Diseño

**Fecha:** 2026-08-07

## Objetivo

Los PDF que envían clientes a veces son escaneos (imagen pura, sin capa de texto) con tablas sin líneas dibujadas, con columnas alineadas visualmente. El flujo actual (Camelot `lattice`) no detecta nada en estos casos. Se añade una rama de extracción por OCR, en paralelo al flujo existente, manteniendo procesamiento 100% local (sin subir documentos de clientes a servicios externos).

## Alcance

- Detección automática de PDF escaneado vs. digital con tablas de bordes.
- Extracción de tablas sin bordes vía OCR local + análisis de espacios en blanco.
- Revisión y corrección manual de la tabla detectada antes de exportar (el OCR nunca es 100% fiable).
- Reutiliza el exportador a Excel existente sin cambios.

**Fuera de alcance (v1):**

- Corrección automática de inclinación/rotación del escaneo (deskew). Si en pruebas con PDF reales resulta ser un problema frecuente, se añade después.
- Modelos de deep learning para reconocimiento de estructura de tabla (Table Transformer, PP-Structure). Se valora solo si `img2table` no da precisión suficiente en la práctica.
- Aplicar rejilla editable a las tablas de la rama Camelot (siguen de solo lectura, como hoy).

## Stack añadido

- **img2table** — detección de tablas sin bordes por análisis de espacios en blanco en la imagen de la página; delega el OCR a un backend.
- **pytesseract + Tesseract OCR** (binario de sistema) — motor de OCR local, mismo motor que ya usa el proyecto `markitdown` para su instalador portátil sin permisos de administrador. Se reutiliza ese empaquetado de binarios en vez de rehacerlo.
- **pytest** (dev) — primeras pruebas automatizadas del proyecto, en `requirements-dev.txt` nuevo (mismo patrón que `Anonimizador`/`markitdown`).

## Componentes

- `detector.py` (nuevo) — `es_escaneado(ruta_pdf) -> bool`. Recorre páginas con `pypdfium2` (ya dependencia), mide caracteres de texto extraíble por página; si la media está por debajo de un umbral configurable, el PDF se considera escaneado.
- `extractor_ocr.py` (nuevo) — `extraer_tablas_ocr(ruta_pdf) -> list[dict]`. Usa `img2table.document.PDF` + `img2table.ocr.TesseractOCR`. Devuelve el mismo formato que `extraer_tablas` actual: `pagina`, `indice`, `df`, `precision` (aquí `precision` es la confianza media de Tesseract, 0-100, no el `parsing_report` de Camelot).
- `extractor.py` (existente) — sin cambios internos.
- `app.py` — añade:
  - Llamada a `es_escaneado()` tras subir cada PDF para decidir qué extractor usar.
  - Aviso visible ("PDF escaneado detectado, usando OCR") cuando aplica la rama nueva.
  - `st.data_editor` (rejilla editable) en vez de `st.dataframe` (solo lectura) para las tablas de la rama OCR; el DataFrame editado por el usuario se recoge de `st.session_state` antes de añadirlo a `seleccionadas`.
- `exporter.py` — sin cambios; recibe siempre el DataFrame ya definitivo (editado o no), sin distinguir su origen.

## Flujo de datos

PDF subido → `es_escaneado()` decide rama → Camelot `lattice` (igual que hoy) o `img2table` + Tesseract (nueva) → ambas ramas devuelven `list[dict]` con la misma forma → UI muestra las tablas (solo lectura si Camelot, editable si OCR) → usuario marca cuáles incluir y corrige celdas si aplica → DataFrame final pasa a `exporter.py` sin distinción de origen → Excel.

## Manejo de errores

- Tesseract no instalado o no encontrado en el `PATH`: mensaje claro en la interfaz señalando la sección correspondiente del README (mismo patrón que el aviso actual de DLL de Visual C++ faltante), no traza técnica cruda.
- `img2table` no detecta ninguna tabla en un PDF marcado como escaneado: aviso específico (distinto del aviso actual de "sin bordes visibles") que sugiere calidad de escaneo o inclinación como causa probable.
- Resultado de la detección OCR se cachea igual que hoy (`st.cache_data` sobre el contenido del archivo), para no repetir el OCR en cada interacción de la interfaz.

## Instalación y distribución

- `requirements.txt`: añade `img2table` y `pytesseract`.
- El binario de Tesseract (no es paquete Python) se empaqueta aparte para los instaladores portátiles Windows/macOS sin admin, reutilizando el script/carpeta de binarios que ya resolvió esto en `markitdown`.

## Testing

Primeras pruebas automatizadas del proyecto (hoy no existe ninguna). `requirements-dev.txt` nuevo con `pytest`.

- `es_escaneado`: 2 PDF de muestra pequeños como fixtures (uno digital con tabla de líneas, uno escaneado imagen pura) → aserción de que el resultado booleano es el esperado en cada caso.
- `extraer_tablas_ocr`: 1 PDF escaneado de muestra con una tabla simple de columnas alineadas → verifica la forma del resultado (claves presentes, `df` es DataFrame, al menos 1 fila). No se testea exactitud del contenido OCR — es frágil y depende de la calidad real del escaneo; esa parte queda cubierta por la revisión manual en la interfaz.
