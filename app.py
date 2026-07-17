"""Convertidor de PDF a Excel — interfaz web con Streamlit."""

import gc
import os
import subprocess
import sys
import tempfile
import time
import traceback
import zipfile
from io import BytesIO
from pathlib import Path

import requests
import streamlit as st

from exporter import (
    MODO_HOJA_POR_TABLA,
    MODO_HOJA_UNICA,
    generar_excel,
    generar_excel_combinado,
)
from extractor import extraer_tablas

st.set_page_config(page_title="PDF a Excel", page_icon="📄", layout="wide")

CARPETA_APP = Path(__file__).parent
URL_VERSION_REMOTA = (
    "https://raw.githubusercontent.com/franbetalegal/pdf-a-excel/main/VERSION"
)


def version_local() -> str | None:
    try:
        return (CARPETA_APP / "VERSION").read_text().strip()
    except OSError:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def version_remota() -> str | None:
    """Consulta la última versión publicada en GitHub. None si no hay red."""
    try:
        respuesta = requests.get(URL_VERSION_REMOTA, timeout=3)
        if respuesta.ok:
            return respuesta.text.strip()
    except Exception:
        pass
    return None


def avisar_si_hay_actualizacion() -> None:
    remota = version_remota()
    local = version_local()
    if not remota or remota == local:
        return
    st.warning(
        f"🔔 Hay una versión nueva disponible (**{remota}**; "
        f"esta es la {local or 'sin numerar'})."
    )
    if sys.platform == "win32":
        if st.button("🔄 Actualizar y reiniciar"):
            # La actualización se aplica fuera de la app (actualizar.bat)
            # con la app cerrada; el .bat vuelve a lanzar iniciar.bat.
            subprocess.Popen(
                ["cmd", "/c", "start", "", "actualizar.bat", "/reiniciar"],
                cwd=CARPETA_APP,
            )
            st.info(
                "Actualizando… esta ventana se quedará sin conexión unos "
                "segundos y la aplicación volverá a abrirse sola."
            )
            time.sleep(2)
            os._exit(0)
    else:
        st.caption(
            "Para actualizar: cierra la aplicación y descarga la última "
            "versión del repositorio."
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


st.title("📄 Convertidor de PDF a Excel")
st.markdown(
    "Sube uno o varios PDF con tablas **con bordes visibles**, revisa las "
    "tablas detectadas y descarga el resultado en Excel."
)

avisar_si_hay_actualizacion()

archivos = st.file_uploader(
    "Sube tus PDF", type="pdf", accept_multiple_files=True
)

if archivos:
    st.subheader("1. Revisa y elige qué tablas incluir")

    # (nombre_pdf, tablas seleccionadas) por cada archivo analizado con éxito
    seleccion_por_archivo: list[tuple[str, list[dict]]] = []

    for num_archivo, archivo in enumerate(archivos):
        st.markdown(f"#### 📕 {archivo.name}")
        try:
            with st.spinner(f"Analizando {archivo.name}…"):
                tablas = procesar_pdf(archivo.getvalue())
        except Exception as exc:
            mostrar_error_de_analisis(exc)
            continue

        if not tablas:
            st.warning(
                "No se ha detectado ninguna tabla en este PDF. Este "
                "convertidor busca tablas con bordes/líneas visibles; si "
                "el PDF tiene datos alineados sin rejilla, no podrá "
                "detectarlos."
            )
            continue

        st.caption(f"{len(tablas)} tabla(s) detectada(s).")
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
                    key=f"incluir_{num_archivo}_{t['indice']}",
                )
                st.dataframe(t["df"], width="stretch")
            if incluir:
                seleccionadas.append(t)

        if seleccionadas:
            seleccion_por_archivo.append((archivo.name, seleccionadas))

    if not seleccion_por_archivo:
        st.info("Selecciona al menos una tabla para generar el Excel.")
        st.stop()

    st.subheader("2. Elige cómo organizar cada Excel")
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

    combinar = False
    if len(seleccion_por_archivo) > 1:
        agrupacion = st.radio(
            "¿Cómo agrupar los resultados?",
            options=[
                f"Un Excel por PDF ({len(seleccion_por_archivo)} archivos)",
                "Un único Excel con todo",
            ],
            horizontal=True,
        )
        combinar = agrupacion == "Un único Excel con todo"

    st.subheader("3. Descarga")
    MIME_XLSX = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if combinar:
        datos = generar_excel_combinado(seleccion_por_archivo, modo)
        st.download_button(
            label="⬇️ Descargar tablas_convertidas.xlsx",
            data=datos,
            file_name="tablas_convertidas.xlsx",
            mime=MIME_XLSX,
            type="primary",
            key="descargar_combinado",
        )
    else:
        excels: list[tuple[str, bytes]] = []
        for nombre_pdf, tablas in seleccion_por_archivo:
            nombre_salida = os.path.splitext(nombre_pdf)[0] + ".xlsx"
            excels.append(
                (nombre_salida, generar_excel(tablas, modo).getvalue())
            )

        for i, (nombre_salida, datos) in enumerate(excels):
            st.download_button(
                label=f"⬇️ Descargar {nombre_salida}",
                data=datos,
                file_name=nombre_salida,
                mime=MIME_XLSX,
                type="primary" if len(excels) == 1 else "secondary",
                key=f"descargar_{i}",
            )

        if len(excels) > 1:
            buffer_zip = BytesIO()
            with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                for nombre_salida, datos in excels:
                    zf.writestr(nombre_salida, datos)
            buffer_zip.seek(0)
            st.download_button(
                label=f"📦 Descargar los {len(excels)} Excel en un ZIP",
                data=buffer_zip,
                file_name="tablas_convertidas.zip",
                mime="application/zip",
                type="primary",
                key="descargar_zip",
            )
