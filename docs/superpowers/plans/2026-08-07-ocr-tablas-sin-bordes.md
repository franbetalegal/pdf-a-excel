# OCR para PDF escaneados sin tablas marcadas — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir una segunda vía de extracción de tablas para PDF escaneados (imagen pura, sin líneas de tabla dibujadas), manteniendo el flujo actual de Camelot intacto para PDF digitales con bordes.

**Architecture:** `extractor_ocr.py` extrae tablas sin bordes de un PDF escaneado con `img2table` + Tesseract local. `detector.py` decide, por PDF, si es un escaneo (mide texto extraíble con `pypdfium2`) y elige entre ese extractor nuevo o el actual (`extractor.py`, Camelot `lattice`). Ambos devuelven la misma forma de datos (`pagina`, `indice`, `df`, `precision`) para que `app.py` y `exporter.py` no distingan el origen salvo para decidir si la tabla se muestra editable.

**Tech Stack:** Python 3.10+, Streamlit, `pypdfium2` (ya presente), `img2table` (nuevo), `pytesseract` (nuevo) + binario de Tesseract OCR (dependencia de sistema, no de pip), `pytest` (nuevo, dev).

## Global Constraints

- Todo el procesamiento debe quedarse en el ordenador local — no subir PDF de clientes a ningún servicio externo (política de la organización sobre datos de clientes). Por eso el OCR es Tesseract local, no una API en la nube.
- Los dos extractores deben devolver `list[dict]` con exactamente las claves `pagina` (int), `indice` (int, global desde 1), `df` (`pandas.DataFrame`), `precision` (`float | None`) — `exporter.py` y el resto de `app.py` no deben necesitar tocarse para consumir cualquiera de los dos.
- La rama Camelot existente no cambia de comportamiento ni de UI (sigue de solo lectura); la rejilla editable (`st.data_editor`) es solo para tablas de la rama OCR.
- Textos de interfaz en español, mismo tono que el resto de la app (ver `app.py` actual).
- Sin permisos de administrador para instalar nada del lado del usuario final (restricción ya vigente del proyecto).
- **Hallazgo de compatibilidad verificado durante este plan:** `img2table` depende de `opencv-contrib-python`, mientras que `camelot-py` depende de `opencv-python-headless`. Instalar ambos paquetes en el mismo entorno es una combinación no oficialmente soportada por el proyecto OpenCV (los dos instalan un paquete `cv2` con el mismo nombre de carpeta), pero se ha probado en un entorno limpio con `pip install camelot-py img2table pytesseract`: pip resuelve ambos a la misma versión subyacente (5.0.0.93 en la prueba), y tanto `camelot.read_pdf(..., flavor="lattice")` como `img2table` funcionan correctamente en el mismo intérprete. No se requiere ninguna acción especial en `requirements.txt` más allá de añadir `img2table` y `pytesseract`; si en el futuro alguna de las dos librerías fija una versión de opencv distinta y esto deja de funcionar, la solución es instalar `camelot-py` con `pip install --no-deps camelot-py` y declarar sus demás dependencias (`click`, `numpy`, `openpyxl`, `pandas`, `pillow`, `playa-pdf`, `pypdfium2`, `tabulate`) sueltas en `requirements.txt`.
- **Nota de empaquetado (cambia lo previsto en el diseño):** el diseño original preveía "empaquetar el binario de Tesseract, reutilizando el script/carpeta de binarios que ya resolvió esto en `markitdown`". Al revisar cómo lo hace `markitdown` realmente, ese empaquetado binario (`packaging/windows/make_exe.ps1` con `Copy-Tesseract`) solo existe en su build portátil basada en Python embebido, que no requiere ningún Python preinstalado. `pdf converter` usa una arquitectura distinta (`instalar.bat`/`instalar.command` instalan Python real en modo usuario y crean un venv), igual que la propia `markitdown` hace en sus scripts `packaging/macos/dev.sh` y `packaging/linux/run.sh`: ahí no empaquetan ningún binario, solo comprueban `command -v tesseract` y avisan si falta, sin bloquear el resto de la app. Este plan sigue ese segundo patrón (Task 5): documentar el requisito e informar en tiempo de ejecución si falta (Task 4), en vez de bundling de binarios.

