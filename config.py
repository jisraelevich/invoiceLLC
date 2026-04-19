"""
Configuración centralizada del Facturador AFIP.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
CSV_FILE = BASE_DIR / "facturas.csv"

# Crear directorio de logs
LOGS_DIR.mkdir(exist_ok=True)

# Credenciales AFIP
AFIP_CUIT = os.getenv("AFIP_CUIT", "").strip()
AFIP_PASSWORD = os.getenv("AFIP_PASSWORD", "").strip()
AFIP_PUNTO_VENTA = int(os.getenv("AFIP_PUNTO_VENTA", "1"))
AFIP_EMPRESA_NOMBRE = os.getenv("AFIP_EMPRESA_NOMBRE", "").strip()

# Configuración del navegador
HEADLESS = False  # CAMBIAR A FALSE PARA EVITAR DETECCIÓN DE BOT
TIMEOUT_GENERAL = 30000  # 30 segundos en milisegundos
TIMEOUT_CORTO = 10000    # 10 segundos
TIMEOUT_LARGO = 60000    # 60 segundos

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_TO_FILE = True
LOG_TO_CONSOLE = True

# URLs de AFIP
AFIP_URL_LOGIN = "https://auth.afip.gov.ar/contribuyente_/login.xhtml"
AFIP_URL_COMPROBANTES = "https://serviciosweb.afip.gov.ar/vfp/abc"

# Configuración del scheduler
SCHEDULER_HORA = "09:00"
SCHEDULER_DIA = "friday"

# Validación de configuración
def validar_configuracion():
    """Valida que la configuración sea correcta."""
    errores = []
    
    if not AFIP_CUIT:
        errores.append("AFIP_CUIT no configurado")
    
    if not AFIP_PASSWORD:
        errores.append("AFIP_PASSWORD no configurado")
    
    if not CSV_FILE.exists():
        errores.append(f"Archivo CSV no encontrado: {CSV_FILE}")
    
    return errores


if __name__ == "__main__":
    # Si se ejecuta como módulo, mostrar configuración
    print("Configuración actual:")
    print(f"  CUIT: {AFIP_CUIT[:4]}...{AFIP_CUIT[-2:] if AFIP_CUIT else 'NO CONFIGURADO'}")
    print(f"  Punto de Venta: {AFIP_PUNTO_VENTA}")
    print(f"  Headless: {HEADLESS}")
    print(f"  Log Level: {LOG_LEVEL}")
    print(f"  CSV: {CSV_FILE}")
    print(f"  Logs: {LOGS_DIR}")
    
    errores = validar_configuracion()
    if errores:
        print("\n⚠️ Errores de configuración:")
        for error in errores:
            print(f"  - {error}")
