"""Generación del archivo Excel a partir de las tablas extraídas."""

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
