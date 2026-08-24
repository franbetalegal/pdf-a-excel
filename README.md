# Convertidor de PDF a Excel

Aplicación web local que extrae tablas de PDFs, tanto con bordes visibles como escaneadas sin bordes (vía OCR local), y las exporta a Excel. Todo se ejecuta en tu ordenador; no se sube nada a internet.

## Requisitos

- **Windows:** ninguno. El instalador descarga Python automáticamente si no está instalado, en modo "solo para este usuario" — **no hacen falta permisos de administrador**. Solo se necesita conexión a internet durante la instalación.
- **macOS:** Python 3.10 o superior ([python.org](https://www.python.org/downloads/), puede instalarse sin admin).

Sin Ghostscript ni ninguna otra dependencia de sistema. (Para PDF escaneados hace falta Tesseract OCR — ver la sección «PDF escaneados» más abajo.)

## Instalación

1. Copia esta carpeta al ordenador (sin la subcarpeta `venv`, si existe).
2. Ejecuta el script de instalación (doble clic):
   - Windows: `instalar.bat`
   - macOS: `instalar.command`

El script instala Python si hace falta (solo en tu perfil de usuario) y crea un entorno aislado dentro de la propia carpeta (`venv/`). No toca nada del sistema.

> **Windows:** si SmartScreen muestra un aviso al ejecutar el script, pulsa «Más información» → «Ejecutar de todas formas».
> **macOS:** si aparece un aviso de seguridad, haz clic derecho sobre el archivo → «Abrir».

## PDF escaneados (sin bordes de tabla)

Además de tablas con bordes visibles, la aplicación puede leer PDF
escaneados (imagen, sin texto seleccionable) cuyas tablas no tienen
líneas dibujadas pero sí columnas alineadas. Para esto usa OCR local
(Tesseract) — el documento no sale de tu ordenador en ningún momento.

Como el OCR no es infalible (letra borrosa, sellos, escaneo torcido),
la app muestra la tabla detectada en una rejilla editable para corregirla
antes de exportar a Excel.

**Requiere tener Tesseract OCR instalado.** `instalar.bat`/`instalar.command`
y `actualizar.bat`/`actualizar.command` intentan instalarlo automáticamente:
en Windows con `winget` (si está disponible en el sistema) y en macOS con
Homebrew (si está instalado). Si no se puede instalar solo, muestran un
aviso y hace falta instalarlo a mano:

- **Windows:** instalar desde [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) (incluye datos de idioma español si se marca esa opción durante la instalación).
- **macOS:** `brew install tesseract tesseract-lang`
- **Linux:** `sudo apt install tesseract-ocr tesseract-ocr-spa`

Si Tesseract no está instalado, la app sigue funcionando con normalidad
para PDF con tablas de bordes visibles; solo al subir un PDF escaneado
avisará de que falta instalarlo.

## Uso

1. Ejecuta `iniciar.command` (macOS) o `iniciar.bat` (Windows). Se abrirá el navegador automáticamente.
2. Sube tu PDF.
3. Revisa las tablas detectadas y desmarca las que no quieras.
4. Elige la organización: **una hoja por tabla** o **todas en una sola hoja**.
5. Descarga el Excel.

Para cerrar la aplicación, cierra la ventana del terminal.

## Actualizar a una nueva versión

La aplicación comprueba al arrancar si hay una versión nueva en GitHub y, si la hay, muestra un aviso con el botón **«Actualizar y reiniciar»** (en Windows y macOS): la aplicación se cierra, se actualiza sola y vuelve a abrirse (requiere internet; si no hay conexión, simplemente no aparece el aviso). La versión instalada se muestra en la esquina superior derecha.

También puedes actualizar manualmente con la aplicación cerrada: `actualizar.bat` (Windows) o `actualizar.command` (macOS).

## Problemas comunes

**«Falta un componente del sistema (Microsoft Visual C++ Redistributable)»** o un error que menciona «DLL load failed» al analizar un PDF: al ordenador le falta un componente estándar de Microsoft que algunas librerías necesitan. Se instala una sola vez desde [aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe) — **este componente sí requiere permisos de administrador**, así que pídeselo al departamento de informática si tu usuario no los tiene.

**Cualquier otro error al analizar un PDF:** despliega «Detalles técnicos del error» en la propia aplicación, copia el texto y envíaselo al responsable de la aplicación.

## Limitaciones

- PDF digitales: solo detecta tablas **con bordes/líneas visibles** (modo *lattice* de Camelot). Los datos alineados sin rejilla no se detectan en esta rama.
- PDF escaneados: requiere columnas alineadas por posición y Tesseract instalado; la precisión del OCR depende de la calidad del escaneo, por eso la tabla es editable antes de exportar.
