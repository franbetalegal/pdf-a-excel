# Convertidor de PDF a Excel

Aplicación web local que extrae tablas de PDFs (tablas con bordes visibles) y las exporta a Excel. Todo se ejecuta en tu ordenador; no se sube nada a internet.

## Requisitos

- **Windows:** ninguno. El instalador descarga Python automáticamente si no está instalado, en modo "solo para este usuario" — **no hacen falta permisos de administrador**. Solo se necesita conexión a internet durante la instalación.
- **macOS:** Python 3.10 o superior ([python.org](https://www.python.org/downloads/), puede instalarse sin admin).

Sin Ghostscript ni ninguna otra dependencia de sistema.

## Instalación

1. Copia esta carpeta al ordenador (sin la subcarpeta `venv`, si existe).
2. Ejecuta el script de instalación (doble clic):
   - Windows: `instalar.bat`
   - macOS: `instalar.command`

El script instala Python si hace falta (solo en tu perfil de usuario) y crea un entorno aislado dentro de la propia carpeta (`venv/`). No toca nada del sistema.

> **Windows:** si SmartScreen muestra un aviso al ejecutar el script, pulsa «Más información» → «Ejecutar de todas formas».
> **macOS:** si aparece un aviso de seguridad, haz clic derecho sobre el archivo → «Abrir».

## Uso

1. Ejecuta `iniciar.command` (macOS) o `iniciar.bat` (Windows). Se abrirá el navegador automáticamente.
2. Sube tu PDF.
3. Revisa las tablas detectadas y desmarca las que no quieras.
4. Elige la organización: **una hoja por tabla** o **todas en una sola hoja**.
5. Descarga el Excel.

Para cerrar la aplicación, cierra la ventana del terminal.

## Actualizar a una nueva versión

La aplicación comprueba al arrancar si hay una versión nueva en GitHub y, si la hay, muestra un aviso con el botón **«Actualizar y reiniciar»**: la aplicación se cierra, se actualiza sola y vuelve a abrirse (requiere internet; si no hay conexión, simplemente no aparece el aviso).

También puedes actualizar manualmente ejecutando `actualizar.bat` con la aplicación cerrada.

## Problemas comunes

**«Falta un componente del sistema (Microsoft Visual C++ Redistributable)»** o un error que menciona «DLL load failed» al analizar un PDF: al ordenador le falta un componente estándar de Microsoft que algunas librerías necesitan. Se instala una sola vez desde [aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe) — **este componente sí requiere permisos de administrador**, así que pídeselo al departamento de informática si tu usuario no los tiene.

**Cualquier otro error al analizar un PDF:** despliega «Detalles técnicos del error» en la propia aplicación, copia el texto y envíaselo al responsable de la aplicación.

## Limitaciones

- Solo detecta tablas **con bordes/líneas visibles** (modo *lattice* de Camelot). Los datos alineados sin rejilla no se detectan.
- No funciona con PDFs escaneados (imágenes); el PDF debe contener texto real.
