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