---

### Task 1: Fixtures de prueba y dependencias de desarrollo

**Files:**
- Create: `requirements-dev.txt`
- Create: `tests/fixtures/generar_fixtures.py`
- Create: `tests/fixtures/digital_con_lineas.pdf` (binario, generado por el script)
- Create: `tests/fixtures/escaneado_imagen.pdf` (binario, generado por el script)

**Interfaces:**
- Produces: dos PDF de muestra en `tests/fixtures/` que usarán las Tasks 2 y 3: `digital_con_lineas.pdf` (texto seleccionable, con una tabla de 3 filas × 3 columnas con bordes dibujados) y `escaneado_imagen.pdf` (una sola página que es una imagen renderizada, sin capa de texto, con el mismo contenido en columnas alineadas por posición X: 50, 400, 700).

- [ ] **Step 1: Crear `requirements-dev.txt`**

```
pytest>=8.0
reportlab>=4.0
pillow>=10
```

- [ ] **Step 2: Crear el script generador de fixtures**

```python
# tests/fixtures/generar_fixtures.py
"""Genera los PDF de muestra usados en los tests.

Ejecutar una sola vez (o cuando cambie el contenido de prueba deseado):
    python tests/fixtures/generar_fixtures.py

Los PDF resultantes se commitean junto al código; los tests no los
regeneran en cada ejecución.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

CARPETA = Path(__file__).parent

FILAS = [
    ["Producto", "Cantidad", "Precio"],
    ["Tornillo", "10", "1.20"],
    ["Tuerca", "20", "0.50"],
]


def generar_pdf_digital() -> None:
    """PDF con texto seleccionable y una tabla con líneas dibujadas."""
    ruta = CARPETA / "digital_con_lineas.pdf"
    c = canvas.Canvas(str(ruta), pagesize=A4)
    ancho, alto = A4
    x0, y0 = 50, alto - 150
    col_x = [x0, x0 + 150, x0 + 300]
    alto_fila = 25

    for i, fila in enumerate(FILAS):
        y = y0 - i * alto_fila
        for j, celda in enumerate(fila):
            c.drawString(col_x[j] + 5, y - 17, celda)

    ancho_tabla = 450
    alto_tabla = alto_fila * len(FILAS)
    c.rect(x0, y0 - alto_tabla + alto_fila, ancho_tabla, alto_tabla)
    for i in range(1, len(FILAS)):
        y = y0 - i * alto_fila + alto_fila
        c.line(x0, y, x0 + ancho_tabla, y)
    for x in col_x[1:]:
        c.line(x, y0 - alto_tabla + alto_fila, x, y0 + alto_fila)
    c.save()
    print("generado", ruta)


def generar_pdf_escaneado() -> None:
    """PDF de una sola página que es una imagen (sin capa de texto),
    con columnas alineadas por posición X pero sin líneas de tabla."""
    ruta = CARPETA / "escaneado_imagen.pdf"
    imagen = Image.new("RGB", (1000, 400), "white")
    dibujo = ImageDraw.Draw(imagen)
    fuente = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial.ttf", 28
    )
    col_x = [50, 400, 700]
    for i, fila in enumerate(FILAS):
        y = 40 + i * 60
        for j, celda in enumerate(fila):
            dibujo.text((col_x[j], y), celda, fill="black", font=fuente)
    imagen.save(ruta, "PDF")
    print("generado", ruta)


if __name__ == "__main__":
    generar_pdf_digital()
    generar_pdf_escaneado()
```

Nota: el script usa una fuente TrueType del sistema macOS (`/System/Library/Fonts/Supplemental/Arial.ttf`) porque solo se ejecuta una vez, a mano, en la máquina de desarrollo, para generar los binarios que luego se commitean. Si se regenera en Linux o Windows, cambiar esa ruta por una fuente TrueType disponible en ese sistema.

