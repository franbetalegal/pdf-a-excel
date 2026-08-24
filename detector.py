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
