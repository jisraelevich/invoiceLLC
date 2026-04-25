"""
Punto de entrada principal del Facturador AFIP.
Orquesta la lectura del CSV, ejecución del bot y actualización de resultados.

Modo de uso:
    - Inmediato: python main.py --ahora
    - Con modo de pausas: python main.py --ahora --modo 1
"""

import asyncio
import argparse
import sys
import random
import warnings

# Ignorar warnings de ResourceWarning de asyncio al cerrar Chromium en Windows
warnings.filterwarnings('ignore', category=ResourceWarning)

from csv_handler import CSVHandler
from bot import BotAFIP
from utils import LoggerFactory, validar_ambiente
from config import (
    AFIP_CUIT, AFIP_PASSWORD, AFIP_PUNTO_VENTA, HEADLESS, CSV_FILE, 
    AFIP_EMPRESA_NOMBRE
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
                logger.error(f"[ERROR] Campo requerido faltante o vacío: {campo}")
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
        logger.error("[ERROR] No se puede continuar - hay errores de configuración")
        return False
    
    logger.info(f"[OK] Configuración cargada:")
    logger.info(f"  - CUIT: {AFIP_CUIT[:4]}...{AFIP_CUIT[-2:]}")
    logger.info(f"  - Punto de Venta: {AFIP_PUNTO_VENTA}")
    logger.info(f"  - Modo Headless: {HEADLESS}")
    
    # Cargar CSV
    csv_handler = CSVHandler(str(CSV_FILE))
    if not csv_handler.cargar_csv():
        logger.error("[ERROR] Error al cargar el archivo CSV")
        return False
    
    # Obtener facturas pendientes
    filas_pendientes = csv_handler.obtener_filas_pendientes()
    
    if not filas_pendientes:
        logger.info("[OK] Sin facturas pendientes para procesar")
        return True
    
    logger.info(f"[OK] Se encontraron {len(filas_pendientes)} factura(s) pendiente(s)")
    
    # ========== INICIALIZAR BOT UNA SOLA VEZ ==========
    bot = BotAFIP(AFIP_CUIT, AFIP_PASSWORD, AFIP_EMPRESA_NOMBRE, HEADLESS, AFIP_PUNTO_VENTA, modo_pausas)
    
    try:
        # Iniciar navegador
        if not await bot.iniciar_navegador():
            logger.error("[ERROR] Error al iniciar navegador")
            return False
        
        # Realizar login
        if not await bot.login():
            logger.error("[ERROR] Error durante login")
            await bot.cerrar()
            return False
        
        # Seleccionar empresa
        if not await bot.seleccionar_empresa():
            logger.error("[ERROR] Error seleccionando empresa")
            await bot.cerrar()
            return False
        
        # Navegar a menú principal
        if not await bot.navegar_menu_principal():
            logger.error("[ERROR] Error navegando menú principal")
            logger.error("[INFO] PROBABLE CAUSA: AFIP está temporalmente fuera de servicio")
            logger.error("[INFO] Acciones recomendadas:")
            logger.error("   1. Espera 5-10 minutos e intenta nuevamente")
            logger.error("   2. Prueba accediendo manualmente a https://auth.afip.gov.ar")
            logger.error("   3. Si AFIP funciona bien, contacta soporte técnico")
            await bot.cerrar()
            return False
        
        logger.info("[OK] SESIÓN INITIALIZED - Listo para procesar facturas")
        
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
                    logger.info(f"[PAUSA] {pausa} segundos")
                    await asyncio.sleep(pausa)
                elif modo_pausas == 3:
                    # Modo HUMANIZADO: 60-120 segundos
                    pausa = random.randint(60, 120)
                    logger.info(f"[PAUSA] {pausa} segundos")
                    await asyncio.sleep(pausa)
        
        # Cerrar navegador
        await bot.cerrar()
        
        # Guardar cambios en el MISMO archivo que se cargó
        logger.info("\nActualizando facturas.csv...")
        if csv_handler.guardar_csv(str(CSV_FILE)):
            logger.info("[OK] Facturas actualizadas en facturas.csv")
        else:
            logger.error("[ERROR] Error al actualizar CSV")
        
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


def main():
    """Función principal."""
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description="Facturador Automático AFIP"
    )
    parser.add_argument(
        "--ahora",
        action="store_true",
        help="Ejecutar inmediatamente"
    )
    parser.add_argument(
        "--modo",
        type=int,
        choices=[1, 2, 3],
        default=2,
        help="Modo de pausas: 1=Rápido, 2=Aleatorio (defecto), 3=Humanizado"
    )
    
    args = parser.parse_args()
    
    # Requerir --ahora para ejecutar
    if not args.ahora:
        logger.error("[ERROR] Uso: python main.py --ahora [--modo 1|2|3]")
        logger.error("Ejemplo: python main.py --ahora --modo 2")
        sys.exit(1)
    
    # Ejecutar inmediatamente
    if args.ahora:
        logger.info("Modo: Ejecución inmediata")
        try:
            asyncio.run(ejecutar_facturador(args.modo))
        except KeyboardInterrupt:
            logger.info("\nEjecución interrumpida por usuario")
        except Exception as e:
            logger.error(f"Error inesperado: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Error crítico: {e}", exc_info=True)
        sys.exit(1)
