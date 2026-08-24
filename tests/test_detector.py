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
