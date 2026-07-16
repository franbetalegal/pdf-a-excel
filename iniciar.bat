@echo off
REM Arranca el Convertidor PDF a Excel y abre el navegador.
cd /d "%~dp0"

if not exist venv\Scripts\streamlit.exe (
    echo La aplicacion no esta instalada. Ejecuta primero "instalar.bat".
    pause
    exit /b 1
)

venv\Scripts\streamlit run app.py