- [ ] **Step 3: Instalar dependencias de desarrollo y generar los fixtures**

Run (con el venv del proyecto activado):
```bash
pip install -r requirements-dev.txt
python tests/fixtures/generar_fixtures.py
```
Expected: se crean `tests/fixtures/digital_con_lineas.pdf` y `tests/fixtures/escaneado_imagen.pdf`.

- [ ] **Step 4: Verificar el contenido de los fixtures**

Run:
```bash
python -c "
import pypdfium2 as pdfium
for nombre in ['tests/fixtures/digital_con_lineas.pdf', 'tests/fixtures/escaneado_imagen.pdf']:
    doc = pdfium.PdfDocument(nombre)
    total = sum(len(p.get_textpage().get_text_range().strip()) for p in doc)
    print(nombre, '->', total, 'caracteres')
    doc.close()
"
```
Expected: `digital_con_lineas.pdf` con un número de caracteres claramente mayor que 0 (bastantes decenas), `escaneado_imagen.pdf` con `0` caracteres.

- [ ] **Step 5: Commit**

```bash
git add requirements-dev.txt tests/fixtures/generar_fixtures.py tests/fixtures/digital_con_lineas.pdf tests/fixtures/escaneado_imagen.pdf
git commit -m "test: añade fixtures de PDF digital y escaneado para las pruebas de OCR"
```

---

### Task 2: Extracción de tablas sin bordes vía OCR (`img2table` + Tesseract)

**Files:**
- Create: `extractor_ocr.py`
- Test: `tests/test_extractor_ocr.py`
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: fixture `tests/fixtures/escaneado_imagen.pdf` (Task 1).
- Produces: `extraer_tablas_ocr(ruta_pdf: str) -> list[dict]`, con dicts de forma `{"pagina": int, "indice": int, "df": pandas.DataFrame, "precision": None}`. La Task 3 (`detector.elegir_extractor`) y la Task 4 (`app.py`) consumen esta función y esta forma de dict.

Nota sobre `precision`: se investigó la API pública de `img2table` (`ExtractedTable`, en `img2table.tables.extraction`) y no expone una puntuación de confianza por tabla — solo captura la confianza de Tesseract por palabra internamente, sin sacarla al resultado público. En vez de depender de atributos internos no documentados de la librería (frágil ante actualizaciones), `precision` se deja en `None` para toda tabla de origen OCR; la Task 4 usa esto como señal para no mostrar un porcentaje sin sentido y en su lugar avisar que conviene revisar la tabla a mano (la rejilla editable ya cubre esto).

- [ ] **Step 1: Añadir dependencias a `requirements.txt`**

Modificar `requirements.txt` (añadir al final):
```
img2table>=1.3
pytesseract>=0.3
```

Run:
```bash
pip install -r requirements.txt
```
Expected: instala `img2table`, `pytesseract` y sus dependencias (incluye `opencv-contrib-python`; ver la nota de compatibilidad en "Global Constraints" — no requiere ninguna acción manual).

- [ ] **Step 2: Escribir el test que falla**

```python
# tests/test_extractor_ocr.py
from pathlib import Path

from extractor_ocr import extraer_tablas_ocr

FIXTURES = Path(__file__).parent / "fixtures"


def test_extrae_tabla_de_pdf_escaneado():
    resultados = extraer_tablas_ocr(str(FIXTURES / "escaneado_imagen.pdf"))

    assert len(resultados) == 1
    tabla = resultados[0]
    assert tabla["pagina"] == 1
    assert tabla["indice"] == 1
    assert tabla["precision"] is None
    # 3 filas (cabecera + 2 datos) x 3 columnas. No se afirma el texto
    # exacto porque el propio OCR es lo que se está probando aquí, no
    # la limpieza de sus errores.
    assert tabla["df"].shape == (3, 3)
```

- [ ] **Step 3: Ejecutar el test y comprobar que falla**

