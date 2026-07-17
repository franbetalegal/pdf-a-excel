@echo off
REM Instalacion del Convertidor PDF a Excel (Windows).
REM Si el ordenador no tiene Python, lo descarga de python.org y lo instala
REM SOLO para el usuario actual (no requiere permisos de administrador).
REM Despues crea un entorno aislado dentro de esta carpeta con la aplicacion.
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "PYTHON="

REM --- 1. Buscar un Python ya instalado (sin tocar el alias de la Microsoft Store) ---
for /f "delims=" %%P in ('py -3 -c "import sys;print(sys.executable)" 2^>nul') do set "PYTHON=%%P"

if not defined PYTHON (
    for /d %%D in ("%LocalAppData%\Programs\Python\Python3*") do (
        if exist "%%D\python.exe" set "PYTHON=%%D\python.exe"
    )
)

REM --- 2. Si no hay Python, descargarlo e instalarlo solo para este usuario ---
if not defined PYTHON (
    echo No se encontro Python en este ordenador.
    echo Descargando Python 3.12 desde python.org ^(unos 25 MB^)...
    curl -L -o "%TEMP%\python-instalador.exe" https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
    if errorlevel 1 (
        echo.
        echo ERROR: no se pudo descargar Python. Comprueba la conexion a internet.
        pause
        exit /b 1
    )
    echo Instalando Python solo para tu usuario ^(sin permisos de administrador^)...
    "%TEMP%\python-instalador.exe" /passive InstallAllUsers=0 PrependPath=1 Include_test=0
    del "%TEMP%\python-instalador.exe" >nul 2>nul
    for /d %%D in ("%LocalAppData%\Programs\Python\Python3*") do (
        if exist "%%D\python.exe" set "PYTHON=%%D\python.exe"
    )
    if not defined PYTHON (
        echo.
        echo ERROR: la instalacion de Python no se completo.
        pause
        exit /b 1
    )
)

echo.
echo Usando Python: !PYTHON!
echo.
echo Creando el entorno de la aplicacion...
"!PYTHON!" -m venv venv
if errorlevel 1 (
    echo ERROR: no se pudo crear el entorno virtual.
    pause
    exit /b 1
)

echo Instalando dependencias ^(puede tardar unos minutos^)...
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: fallo la instalacion de dependencias. Comprueba la conexion a internet.
    pause
    exit /b 1
)

REM Evita que Streamlit pida un email en el primer arranque.
if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    echo [general]> "%USERPROFILE%\.streamlit\credentials.toml"
    echo email = "">> "%USERPROFILE%\.streamlit\credentials.toml"
)

echo Comprobando la instalacion...
venv\Scripts\python -c "import cv2, camelot, pandas, streamlit, openpyxl"
if errorlevel 1 (
    echo.
    echo AVISO: las librerias se instalaron pero no pueden cargarse.
    echo Es probable que falte "Microsoft Visual C++ Redistributable".
    echo Consulta la seccion "Problemas comunes" del README.md.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Instalacion completada y verificada.
echo  Usa "iniciar.bat" para abrir la aplicacion.
echo ============================================================
pause
