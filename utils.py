"""
Utilidades compartidas para el Facturador AFIP.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import traceback

from config import LOGS_DIR, LOG_LEVEL, LOG_TO_FILE, LOG_TO_CONSOLE


class LoggerFactory:
    """Factory para crear loggers configurados."""
    
    _loggers = {}
    
    @staticmethod
    def get_logger(nombre: str) -> logging.Logger:
        """
        Obtiene un logger configurado.
        
        Args:
            nombre: Nombre del logger (generalmente __name__)
            
        Returns:
            logging.Logger: Logger configurado
        """
        if nombre in LoggerFactory._loggers:
            return LoggerFactory._loggers[nombre]
        
        logger = logging.getLogger(nombre)
        
        # Evitar duplicar handlers
        if logger.handlers:
            return logger
        
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Formato de logging
        formato = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S'
        )
        
        # Handler a archivo
        if LOG_TO_FILE:
            fecha_log = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = LOGS_DIR / f"facturador_{fecha_log}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, LOG_LEVEL))
            file_handler.setFormatter(formato)
            logger.addHandler(file_handler)
        
        # Handler a consola
        if LOG_TO_CONSOLE:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, LOG_LEVEL))
            console_handler.setFormatter(formato)
            logger.addHandler(console_handler)
        
        LoggerFactory._loggers[nombre] = logger
        return logger


def crear_excel_si_no_existe():
    """Crea un Excel de ejemplo si no existe."""
    from excel_handler import crear_excel_ejemplo
    from config import EXCEL_FILE
    
    if not EXCEL_FILE.exists():
        logger = LoggerFactory.get_logger(__name__)
        logger.warning(f"Archivo {EXCEL_FILE} no encontrado. Creando ejemplo...")
        crear_excel_ejemplo(str(EXCEL_FILE))


def validar_ambiente():
    """
    Valida que el ambiente esté correctamente configurado.
    
    Returns:
        tuple: (es_valido, lista_de_errores)
    """
    from config import validar_configuracion
    
    logger = LoggerFactory.get_logger(__name__)
    
    errores = validar_configuracion()
    
    if errores:
        logger.error("❌ Errores de configuración detectados:")
        for error in errores:
            logger.error(f"   - {error}")
        return False, errores
    
    logger.info("✓ Configuración validada correctamente")
    return True, []


def manejar_excepcion(tipo_excepcion: Optional[Exception] = None):
    """
    Decorador para manejar excepciones de forma consistente.
    
    Uso:
        @manejar_excepcion()
        async def mi_funcion():
            ...
    """
    def decorador(func):
        async def wrapper(*args, **kwargs):
            logger = LoggerFactory.get_logger(func.__module__)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"❌ Error en {func.__name__}: {str(e)}")
                logger.debug(traceback.format_exc())
                raise
        return wrapper
    return decorador


def listar_logs():
    """
    Lista todos los logs disponibles.
    
    Returns:
        list: Lista de archivos de log
    """
    if not LOGS_DIR.exists():
        return []
    
    return sorted(
        LOGS_DIR.glob("facturador_*.log"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )


def obtener_ultimo_log() -> Optional[Path]:
    """
    Obtiene el último archivo de log.
    
    Returns:
        Path: Ruta del último log o None
    """
    logs = listar_logs()
    return logs[0] if logs else None


def limpiar_logs_antiguos(dias: int = 7):
    """
    Elimina logs más antiguos que X días.
    
    Args:
        dias: Número de días a retener
    """
    from time import time
    
    logger = LoggerFactory.get_logger(__name__)
    
    if not LOGS_DIR.exists():
        return
    
    limite_tiempo = time() - (dias * 86400)  # 86400 segundos por día
    eliminados = 0
    
    for log_file in LOGS_DIR.glob("facturador_*.log"):
        if log_file.stat().st_mtime < limite_tiempo:
            try:
                log_file.unlink()
                eliminados += 1
            except Exception as e:
                logger.warning(f"No se pudo eliminar {log_file}: {e}")
    
    if eliminados > 0:
        logger.info(f"Logs antiguos eliminados: {eliminados}")


def obtener_estadisticas_logs():
    """
    Obtiene estadísticas sobre los logs.
    
    Returns:
        dict: Estadísticas
    """
    logs = listar_logs()
    
    return {
        'total': len(logs),
        'ultimo': logs[0].name if logs else None,
        'directorio': str(LOGS_DIR),
    }


if __name__ == "__main__":
    # Test del logger
    logger = LoggerFactory.get_logger("test")
    logger.info("Esto es un mensaje de INFO")
    logger.warning("Esto es un mensaje de WARNING")
    logger.error("Esto es un mensaje de ERROR")
    
    print("\nEstadísticas de logs:")
    print(obtener_estadisticas_logs())
