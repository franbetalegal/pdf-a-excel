from pathlib import Path

from extractor_ocr import extraer_tablas_ocr

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
