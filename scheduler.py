"""
Módulo de programación de tareas automáticas.
Encargado de ejecutar el bot en horarios específicos.
"""

import time
import schedule
from datetime import datetime
from pathlib import Path
from typing import Callable

from utils import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class Scheduler:
    """Gestor de tareas programadas."""
    
    def __init__(self, tarea: Callable, hora: str = "09:00", dia_semana: str = "friday"):
        """
        Inicializa el scheduler.
        
        Args:
            tarea: Función a ejecutar
            hora: Hora en formato HH:MM (ej: "09:00")
            dia_semana: Día de la semana (ej: "friday", "monday", etc)
        """
        self.tarea = tarea
        self.hora = hora
        self.dia_semana = dia_semana
        self.activo = False
    
    def programar(self):
        """Programa la tarea automática."""
        try:
            job = schedule.every().friday.at(self.hora).do(self.tarea)
            logger.info(f"Tarea programada para cada {self.dia_semana} a las {self.hora}")
            return job
        except Exception as e:
            logger.error(f"Error al programar tarea: {e}")
            return None
    
    def ejecutar_loop(self):
        """
        Inicia el loop de ejecución de tareas programadas.
        Este loop debe ejecutarse continuamente.
        """
        logger.info("Iniciando loop de scheduler...")
        self.activo = True
        
        try:
            while self.activo:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        except KeyboardInterrupt:
            logger.info("Scheduler interrumpido por usuario")
            self.activo = False
        except Exception as e:
            logger.error(f"Error en loop de scheduler: {e}")
            self.activo = False
    
    def detener(self):
        """Detiene el loop de ejecución."""
        logger.info("Deteniendo scheduler...")
        self.activo = False
        schedule.clear()
    
    @staticmethod
    def obtener_fecha_proxima_ejecucion() -> str:
        """
        Calcula la fecha de la próxima ejecución programada.
        
        Returns:
            str: Fecha y hora de la próxima ejecución
        """
        try:
            jobs = schedule.get_jobs()
            if jobs:
                return jobs[0].next_run.strftime("%d/%m/%Y %H:%M:%S")
            return "No hay tareas programadas"
        except Exception as e:
            logger.error(f"Error al obtener próxima ejecución: {e}")
            return "Error"


if __name__ == "__main__":
    # Test del scheduler
    logger.info("Iniciando test del scheduler...")
