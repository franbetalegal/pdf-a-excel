"""Convertidor de PDF a Excel — interfaz web con Streamlit."""

import gc
import os
import tempfile
import traceback

import streamlit as st

from exporter import MODO_HOJA_POR_TABLA, MODO_HOJA_UNICA, generar_excel
from extractor import extraer_tablas

st.set_page_config(page_title="PDF a Excel", page_icon="📄", layout="wide")

st.title("📄 Convertidor de PDF a Excel")
st.markdown(
    "Sube un PDF con tablas **con bordes visibles**, revisa las tablas "
    "detectadas y descarga el resultado en Excel."
)


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


archivo = st.file_uploader("Sube tu PDF", type="pdf")

if archivo is not None:
    try:
        with st.spinner("Analizando el PDF y buscando tablas…"):
            tablas = procesar_pdf(archivo.getvalue())
    except Exception as exc:
        if isinstance(exc, ImportError) or "DLL" in str(exc):
            st.error(
                "Falta un componente del sistema necesario para analizar "
                "PDFs (Microsoft Visual C++ Redistributable). Consulta la "
                "sección «Problemas comunes» del README."
            )
        else:
            st.error(
                "Ocurrió un error al procesar el PDF. Si el archivo se abre "
                "bien en otros programas, copia los detalles técnicos de "
                "abajo y envíalos al responsable de la aplicación."
            )
        with st.expander("Detalles técnicos del error"):
            st.code(traceback.format_exc())
        st.stop()

    if not tablas:
        st.warning(
            "No se ha detectado ninguna tabla. Este convertidor busca tablas "
            "con bordes/líneas visibles; si tu PDF tiene datos alineados sin "
            "rejilla, no podrá detectarlos."
        )
        st.stop()

    st.success(f"Se han detectado **{len(tablas)}** tabla(s).")

    st.subheader("1. Revisa y elige qué tablas incluir")
    seleccionadas = []
    for t in tablas:
        etiqueta = (
            f"Tabla {t['indice']} — página {t['pagina']} "
            f"(precisión {t['precision']}%)"
        )
        with st.expander(etiqueta, expanded=len(tablas) <= 3):
            incluir = st.checkbox(
                "Incluir esta tabla en el Excel",
                value=True,
                key=f"incluir_{t['indice']}",
            )
            st.dataframe(t["df"], width="stretch")
        if incluir:
            seleccionadas.append(t)

    st.subheader("2. Elige cómo organizar el Excel")
    modo_texto = st.radio(
        "Organización de las tablas",
        options=["Una hoja por tabla", "Todas en una sola hoja"],
        horizontal=True,
    )
    modo = (
        MODO_HOJA_POR_TABLA
        if modo_texto == "Una hoja por tabla"
        else MODO_HOJA_UNICA
    )

    st.subheader("3. Descarga")
    if not seleccionadas:
        st.info("Selecciona al menos una tabla para generar el Excel.")
    else:
        excel = generar_excel(seleccionadas, modo)
        nombre_salida = os.path.splitext(archivo.name)[0] + ".xlsx"
        st.download_button(
            label=f"⬇️ Descargar {nombre_salida}",
            data=excel,
            file_name=nombre_salida,
            mime="application/vnd.openxmlformats-officedocument"
            ".spreadsheetml.sheet",
            type="primary",
        )
