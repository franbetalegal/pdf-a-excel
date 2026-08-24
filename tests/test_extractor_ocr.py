from pathlib import Path

from img2table.ocr._types import OCRData
from img2table.ocr.tesseract import TesseractOCR

from extractor_ocr import TesseractOCRSinNulos, extraer_tablas_ocr

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


def test_ocr_sin_nulos_reemplaza_palabras_de_valor_none(monkeypatch):
    """Regresión: TesseractOCR pone `value: None` en palabras de texto
    ruidoso/vacío (frecuente en escaneos reales) y img2table no las filtra
    antes de un `str.join`, lo que hacía fallar con
    `TypeError: sequence item N: expected str instance, NoneType found`
    (visto al subir un PDF real vía la app, no reproducido con el fixture
    sintético porque su texto no tiene ruido)."""
    datos_con_none = OCRData(
        records={
            0: [
                {
                    "id": "palabra_1",
                    "parent": "linea_1",
                    "value": "Hola",
                    "confidence": 90,
                    "x1": 0,
                    "y1": 0,
                    "x2": 10,
                    "y2": 10,
                },
                {
                    "id": "palabra_2",
                    "parent": "linea_1",
                    "value": None,
                    "confidence": None,
                    "x1": 11,
                    "y1": 0,
                    "x2": 20,
                    "y2": 10,
                },
            ]
        }
    )
    monkeypatch.setattr(TesseractOCR, "of", lambda self, document: datos_con_none)

    resultado = TesseractOCRSinNulos(lang="spa+eng").of(document=None)

    valores = [palabra["value"] for palabra in resultado.records[0]]
    assert None not in valores
    assert valores == ["Hola", ""]
