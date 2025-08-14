Capturador de Pantalla Personalizado
Este es un programa de captura de pantalla hecho a la medida para Windows. Fue creado para resolver el problema de gestionar múltiples capturas de pantalla, ofreciendo un flujo de trabajo rápido y eficiente sin llenar el disco duro de archivos innecesarios.

Características Principales
Atajos de teclado personalizables: El programa funciona en segundo plano, listo para ser activado con un atajo de teclado a tu medida.

Tres opciones de salida: Después de capturar un área, el programa te da la opción de guardar de forma permanente, guardar temporalmente o copiar al portapapeles.

Autolimpieza de archivos temporales: Las capturas guardadas en la carpeta Temporales se borran automáticamente después de 24 horas.

Distribución sencilla: El proyecto se puede empaquetar en un solo archivo .exe para que cualquier persona pueda usarlo sin necesidad de instalar Python o las librerías necesarias.

Cómo Usar (Para el usuario)
Si tienes el archivo capturas.exe, solo necesitas seguir estos pasos:

Haz doble clic en el archivo capturas.exe. Se abrirá una ventana de terminal en segundo plano.

El programa ya está funcionando. Puedes minimizar la ventana de terminal y usar los siguientes atajos de teclado:

Alt + h: Selecciona un área de la pantalla y muestra un menú para guardar o copiar.

Ctrl + y: Selecciona un área y copia la captura directamente al portapapeles, sin mostrar el menú.

Para cerrar el programa, simplemente cierra la ventana de terminal.

Cómo Instalar y Ejecutar (Para desarrolladores)
Si quieres ejecutar el script de Python directamente, sigue estos pasos:

Clona el repositorio.

Instala las librerías necesarias usando pip:

Bash

pip install keyboard Pillow pywin32
Ejecuta el script desde tu terminal:

Bash

python capturas.py
Cómo Generar el Archivo .exe
Si deseas crear tu propio archivo ejecutable para compartir, necesitarás PyInstaller:

Instala PyInstaller con pip:

Bash

pip install pyinstaller
Ejecuta el siguiente comando en la misma carpeta donde está capturas.py:

Bash

pyinstaller --onefile capturas.py
El archivo capturas.exe se generará en la carpeta dist.

Creador: [Tu Nombre]

Contacto: [Tu Email o Perfil de GitHub]
