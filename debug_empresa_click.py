"""
Script de depuración para encontrar el selector correcto del botón de empresa.
Para cuando se llegue a la pantalla de selección de empresa, permitir interacción manual.
"""

import asyncio
from bot import BotAFIP
from utils import LoggerFactory
from config import AFIP_CUIT, AFIP_PASSWORD, AFIP_PUNTO_VENTA, AFIP_EMPRESA_NOMBRE

logger = LoggerFactory.get_logger(__name__)


async def debug_empresa_selection():
    """Ejecuta el bot hasta la pantalla de selección de empresa."""
    
    bot = BotAFIP(AFIP_CUIT, AFIP_PASSWORD, AFIP_PUNTO_VENTA, AFIP_EMPRESA_NOMBRE, headless=False)
    
    try:
        logger.info("Iniciando navegador...")
        if not await bot.iniciar_navegador():
            logger.error("No se pudo iniciar el navegador")
            return
        
        logger.info("Realizando login...")
        if not await bot.login():
            logger.error("Login fallido")
            return
        
        logger.info("Navegando a Facturación...")
        facturacion_selectors = [
            "text=Facturación",
            "a:has-text('Facturación')",
            "[href*='factura']",
        ]
        
        for selector in facturacion_selectors:
            try:
                await bot.page.click(selector, timeout=5000)
                logger.info(f"Clickeado 'Facturación'")
                break
            except:
                continue
        
        await asyncio.sleep(2)
        
        logger.info("Clickeando EMITIR FACTURA...")
        emitir_selectors = [
            "text=EMITIR FACTURA",
            "a:has-text('EMITIR FACTURA')",
        ]
        
        for selector in emitir_selectors:
            try:
                await bot.page.click(selector, timeout=3000)
                logger.info(f"Clickeado 'EMITIR FACTURA'")
                await asyncio.sleep(2)
                break
            except:
                continue
        
        logger.info("Navegando a generador de facturas...")
        await bot.page.goto("https://fe.afip.gob.ar/rcel/jsp/index_bis.jsp", wait_until="networkidle")
        await asyncio.sleep(2)
        
        logger.info("\n" + "="*70)
        logger.info("¡PANTALLA DE SELECCIÓN DE EMPRESA ALCANZADA!")
        logger.info("="*70)
        logger.info("\n📋 INSPECTOR DE PÁGINA - Elementos detectados:\n")
        
        # Inspeccionar todos los botones
        buttons = await bot.page.query_selector_all("button")
        logger.info(f"Botones encontrados: {len(buttons)}")
        for idx, btn in enumerate(buttons):
            text = await btn.text_content()
            classes = await btn.get_attribute("class")
            id_attr = await btn.get_attribute("id")
            logger.info(f"  [{idx}] Botón: '{text}' | class='{classes}' | id='{id_attr}'")
        
        # Inspeccionar todos los links
        logger.info("")
        links = await bot.page.query_selector_all("a")
        logger.info(f"Links encontrados: {len(links)}")
        for idx, link in enumerate(links):
            text = await link.text_content()
            href = await link.get_attribute("href")
            logger.info(f"  [{idx}] Link: '{text}' | href='{href}'")
        
        # Inspeccionar inputs
        logger.info("")
        inputs = await bot.page.query_selector_all("input")
        logger.info(f"Inputs encontrados: {len(inputs)}")
        for idx, inp in enumerate(inputs):
            type_attr = await inp.get_attribute("type")
            value = await inp.get_attribute("value")
            name = await inp.get_attribute("name")
            logger.info(f"  [{idx}] Input: type='{type_attr}' | name='{name}' | value='{value}'")
        
        # Inspeccionar cualquier elemento con "ESCALERA"
        logger.info("\n" + "-"*70)
        logger.info("Elementos que contienen 'ESCALERA':\n")
        try:
            escalera_elements = await bot.page.query_selector_all("//text()[contains(., 'ESCALERA')]/..")
            logger.info(f"Elementos con 'ESCALERA': {len(escalera_elements)}")
            for idx, elem in enumerate(escalera_elements):
                tag = await elem.evaluate("el => el.tagName")
                text = await elem.text_content()
                outer = await elem.evaluate("el => el.outerHTML.substring(0, 200)")
                logger.info(f"  [{idx}] Tag='{tag}' | Texto='{text}' | HTML: {outer}...")
        except Exception as e:
            logger.warning(f"No se pudo inspeccionar elementos ESCALERA: {e}")
        
        logger.info("\n" + "="*70)
        logger.info("👆 INSTRUCCIONES:")
        logger.info("="*70)
        logger.info("1. Mira el navegador que se abrió")
        logger.info("2. Haz CLICK en el botón de empresa 'ESCALERA DIAZ...'")
        logger.info("3. Dime cuál fue:")
        logger.info("   - ¿Era un botón azul?")
        logger.info("   - ¿Qué texto exacto había?")
        logger.info("   - ¿Qué sucedió después de clickearlo?")
        logger.info("="*70 + "\n")
        
        # Esperar al usuario
        logger.info("⏳ Esperando tu interacción manual... (Ctrl+C para cancelar)")
        while True:
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        logger.info("\nDepuración cancelada por usuario")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await bot.cerrar()


if __name__ == "__main__":
    asyncio.run(debug_empresa_selection())
