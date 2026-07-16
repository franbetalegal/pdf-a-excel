#!/bin/bash
# Arranca el Convertidor PDF a Excel y abre el navegador.
cd "$(dirname "$0")"

if [ ! -f venv/bin/streamlit ]; then
    echo "La aplicación no está instalada. Ejecuta primero 'instalar.command'."
    exit 1
fi

./venv/bin/streamlit run app.py
