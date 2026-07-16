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

echo ""
echo "✅ Instalación completada. Usa 'iniciar.command' para abrir la aplicación."
