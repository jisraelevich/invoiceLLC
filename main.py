"""
Punto de entrada principal del Facturador AFIP.
Orquesta la lectura del Excel, ejecución del bot y actualización de resultados.

Modo de uso:
    - Automático (viernes 9 AM): python main.py
    - Inmediato: python main.py --ahora
    - Con modo de pausas: python main.py --ahora --modo 1
"""

import asyncio
import argparse
import sys
import random
from pathlib import Path
from datetime import datetime

from excel_handler import ExcelHandler, crear_excel_ejemplo
from csv_handler import CSVHandler
from bot import BotAFIP
from scheduler import Scheduler
from utils import LoggerFactory, validar_ambiente, crear_excel_si_no_existe
from config import (
    AFIP_CUIT, AFIP_PASSWORD, AFIP_PUNTO_VENTA, HEADLESS, CSV_FILE, 
    SCHEDULER_HORA, SCHEDULER_DIA, AFIP_EMPRESA_NOMBRE
)

# Variables globales de logger
logger = LoggerFactory.get_logger(__name__)


async def procesar_factura(bot: BotAFIP, csv_handler: CSVHandler, fila: dict, modo_pausas: int = 2) -> bool:
    """
    Procesa una factura individual usando el bot ya inicializado.
    El navegador se mantiene abierto entre facturas.
    
    Args:
        bot: Instancia del BotAFIP con sesión activa
        csv_handler: Instancia del manejador de CSV
        fila: Diccionario con datos de la factura
        modo_pausas: Modo de pausas (1=rápido, 2=aleatorio, 3=humanizado)
        
    Returns:
        bool: True si se procesó exitosamente
    """
    try:
        logger.info(f"Procesando factura: {fila.get('descripcion', 'sin descripción')}")
        
        # Validar datos requeridos
        campos_requeridos = ['fecha', 'descripcion', 'monto']
        for campo in campos_requeridos:
            if campo not in fila or not fila[campo]:
                logger.error(f"Campo requerido faltante o vacío: {campo}")
                return False
        
        # Preparar datos para la factura
        datos = {
            "FECHA": str(fila['fecha']),
            "CODIGO": str(fila.get('codigo', '055')),
            "PRODUCTO SERVICIO": str(fila['descripcion']),
            "PRECIO UNITARIO": str(fila['monto'])
        }
        
        # Generar factura (el navegador ya está en el menú)
        exito, cae, nro_comprobante = await bot.generar_factura(datos)
        
        # IMPORTANTE: Siempre intentar retornar al menú, incluso si falló
        await bot.retornar_al_menu()
        
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
        # Intentar retornar al menú incluso en excepción
        try:
            await bot.retornar_al_menu()
        except:
            pass
        return False


async def ejecutar_facturador(modo_pausas=2):
    """
    Ejecuta el ciclo principal del facturador.
    Lee el CSV, realiza login UNA sola vez, genera todas las facturas, y cierra.
    
    Args:
        modo_pausas: 1=sin pausa, 2=aleatorio (30-60s), 3=completo (humanizado)
    """
    logger.info("="*60)
    logger.info("Iniciando Facturador AFIP")
    logger.info(f"Modo de pausas: {['RÁPIDO','ALEATORIO','HUMANIZADO'][modo_pausas-1]}")
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
    
    # ========== INICIALIZAR BOT UNA SOLA VEZ ==========
    bot = BotAFIP(AFIP_CUIT, AFIP_PASSWORD, AFIP_EMPRESA_NOMBRE, HEADLESS, AFIP_PUNTO_VENTA, modo_pausas)
    
    try:
        # Iniciar navegador
        if not await bot.iniciar_navegador():
            logger.error("❌ Error al iniciar navegador")
            return False
        
        # Realizar login
        if not await bot.login():
            logger.error("❌ Error durante login")
            await bot.cerrar()
            return False
        
        # Seleccionar empresa
        if not await bot.seleccionar_empresa():
            logger.error("❌ Error seleccionando empresa")
            await bot.cerrar()
            return False
        
        # Navegar a menú principal
        if not await bot.navegar_menu_principal():
            logger.error("❌ Error navegando menú principal")
            logger.error("━" * 60)
            logger.error("⚠️  PROBABLE CAUSA: AFIP está temporalmente fuera de servicio")
            logger.error("📝 Acciones recomendadas:")
            logger.error("   1. Espera 5-10 minutos e intenta nuevamente")
            logger.error("   2. Prueba accediendo manualmente a https://auth.afip.gov.ar")
            logger.error("   3. Si AFIP funciona bien, contacta soporte técnico")
            logger.error("━" * 60)
            await bot.cerrar()
            return False
        
        logger.info("✓ SESIÓN INITIALIZED - Listo para procesar facturas")
        
        # ========== PROCESAR CADA FACTURA ==========
        exitosas = 0
        fallidas = 0
        
        for idx, fila in enumerate(filas_pendientes, 1):
            logger.info(f"\n[{idx}/{len(filas_pendientes)}] Procesando factura...")
            
            if await procesar_factura(bot, csv_handler, fila, modo_pausas):
                exitosas += 1
            else:
                fallidas += 1
            
            # Pausa entre facturas según modo
            if idx < len(filas_pendientes):
                if modo_pausas == 1:
                    # Modo RÁPIDO: sin pausa
                    pass
                elif modo_pausas == 2:
                    # Modo ALEATORIO: 4-15 segundos
                    pausa = random.randint(4, 15)
                    logger.info(f"⏳ Pausa: {pausa} segundos")
                    await asyncio.sleep(pausa)
                elif modo_pausas == 3:
                    # Modo HUMANIZADO: 60-120 segundos
                    pausa = random.randint(60, 120)
                    logger.info(f"⏳ Pausa: {pausa} segundos")
                    await asyncio.sleep(pausa)
        
        # Cerrar navegador
        await bot.cerrar()
        
        # Guardar cambios en el MISMO archivo que se cargó
        logger.info("\nActualizando facturas.csv...")
        if csv_handler.guardar_csv("facturas.csv"):
            logger.info("✓ Facturas actualizadas en facturas.csv")
        else:
            logger.error("❌ Error al actualizar CSV")
        
        # Resumen
        logger.info("\n" + "="*60)
        logger.info(f"RESUMEN: {exitosas} exitosa(s), {fallidas} fallida(s)")
        logger.info("="*60)
        
        return fallidas == 0
        
    except Exception as e:
        logger.error(f"Error en facturador: {e}", exc_info=True)
        try:
            await bot.cerrar()
        except:
            pass
        return False


def tarea_facturador_programada():
    """
    Wrapper para ejecutar el facturador como tarea programada.
    Usa modo 2 (aleatorio) por defecto.
    """
    try:
        asyncio.run(ejecutar_facturador(modo_pausas=2))
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
        "--modo",
        type=int,
        choices=[1, 2, 3],
        default=2,
        help="Modo de pausas: 1=Rápido, 2=Aleatorio (defecto), 3=Humanizado"
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
            asyncio.run(ejecutar_facturador(args.modo))
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
