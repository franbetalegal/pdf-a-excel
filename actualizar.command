#!/bin/bash
# Actualiza la aplicación a la última versión publicada en GitHub
# sin tocar el entorno ya instalado (carpeta venv).
cd "$(dirname "$0")"

echo "Descargando la última versión…"
ZIP="$(mktemp -t pdf-a-excel).zip"
if ! curl -fsSL -o "$ZIP" https://github.com/franbetalegal/pdf-a-excel/archive/refs/heads/main.zip; then
    echo "ERROR: no se pudo descargar la actualización. Comprueba la conexión a internet."
    exit 1
fi

echo "Aplicando la actualización…"
CARPETA_TMP="$(mktemp -d)"
unzip -q -o "$ZIP" -d "$CARPETA_TMP"
cp -R "$CARPETA_TMP/pdf-a-excel-main/." .
rm -rf "$CARPETA_TMP" "$ZIP"

if [ -f venv/bin/python ]; then
    echo "Actualizando dependencias…"
    ./venv/bin/python -m pip install -q -r requirements.txt
fi

echo "Comprobando Tesseract OCR (necesario para PDF escaneados)…"
if command -v tesseract &>/dev/null; then
    echo "Tesseract OCR ya está instalado."
elif command -v brew &>/dev/null; then
    echo "Instalando Tesseract OCR con Homebrew…"
    brew install tesseract tesseract-lang || echo "AVISO: no se pudo instalar Tesseract automáticamente. Instálalo con 'brew install tesseract tesseract-lang' o consulta la sección «PDF escaneados» del README."
else
    echo "AVISO: no se encontró Homebrew, así que no se puede instalar Tesseract automáticamente."
    echo "Instálalo con Homebrew (https://brew.sh) y 'brew install tesseract tesseract-lang', o consulta la sección «PDF escaneados» del README. La app funciona igualmente con PDF de bordes visibles sin esto."
fi

# Evita que Streamlit pida un email en el primer arranque.
if [ ! -f "$HOME/.streamlit/credentials.toml" ]; then
    mkdir -p "$HOME/.streamlit"
    printf '[general]\nemail = ""\n' > "$HOME/.streamlit/credentials.toml"
fi

echo ""
echo "✅ Actualización completada."

# Con --reiniciar (usado por el botón «Actualizar y reiniciar» de la app)
# se vuelve a abrir la aplicación automáticamente.
if [ "$1" = "--reiniciar" ]; then
    exec ./venv/bin/streamlit run app.py
fi
echo "Ya puedes usar 'iniciar.command'."
