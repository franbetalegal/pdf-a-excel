# tests/fixtures/generar_fixtures.py
"""Genera los PDF de muestra usados en los tests.

Ejecutar una sola vez (o cuando cambie el contenido de prueba deseado):
    python tests/fixtures/generar_fixtures.py

Los PDF resultantes se commitean junto al código; los tests no los
regeneran en cada ejecución.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

CARPETA = Path(__file__).parent

FILAS = [
    ["Producto", "Cantidad", "Precio"],
    ["Tornillo", "10", "1.20"],
    ["Tuerca", "20", "0.50"],
]


def generar_pdf_digital() -> None:
    """PDF con texto seleccionable y una tabla con líneas dibujadas."""
    ruta = CARPETA / "digital_con_lineas.pdf"
    c = canvas.Canvas(str(ruta), pagesize=A4)
    ancho, alto = A4
    x0, y0 = 50, alto - 150
    col_x = [x0, x0 + 150, x0 + 300]
    alto_fila = 25

    for i, fila in enumerate(FILAS):
        y = y0 - i * alto_fila
        for j, celda in enumerate(fila):
            c.drawString(col_x[j] + 5, y - 17, celda)

    ancho_tabla = 450
    alto_tabla = alto_fila * len(FILAS)
    c.rect(x0, y0 - alto_tabla + alto_fila, ancho_tabla, alto_tabla)
    for i in range(1, len(FILAS)):
        y = y0 - i * alto_fila + alto_fila
        c.line(x0, y, x0 + ancho_tabla, y)
    for x in col_x[1:]:
        c.line(x, y0 - alto_tabla + alto_fila, x, y0 + alto_fila)
    c.save()
    print("generado", ruta)


def generar_pdf_escaneado() -> None:
    """PDF de una sola página que es una imagen (sin capa de texto),
    con columnas alineadas por posición X pero sin líneas de tabla."""
    ruta = CARPETA / "escaneado_imagen.pdf"
    imagen = Image.new("RGB", (1000, 400), "white")
    dibujo = ImageDraw.Draw(imagen)
    fuente = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial.ttf", 28
    )
    col_x = [50, 400, 700]
    for i, fila in enumerate(FILAS):
        y = 40 + i * 60
        for j, celda in enumerate(fila):
            dibujo.text((col_x[j], y), celda, fill="black", font=fuente)
    imagen.save(ruta, "PDF")
    print("generado", ruta)


if __name__ == "__main__":
    generar_pdf_digital()
    generar_pdf_escaneado()