Run: `pytest tests/test_extractor_ocr.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'extractor_ocr'`.

- [ ] **Step 4: Implementación**

```python
# extractor_ocr.py
"""Extracción de tablas sin bordes de un PDF escaneado, vía OCR local.

Usa img2table (detección de tabla por análisis de espacios en blanco,
sin depender de líneas dibujadas) con Tesseract como motor de OCR local
— nada se envía a ningún servicio externo.
"""

from img2table.document import PDF
from img2table.ocr import TesseractOCR


def extraer_tablas_ocr(ruta_pdf: str) -> list[dict]:
    """Extrae todas las tablas sin bordes de un PDF escaneado.

    Devuelve una lista de dicts con: pagina, indice (global, desde 1),
    df (DataFrame) y precision (siempre None: img2table no expone una
    puntuación de confianza por tabla en su API pública — la revisión
    manual en la interfaz cubre esa falta de certeza).
    """
    ocr = TesseractOCR(lang="spa+eng")
    documento = PDF(ruta_pdf)
    tablas_por_pagina = documento.extract_tables(
        ocr=ocr,
        implicit_rows=True,
        implicit_columns=True,
        borderless_tables=True,
    )

    resultados = []
    indice = 1
    for pagina_idx in sorted(tablas_por_pagina):
        for tabla in tablas_por_pagina[pagina_idx]:
            resultados.append(
                {
                    "pagina": pagina_idx + 1,
                    "indice": indice,
                    "df": tabla.df,
                    "precision": None,
                }
            )
            indice += 1
    return resultados
```

- [ ] **Step 5: Ejecutar el test y comprobar que pasa**

Run: `pytest tests/test_extractor_ocr.py -v`
Expected: PASS. Requiere que Tesseract esté instalado en la máquina donde se ejecuta el test (`tesseract --version` debe funcionar en la terminal); si no lo está, instalarlo primero (macOS: `brew install tesseract tesseract-lang`).

- [ ] **Step 6: Commit**

```bash
git add extractor_ocr.py tests/test_extractor_ocr.py requirements.txt
git commit -m "feat: extrae tablas sin bordes de PDF escaneados con OCR local (img2table + Tesseract)"
```

---

### Task 3: Detección de PDF escaneado y selección de extractor

**Files:**
- Create: `detector.py`
- Test: `tests/test_detector.py`

**Interfaces:**
- Consumes: fixtures de la Task 1 (`tests/fixtures/digital_con_lineas.pdf`, `tests/fixtures/escaneado_imagen.pdf`); `extraer_tablas` de `extractor.py` (ya existía antes de este plan); `extraer_tablas_ocr` de `extractor_ocr.py` (Task 2).
- Produces: `es_escaneado(ruta_pdf: str) -> bool`; `elegir_extractor(ruta_pdf: str) -> Callable[[str], list[dict]]`. La Task 4 (integración en `app.py`) consume `elegir_extractor`.

- [ ] **Step 1: Escribir los tests que fallan**

```python
# tests/test_detector.py
from pathlib import Path

from detector import elegir_extractor, es_escaneado
from extractor import extraer_tablas
from extractor_ocr import extraer_tablas_ocr

FIXTURES = Path(__file__).parent / "fixtures"


def test_pdf_digital_no_se_detecta_como_escaneado():
    assert es_escaneado(str(FIXTURES / "digital_con_lineas.pdf")) is False


def test_pdf_imagen_se_detecta_como_escaneado():
    assert es_escaneado(str(FIXTURES / "escaneado_imagen.pdf")) is True


def test_elige_extractor_ocr_para_pdf_escaneado():
    extractor = elegir_extractor(str(FIXTURES / "escaneado_imagen.pdf"))
    assert extractor is extraer_tablas_ocr


def test_elige_extractor_camelot_para_pdf_digital():
    extractor = elegir_extractor(str(FIXTURES / "digital_con_lineas.pdf"))
    assert extractor is extraer_tablas
```

