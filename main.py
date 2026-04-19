"""
Punto de entrada principal del Facturador AFIP.
Orquesta la lectura del Excel, ejecución del bot y actualización de resultados.

Modo de uso:
    - Automático (viernes 9 AM): python main.py
    - Inmediato: python main.py --ahora
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime

from excel_handler import ExcelHandler, crear_excel_ejemplo
from csv_handler import CSVHandler
from bot import ejecutar_bot_factura
from scheduler import Scheduler
from utils import LoggerFactory, validar_ambiente, crear_excel_si_no_existe
from config import (
    AFIP_CUIT, AFIP_PASSWORD, AFIP_PUNTO_VENTA, HEADLESS, CSV_FILE, 
    SCHEDULER_HORA, SCHEDULER_DIA, AFIP_EMPRESA_NOMBRE
)

# Variables globales de logger
logger = LoggerFactory.get_logger(__name__)


async def procesar_factura(csv_handler: CSVHandler, fila: dict, cuit: str, 
                           password: str, punto_venta: int, headless: bool) -> bool:
    """
    Procesa una factura individual.
    
    Args:
        csv_handler: Instancia del manejador de CSV
        fila: Diccionario con datos de la factura
        cuit: CUIT del usuario AFIP
        password: Contraseña del usuario AFIP
        punto_venta: Punto de venta a usar
        headless: Si ejecutar en modo headless
        
    Returns:
        bool: True si se procesó exitosamente
    """
    try:
        logger.info(f"Procesando factura: {fila.get('descripcion', 'sin descripción')}")
        
        # Validar datos requeridos
        campos_requeridos = ['fecha', 'descripcion', 'monto', 'cuit_cliente', 'nombre_cliente']
        for campo in campos_requeridos:
            if campo not in fila or not fila[campo]:
                logger.error(f"Campo requerido faltante o vacío: {campo}")
                return False
        
        # Ejecutar bot para generar factura
        exito, cae, nro_comprobante = await ejecutar_bot_factura(
            cuit=cuit,
            password=password,
            punto_venta=punto_venta,
            fecha=str(fila['fecha']),
            codigo=str(fila.get('codigo', '055')),
            descripcion=str(fila['descripcion']),
            monto=str(fila['monto']),
            cuit_cliente=str(fila['cuit_cliente']),
            nombre_cliente=str(fila['nombre_cliente']),
            empresa_nombre=AFIP_EMPRESA_NOMBRE,
            headless=headless
        )
        
        if exito and cae and nro_comprobante:
            # Actualizar CSV con resultados
            if csv_handler.actualizar_fila(fila['numero_fila'], cae, nro_comprobante):
                logger.info(f"Factura actualizada en CSV: CAE={cae}, Nro={nro_comprobante}")
                return True
            else:
                logger.error("Error al actualizar la factura en CSV (pero se generó en AFIP)")
                return False
        else:
            logger.error("Error al generar factura en AFIP")
            return False
            
    except Exception as e:
        logger.error(f"Excepción al procesar factura: {e}", exc_info=True)
        return False


async def ejecutar_facturador():
    """
    Ejecuta el ciclo principal del facturador.
    Lee el Excel, procesa facturas pendientes y actualiza resultados.
    """
    logger.info("="*60)
    logger.info("Iniciando Facturador AFIP")
    logger.info("="*60)
    
    # Validar configuración
    es_valido, errores = validar_ambiente()
    if not es_valido:
        logger.error("❌ No se puede continuar - hay errores de configuración")
        return False
    
    logger.info(f"✓ Configuración cargada:")
    logger.info(f"  - CUIT: {AFIP_CUIT[:4]}...{AFIP_CUIT[-2:]}")
    logger.info(f"  - Punto de Venta: {AFIP_PUNTO_VENTA}")
    logger.info(f"  - Modo Headless: {HEADLESS}")
    
    # Cargar CSV
    csv_handler = CSVHandler("facturas.csv")
    if not csv_handler.cargar_csv():
        logger.error("❌ Error al cargar el archivo CSV")
        return False
    
    # Obtener facturas pendientes
    filas_pendientes = csv_handler.obtener_filas_pendientes()
    
    if not filas_pendientes:
        logger.info("✓ Sin facturas pendientes para procesar")
        return True
    
    logger.info(f"✓ Se encontraron {len(filas_pendientes)} factura(s) pendiente(s)")
    
    # Procesar cada factura
    exitosas = 0
    fallidas = 0
    
    for idx, fila in enumerate(filas_pendientes, 1):
        logger.info(f"\n[{idx}/{len(filas_pendientes)}] Procesando factura...")
        
        if await procesar_factura(csv_handler, fila, AFIP_CUIT, AFIP_PASSWORD, AFIP_PUNTO_VENTA, HEADLESS):
            exitosas += 1
        else:
            fallidas += 1
        
        # Breve pausa entre facturas para evitar sobrecargar
        if idx < len(filas_pendientes):
            await asyncio.sleep(2)
    
    # Guardar cambios en CSV
    logger.info("\nGuardando cambios en CSV...")
    if csv_handler.guardar_csv("facturas_emitidas.csv"):
        logger.info("✓ CSV guardado correctamente en facturas_emitidas.csv")
    else:
        logger.error("❌ Error al guardar CSV")
    
    # Resumen
    logger.info("\n" + "="*60)
    logger.info(f"RESUMEN: {exitosas} exitosa(s), {fallidas} fallida(s)")
    logger.info("="*60)
    
    return fallidas == 0


def tarea_facturador_programada():
    """
    Wrapper para ejecutar el facturador como tarea programada.
    """
    try:
        asyncio.run(ejecutar_facturador())
    except Exception as e:
        logger.error(f"Error en tarea programada: {e}", exc_info=True)


def main():
    """Función principal."""
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description="Facturador Automático AFIP"
    )
    parser.add_argument(
        "--ahora",
        action="store_true",
        help="Ejecutar inmediatamente (no esperar al viernes)"
    )
    parser.add_argument(
        "--crear-ejemplo",
        action="store_true",
        help="Crear un archivo Excel de ejemplo"
    )
    parser.add_argument(
        "--entorno",
        action="store_true",
        help="Mostrar variables de entorno configuradas"
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Mostrar logs disponibles"
    )
    
    args = parser.parse_args()
    
    # Crear Excel de ejemplo si se solicita
    if args.crear_ejemplo:
        logger.info("Creando archivo Excel de ejemplo...")
        if crear_excel_ejemplo(str(EXCEL_FILE)):
            logger.info(f"✓ Excel de ejemplo creado: {EXCEL_FILE}")
        return
    
    # Mostrar variables de entorno
    if args.entorno:
        logger.info("Variables de entorno:")
        logger.info(f"  AFIP_CUIT: {AFIP_CUIT[:4]}...{AFIP_CUIT[-2:] if AFIP_CUIT else 'NO CONFIGURADO'}")
        logger.info(f"  AFIP_PASSWORD: {'***OCULTO***' if AFIP_PASSWORD else 'NO CONFIGURADO'}")
        logger.info(f"  AFIP_PUNTO_VENTA: {AFIP_PUNTO_VENTA}")
        logger.info(f"  HEADLESS: {HEADLESS}")
        return
    
    # Mostrar logs disponibles
    if args.logs:
        from utils import listar_logs, obtener_estadisticas_logs
        logger.info("Estadísticas de logs:")
        stats = obtener_estadisticas_logs()
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        return
    
    # Ejecutar inmediatamente
    if args.ahora:
        logger.info("Modo: Ejecución inmediata")
        try:
            asyncio.run(ejecutar_facturador())
        except KeyboardInterrupt:
            logger.info("\nEjecución interrumpida por usuario")
        except Exception as e:
            logger.error(f"Error inesperado: {e}", exc_info=True)
    else:
        # Modo automático: viernes a las 9:00 AM
        logger.info("Modo: Ejecución automática (viernes a las 9:00 AM)")
        logger.info("Para ejecutar inmediatamente, use: python main.py --ahora")
        
        scheduler = Scheduler(tarea_facturador_programada, hora=SCHEDULER_HORA, dia_semana=SCHEDULER_DIA)
        scheduler.programar()
        
        logger.info(f"✓ Próxima ejecución: {scheduler.obtener_fecha_proxima_ejecucion()}")
        logger.info("Presione Ctrl+C para detener")
        
        try:
            scheduler.ejecutar_loop()
        except KeyboardInterrupt:
            logger.info("\nScheduler detenido por usuario")
            scheduler.detener()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Error crítico: {e}", exc_info=True)
        sys.exit(1)
