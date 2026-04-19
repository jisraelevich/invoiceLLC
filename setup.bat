@echo off
REM Script de instalación para Windows
REM Instala Python, dependencias y realiza setup inicial

echo.
echo ========================================
echo Facturador AFIP - Setup Inicial (Windows)
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en PATH
    echo Descárgalo desde: https://www.python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

echo [OK] Python detectado

REM Crear entorno virtual
echo.
echo Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual
    pause
    exit /b 1
)

REM Activar entorno virtual
echo.
echo Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)

REM Instalar dependencias
echo.
echo Instalando dependencias de Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias
    pause
    exit /b 1
)

REM Instalar navegadores Playwright
echo.
echo Instalando navegadores Playwright (esto puede tardar varios minutos)...
playwright install
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar los navegadores
    pause
    exit /b 1
)

REM Crear Excel de ejemplo
echo.
echo Creando Excel de ejemplo...
python main.py --crear-ejemplo
if errorlevel 1 (
    echo [ERROR] No se pudo crear el Excel
    pause
    exit /b 1
)

REM Copiar .env.example a .env
echo.
echo Creando archivo .env...
if not exist .env (
    copy .env.example .env
    echo [OK] Archivo .env creado desde .env.example
) else (
    echo [AVISO] El archivo .env ya existe
)

echo.
echo ========================================
echo INSTALACION COMPLETADA
echo ========================================
echo.
echo PRÓXIMOS PASOS:
echo 1. Edita el archivo .env con tus datos AFIP:
echo    - AFIP_CUIT=tu_cuit
echo    - AFIP_PASSWORD=tu_clave_fiscal
echo.
echo 2. Verifica facturas.xlsx está listo (ya fue creado)
echo.
echo 3. Ejecuta el facturador:
echo    - Modo inmediato:  python main.py --ahora
echo    - Modo automático: python main.py
echo.
echo Para más ayuda, lee README.md
echo.
pause