- [ ] **Step 2: Ejecutar los tests y comprobar que fallan**

Run: `pytest tests/test_detector.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'detector'`.

- [ ] **Step 3: Implementación**

```python
# detector.py
"""Decide si un PDF es un escaneo (imagen sin texto) y qué extractor usar."""

from typing import Callable

import pypdfium2 as pdfium

from extractor import extraer_tablas
from extractor_ocr import extraer_tablas_ocr

UMBRAL_CARACTERES_POR_PAGINA = 20


def es_escaneado(ruta_pdf: str) -> bool:
    """True si el PDF no tiene suficiente texto extraíble (probable escaneo).

    Se mide la media de caracteres de texto extraíble por página con
    pypdfium2; un PDF de imagen pura (sin capa de texto OCR) da 0.
    """
    documento = pdfium.PdfDocument(ruta_pdf)
    try:
        total_caracteres = sum(
            len(pagina.get_textpage().get_text_range().strip())
            for pagina in documento
        )
        return (total_caracteres / len(documento)) < UMBRAL_CARACTERES_POR_PAGINA
    finally:
        documento.close()


def elegir_extractor(ruta_pdf: str) -> Callable[[str], list[dict]]:
    """Devuelve la función de extracción adecuada para este PDF."""
    return extraer_tablas_ocr if es_escaneado(ruta_pdf) else extraer_tablas
```

- [ ] **Step 4: Ejecutar los tests y comprobar que pasan**

Run: `pytest tests/test_detector.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add detector.py tests/test_detector.py
git commit -m "feat: detecta PDF escaneados y elige el extractor adecuado"
```

---

### Task 4: Integración en la interfaz (`app.py`)

**Files:**
- Modify: `app.py:17-23` (imports)
- Modify: `app.py:103-118` (`procesar_pdf`)
- Modify: `app.py:121-135` (`mostrar_error_de_analisis`)
- Modify: `app.py:147-150` (texto introductorio)
- Modify: `app.py:164-197` (bucle de archivos y tablas)

**Interfaces:**
- Consumes: `elegir_extractor` (`detector.py`, Task 3); `extraer_tablas_ocr` (`extractor_ocr.py`, Task 2, solo para comparar identidad de función).
- Produces: ningún nuevo símbolo público — este es el punto donde todo se conecta a la interfaz Streamlit.

No hay tests automatizados para este paso (es interfaz Streamlit interactiva); se verifica a mano al final con la app corriendo.

- [ ] **Step 1: Actualizar los imports**

En `app.py`, sustituir:
```python
from exporter import (
    MODO_HOJA_POR_TABLA,
    MODO_HOJA_UNICA,
    generar_excel,
    generar_excel_combinado,
)
from extractor import extraer_tablas
```
por:
```python
from detector import elegir_extractor
from exporter import (
    MODO_HOJA_POR_TABLA,
    MODO_HOJA_UNICA,
    generar_excel,
    generar_excel_combinado,
)
from extractor_ocr import extraer_tablas_ocr
```

- [ ] **Step 2: Cambiar `procesar_pdf` para que también informe el origen**

Sustituir:
```python
@st.cache_data(show_spinner=False)
def procesar_pdf(contenido: bytes) -> list[dict]:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(contenido)
        ruta = f.name
    try:
        return extraer_tablas(ruta)
    finally:
        # En Windows la librería de PDF puede mantener el archivo abierto;
        # liberamos sus objetos y, si sigue bloqueado, lo dejamos en la
        # carpeta temporal en vez de fallar.
        gc.collect()
        try:
            os.unlink(ruta)
        except OSError:
            pass
```
por:
```python
@st.cache_data(show_spinner=False)
def procesar_pdf(contenido: bytes) -> tuple[bool, list[dict]]:
    """Devuelve (es_ocr, tablas): es_ocr indica si se usó la rama OCR
    (PDF escaneado) en vez de Camelot."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(contenido)
        ruta = f.name
    try:
        extraer = elegir_extractor(ruta)
        return extraer is extraer_tablas_ocr, extraer(ruta)
    finally:
        # En Windows la librería de PDF puede mantener el archivo abierto;
        # liberamos sus objetos y, si sigue bloqueado, lo dejamos en la
        # carpeta temporal en vez de fallar.
        gc.collect()
        try:
            os.unlink(ruta)
        except OSError:
            pass
```

