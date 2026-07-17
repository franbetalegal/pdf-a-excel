"""Generación del archivo Excel a partir de las tablas extraídas."""

import os
import re
from io import BytesIO

import pandas as pd

MODO_HOJA_POR_TABLA = "hojas"
MODO_HOJA_UNICA = "unica"


def generar_excel(tablas: list[dict], modo: str) -> BytesIO:
    """Construye el .xlsx en memoria.

    - MODO_HOJA_POR_TABLA: cada tabla en su propia hoja "Pag{N}_Tabla{i}".
    - MODO_HOJA_UNICA: todas en la hoja "Tablas", concatenadas con una fila
      separadora que indica página y número de tabla.
    """
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        if modo == MODO_HOJA_POR_TABLA:
            for t in tablas:
                nombre = f"Pag{t['pagina']}_Tabla{t['indice']}"[:31]
                t["df"].to_excel(
                    writer, sheet_name=nombre, index=False, header=False
                )
        else:
            fila = 0
            for t in tablas:
                separador = pd.DataFrame(
                    [[f"— Página {t['pagina']}, Tabla {t['indice']} —"]]
                )
                separador.to_excel(
                    writer,
                    sheet_name="Tablas",
                    startrow=fila,
                    index=False,
                    header=False,
                )
                fila += 1
                t["df"].to_excel(
                    writer,
                    sheet_name="Tablas",
                    startrow=fila,
                    index=False,
                    header=False,
                )
                fila += len(t["df"]) + 1
    buffer.seek(0)
    return buffer


def _limpiar_nombre_hoja(nombre: str) -> str:
    """Excel prohíbe []:*?/\\ en los nombres de hoja."""
    return re.sub(r"[\[\]:*?/\\]", "_", nombre).strip() or "PDF"


def generar_excel_combinado(
    seleccion_por_archivo: list[tuple[str, list[dict]]], modo: str
) -> BytesIO:
    """Construye un único .xlsx con las tablas de varios PDFs.

    - MODO_HOJA_POR_TABLA: hoja "NombrePDF_P{pag}_T{i}" por tabla (máx. 31
      caracteres, con desambiguación si dos nombres coinciden).
    - MODO_HOJA_UNICA: todo en la hoja "Tablas", cada tabla precedida de una
      fila separadora con archivo, página y número de tabla.
    """
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        if modo == MODO_HOJA_POR_TABLA:
            usados: set[str] = set()
            for nombre_pdf, tablas in seleccion_por_archivo:
                base = _limpiar_nombre_hoja(os.path.splitext(nombre_pdf)[0])
                for t in tablas:
                    sufijo = f"_P{t['pagina']}_T{t['indice']}"
                    hoja = base[: 31 - len(sufijo)] + sufijo
                    n = 2
                    while hoja in usados:
                        extra = f"~{n}"
                        hoja = (
                            base[: 31 - len(sufijo) - len(extra)]
                            + sufijo
                            + extra
                        )
                        n += 1
                    usados.add(hoja)
                    t["df"].to_excel(
                        writer, sheet_name=hoja, index=False, header=False
                    )
        else:
            fila = 0
            for nombre_pdf, tablas in seleccion_por_archivo:
                for t in tablas:
                    separador = pd.DataFrame(
                        [[
                            f"— {nombre_pdf} · Página {t['pagina']}, "
                            f"Tabla {t['indice']} —"
                        ]]
                    )
                    separador.to_excel(
                        writer,
                        sheet_name="Tablas",
                        startrow=fila,
                        index=False,
                        header=False,
                    )
                    fila += 1
                    t["df"].to_excel(
                        writer,
                        sheet_name="Tablas",
                        startrow=fila,
                        index=False,
                        header=False,
                    )
                    fila += len(t["df"]) + 1
    buffer.seek(0)
    return buffer
