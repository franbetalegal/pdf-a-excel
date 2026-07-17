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
