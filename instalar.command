#!/bin/bash
# Instalación del Convertidor PDF a Excel (macOS).
# Crea un entorno virtual dentro de esta carpeta e instala las dependencias.
# No requiere permisos de administrador.
cd "$(dirname "$0")"

if ! command -v python3 &>/dev/null; then
    echo "ERROR: No se encontró Python 3. Instálalo desde https://www.python.org/downloads/"
    exit 1
fi

echo "Creando entorno virtual…"
python3 -m venv venv

echo "Instalando dependencias (puede tardar unos minutos)…"
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

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
echo "✅ Instalación completada. Usa 'iniciar.command' para abrir la aplicación."
