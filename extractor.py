"""Extracción de tablas de un PDF usando Camelot (modo lattice)."""

import camelot


def extraer_tablas(ruta_pdf: str) -> list[dict]:
    """Extrae todas las tablas con bordes del PDF.

    Devuelve una lista de dicts con: pagina, indice (global, desde 1),
    df (DataFrame) y precision (0-100 según Camelot).
    """
    tablas = camelot.read_pdf(ruta_pdf, pages="all", flavor="lattice")
    resultados = []
    for i, tabla in enumerate(tablas):
        resultados.append(
            {
                "pagina": int(tabla.page),
                "indice": i + 1,
                "df": tabla.df,
                "precision": round(tabla.parsing_report.get("accuracy", 0), 1),
            }
        )
    return resultados