- [ ] **Step 3: Mensaje de error específico para Tesseract ausente**

Sustituir:
```python
def mostrar_error_de_analisis(exc: Exception) -> None:
    if isinstance(exc, ImportError) or "DLL" in str(exc):
        st.error(
            "Falta un componente del sistema necesario para analizar "
            "PDFs (Microsoft Visual C++ Redistributable). Consulta la "
            "sección «Problemas comunes» del README."
        )
    else:
        st.error(
            "Ocurrió un error al procesar este PDF. Si el archivo se abre "
            "bien en otros programas, copia los detalles técnicos de "
            "abajo y envíalos al responsable de la aplicación."
        )
    with st.expander("Detalles técnicos del error"):
        st.code("".join(traceback.format_exception(exc)))
```
por:
```python
def mostrar_error_de_analisis(exc: Exception) -> None:
    mensaje = str(exc)
    if "Tesseract not found" in mensaje or "trainned data cannot be located" in mensaje:
        st.error(
            "Este PDF parece un escaneo y hace falta Tesseract OCR para "
            "leerlo, pero no está instalado en este ordenador. Consulta "
            "la sección «Problemas comunes» del README para instalarlo."
        )
    elif isinstance(exc, ImportError) or "DLL" in mensaje:
        st.error(
            "Falta un componente del sistema necesario para analizar "
            "PDFs (Microsoft Visual C++ Redistributable). Consulta la "
            "sección «Problemas comunes» del README."
        )
    else:
        st.error(
            "Ocurrió un error al procesar este PDF. Si el archivo se abre "
            "bien en otros programas, copia los detalles técnicos de "
            "abajo y envíalos al responsable de la aplicación."
        )
    with st.expander("Detalles técnicos del error"):
        st.code("".join(traceback.format_exception(exc)))
```

- [ ] **Step 4: Actualizar el texto introductorio**

Sustituir:
```python
st.markdown(
    "Sube uno o varios PDF con tablas **con bordes visibles**, revisa las "
    "tablas detectadas y descarga el resultado en Excel."
)
```
por:
```python
st.markdown(
    "Sube uno o varios PDF —con tablas de bordes visibles o PDF "
    "escaneados sin bordes—, revisa las tablas detectadas (y corrígelas "
    "si vienen de un escaneo) y descarga el resultado en Excel."
)
```

- [ ] **Step 5: Actualizar el bucle de archivos y tablas**

Sustituir el cuerpo del bucle `for num_archivo, archivo in enumerate(archivos):` (desde el `try:` de `procesar_pdf` hasta el `if seleccionadas:` final de esa iteración) por:

