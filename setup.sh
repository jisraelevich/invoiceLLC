#!/bin/bash
# Script de instalación para Linux/Mac
# Instala Python, dependencias y realiza setup inicial

echo ""
echo "========================================"
echo "Facturador AFIP - Setup Inicial (Unix)"
echo "========================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no está instalado"
    echo "En macOS: brew install python3"
    echo "En Ubuntu: sudo apt-get install python3-venv python3-pip"
    exit 1
fi

echo "[OK] Python3 detectado: $(python3 --version)"

# Crear entorno virtual
echo ""
echo "Creando entorno virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo crear el entorno virtual"
    exit 1
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo activar el entorno virtual"
    exit 1
fi

# Instalar dependencias
echo ""
echo "Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudieron instalar las dependencias"
    exit 1
fi

# Instalar navegadores Playwright
echo ""
echo "Instalando navegadores Playwright (esto puede tardar varios minutos)..."
playwright install
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudieron instalar los navegadores"
    exit 1
fi

# Crear Excel de ejemplo
echo ""
echo "Creando Excel de ejemplo..."
python main.py --crear-ejemplo
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo crear el Excel"
    exit 1
fi

# Copiar .env.example a .env
echo ""
echo "Creando archivo .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[OK] Archivo .env creado desde .env.example"
else
    echo "[AVISO] El archivo .env ya existe"
fi

echo ""
echo "========================================"
echo "INSTALACION COMPLETADA"
echo "========================================"
echo ""
echo "PRÓXIMOS PASOS:"
echo "1. Edita el archivo .env con tus datos AFIP:"
echo "   - AFIP_CUIT=tu_cuit"
echo "   - AFIP_PASSWORD=tu_clave_fiscal"
echo ""
echo "2. Verifica facturas.xlsx está listo (ya fue creado)"
echo ""
echo "3. Ejecuta el facturador:"
echo "   - Modo inmediato:  python main.py --ahora"
echo "   - Modo automático: python main.py"
echo ""
echo "Para más ayuda, lee README.md"
echo ""
