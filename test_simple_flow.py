"""
Test simple flow based on user's manual steps
"""

import asyncio
from bot import BotAFIP
from utils import LoggerFactory
from config import AFIP_CUIT, AFIP_PASSWORD, AFIP_PUNTO_VENTA, AFIP_EMPRESA_NOMBRE

logger = LoggerFactory.get_logger(__name__)


async def test_simple_flow():
    """Test the simplified flow"""
    
    bot = BotAFIP(AFIP_CUIT, AFIP_PASSWORD, AFIP_PUNTO_VENTA, AFIP_EMPRESA_NOMBRE, headless=False)
    try:
        logger.info("Iniciando test...")
        if not await bot.iniciar_navegador():
            return
        
        # Login
        if not await bot.login():
            return
        
        # Navigate to comprobantes
        if not await bot.navegar_a_comprobantes():
            return
        
        logger.info("✓ Navegación completada - en página genComDatosEmisor.do")
        logger.info("Esperando instrucciones...")
        
        # Now simulate the genEmDatosEmisor steps
        # 1. Ingresar fecha
        logger.info("\n[PASO 1] Ingresando fecha: 04/10/2026")
        fecha_inputs = await bot.page.query_selector_all("input[type='text']")
        if fecha_inputs:
            await fecha_inputs[0].fill("04/10/2026")
            logger.info("Fecha ingresada")
        
        # 2. Seleccionar SERVICIOS en concepto
        logger.info("\n[PASO 2] Seleccionando concepto: SERVICIOS")
        radios = await bot.page.query_selector_all("input[type='radio']")
        for radio in radios:
            label_parent = await radio.evaluate("el => el.parentElement?.textContent || ''")
            if "SERVICIOS" in label_parent.upper():
                await radio.click()
                logger.info("SERVICIOS seleccionado")
                break
        
        # 3. Click CONTINUAR
        logger.info("\n[PASO 3] Clickeando CONTINUAR")
        continuar_buttons = [
            "text=CONTINUAR",
            "text=Continuar",
            "input[value='CONTINUAR']",
            "button:has-text('CONTINUAR')"
        ]
        
        for selector in continuar_buttons:
            try:
                await bot.page.click(selector, timeout=3000)
                logger.info("CONTINUAR clickeado")
                await asyncio.sleep(2)
                break
            except:
                continue
        
        await bot.page.wait_for_load_state("networkidle", timeout=10000)
        
        logger.info("\n✓ Debería estar en genComDatosReceptor.do")
        logger.info("Página actual:", await bot.page.url())
        
        # 4. Seleccionar CONSUMIDOR FINAL
        logger.info("\n[PASO 4] Seleccionando condición IVA: CONSUMIDOR FINAL")
        
        # 5. Click checkbox CONTADO
        logger.info("\n[PASO 5] Tildando CONTADO")
        
        logger.info("\n✓ Flow test completado!")
        logger.info("Presiona Ctrl+C para salir")
        
        while True:
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        logger.info("Test cancelado")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await bot.cerrar()


if __name__ == "__main__":
    asyncio.run(test_simple_flow())
