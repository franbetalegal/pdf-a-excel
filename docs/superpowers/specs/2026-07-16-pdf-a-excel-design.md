# Convertidor de PDF a Excel — Diseño

**Fecha:** 2026-07-16

## Objetivo

Herramienta local con interfaz web para extraer tablas de PDFs (tablas con bordes/líneas) y exportarlas a Excel. Uso personal, ejecutada en localhost, pensada para instalarse fácilmente en varios ordenadores sin permisos de administrador.

## Stack

- **Streamlit** — interfaz web (subida, previsualización, descarga) en un solo proceso Python.
- **camelot-py 1.x** con backend `pdfium` — extracción de tablas en modo `lattice` (tablas con bordes). Sin Ghostscript ni dependencias de sistema: todo se instala vía pip.
- **pandas + openpyxl** — construcción del archivo `.xlsx` en memoria.

## Componentes

- `app.py` — capa de presentación Streamlit:
  1. Subida del PDF.
  2. Previsualización de cada tabla detectada, con número de página, puntuación de precisión de Camelot y casilla para incluir/excluir.
  3. Selector de modo de organización: *una hoja por tabla* o *todo en una hoja* (concatenadas con fila separadora indicando la página de origen).
  4. Botón de descarga del Excel.
- `extractor.py` — envuelve Camelot: `read_pdf(ruta, pages="all", flavor="lattice")`; devuelve lista de tablas (página, DataFrame, precisión).
- `exporter.py` — recibe tablas seleccionadas + modo y genera el `.xlsx` en memoria (`BytesIO`). Hojas nombradas `Pag{N}_Tabla{i}` (máx. 31 caracteres).

## Instalación y distribución

- `requirements.txt` con versiones fijadas.
- `instalar.bat` (Windows): si el ordenador no tiene Python, lo descarga de python.org y lo instala en modo por-usuario (`InstallAllUsers=0`, sin admin); después crea un venv local dentro de la carpeta e instala dependencias. Pensado para ordenadores recién instalados con usuarios sin permisos de administrador.
- `instalar.command` (macOS): igual pero requiere Python 3 preinstalado.
- `iniciar.command` / `iniciar.bat`: lanza `streamlit run app.py`.
- Instalar en otro ordenador = copiar la carpeta + ejecutar el script de instalación.

## Manejo de errores

- PDF cifrado, corrupto o ilegible → mensaje de error claro en la interfaz, sin traza técnica.
- PDF sin tablas detectadas → aviso explicando que el modo `lattice` requiere tablas con bordes visibles.
- Resultados de extracción cacheados por contenido del archivo (`st.cache_data`) para no reprocesar en cada interacción.

## Fuera de alcance

- Multiusuario, autenticación, despliegue en internet.
- Modo `stream` de Camelot (tablas sin bordes).
- Edición manual de celdas en la previsualización.