```python
    for num_archivo, archivo in enumerate(archivos):
        st.markdown(f"#### 📕 {archivo.name}")
        try:
            with st.spinner(f"Analizando {archivo.name}…"):
                es_ocr, tablas = procesar_pdf(archivo.getvalue())
        except Exception as exc:
            mostrar_error_de_analisis(exc)
            continue

        if es_ocr:
            st.info(
                "📷 PDF escaneado detectado: usando reconocimiento de "
                "texto (OCR) local. Revisa y corrige las tablas antes "
                "de exportar."
            )

        if not tablas:
            if es_ocr:
                st.warning(
                    "No se ha detectado ninguna tabla en este PDF "
                    "escaneado. Puede deberse a la calidad del escaneo "
                    "(inclinación, baja resolución) o a que los datos no "
                    "guardan columnas alineadas."
                )
            else:
                st.warning(
                    "No se ha detectado ninguna tabla en este PDF. Este "
                    "convertidor busca tablas con bordes/líneas visibles; "
                    "si el PDF tiene datos alineados sin rejilla, no podrá "
                    "detectarlos."
                )
            continue

        st.caption(f"{len(tablas)} tabla(s) detectada(s).")
        seleccionadas = []
        for t in tablas:
            if t["precision"] is None:
                etiqueta = (
                    f"Tabla {t['indice']} — página {t['pagina']} "
                    "(OCR, revisa antes de exportar)"
                )
            else:
                etiqueta = (
                    f"Tabla {t['indice']} — página {t['pagina']} "
                    f"(precisión {t['precision']}%)"
                )
            with st.expander(etiqueta, expanded=len(tablas) <= 3):
                incluir = st.checkbox(
                    "Incluir esta tabla en el Excel",
                    value=True,
                    key=f"incluir_{num_archivo}_{t['indice']}",
                )
                if es_ocr:
                    df_editado = st.data_editor(
                        t["df"],
                        width="stretch",
                        key=f"editor_{num_archivo}_{t['indice']}",
                    )
                    t = {**t, "df": df_editado}
                else:
                    st.dataframe(t["df"], width="stretch")
            if incluir:
                seleccionadas.append(t)

        if seleccionadas:
            seleccion_por_archivo.append((archivo.name, seleccionadas))
```

- [ ] **Step 6: Verificación manual**

Run:
```bash
streamlit run app.py
```
En el navegador:
1. Sube `tests/fixtures/digital_con_lineas.pdf`. Expected: comportamiento igual que antes de este plan — tabla de solo lectura, sin aviso de OCR.
2. Sube `tests/fixtures/escaneado_imagen.pdf`. Expected: aparece el aviso "📷 PDF escaneado detectado…", la tabla se muestra en una rejilla editable con las 3 filas × 3 columnas, la etiqueta dice "(OCR, revisa antes de exportar)".
3. Edita una celda en la rejilla (por ejemplo, corrige un valor mal leído) y descarga el Excel. Expected: el `.xlsx` descargado refleja el valor corregido, no el original del OCR.

- [ ] **Step 7: Commit**

```bash
git add app.py
git commit -m "feat: integra la extracción OCR en la interfaz, con rejilla editable y avisos"
```

---

### Task 5: Documentación (README)

**Files:**
- Modify: `README.md`

**Interfaces:**
- Ninguna — solo documentación.

- [ ] **Step 1: Añadir el requisito de Tesseract**

Añadir una sección nueva al `README.md` (por ejemplo, después de "Requisitos"), con este contenido:

```markdown
## PDF escaneados (sin bordes de tabla)

Además de tablas con bordes visibles, la aplicación puede leer PDF
escaneados (imagen, sin texto seleccionable) cuyas tablas no tienen
líneas dibujadas pero sí columnas alineadas. Para esto usa OCR local
(Tesseract) — el documento no sale de tu ordenador en ningún momento.

Como el OCR no es infalible (letra borrosa, sellos, escaneo torcido),
la app muestra la tabla detectada en una rejilla editable para corregirla
antes de exportar a Excel.

**Requiere tener Tesseract OCR instalado:**

- **Windows:** instalar desde [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) (incluye datos de idioma español si se marca esa opción durante la instalación).
- **macOS:** `brew install tesseract tesseract-lang`
- **Linux:** `sudo apt install tesseract-ocr tesseract-ocr-spa`

Si Tesseract no está instalado, la app sigue funcionando con normalidad
para PDF con tablas de bordes visibles; solo al subir un PDF escaneado
avisará de que falta instalarlo.
```

- [ ] **Step 2: Actualizar la frase de la sección "Instalación" si menciona solo "tablas con bordes"**

Revisar el `README.md` actual y, si la primera línea o la descripción general dice algo como "extrae tablas de PDFs (tablas con bordes visibles)", actualizarla a algo como "extrae tablas de PDFs, tanto con bordes visibles como escaneadas sin bordes (vía OCR local)".

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: documenta el soporte de OCR para PDF escaneados y el requisito de Tesseract"
```
