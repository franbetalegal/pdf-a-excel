@echo off
REM Actualiza la aplicacion a la ultima version publicada en GitHub
REM sin tocar el entorno ya instalado (carpeta venv).
cd /d "%~dp0"

echo Descargando la ultima version...
curl -L -o "%TEMP%\pdf-a-excel.zip" https://github.com/franbetalegal/pdf-a-excel/archive/refs/heads/main.zip
if errorlevel 1 (
    echo ERROR: no se pudo descargar la actualizacion. Comprueba la conexion a internet.
    pause
    exit /b 1
)

echo Aplicando la actualizacion...
tar -xf "%TEMP%\pdf-a-excel.zip" -C "%TEMP%"
xcopy /E /Y /Q "%TEMP%\pdf-a-excel-main\*" . >nul
del "%TEMP%\pdf-a-excel.zip" >nul 2>nul
rmdir /S /Q "%TEMP%\pdf-a-excel-main" >nul 2>nul

if exist venv\Scripts\python.exe (
    echo Actualizando dependencias...
    venv\Scripts\python -m pip install -q -r requirements.txt
)

REM Evita que Streamlit pida un email en el primer arranque.
if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    echo [general]> "%USERPROFILE%\.streamlit\credentials.toml"
    echo email = "">> "%USERPROFILE%\.streamlit\credentials.toml"
)

echo.
echo Actualizacion completada.

REM Con /reiniciar (usado por el boton "Actualizar y reiniciar" de la app)
REM se vuelve a abrir la aplicacion automaticamente.
if /I "%~1"=="/reiniciar" (
    start "" iniciar.bat
    exit /b 0
)
echo Ya puedes usar "iniciar.bat".
pause
