#!/usr/bin/env python3
"""
Debug: Mejorado para login con esperas explícitas
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD, HEADLESS

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()
        
        print(f"CUIT a usar: {AFIP_CUIT}")
        print(f"PASSWORD: {AFIP_PASSWORD[:5]}***")
        
        print("\n1. Navegando a login...")
        await page.goto("https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono", wait_until="domcontentloaded")
        
        # Esperar a que el input de CUIT sea visible
        print("2. Esperando que el input de CUIT sea visible...")
        await page.wait_for_selector("input[type='text']", timeout=10000)
        
        # Obtener todos los inputs
        inputs = await page.query_selector_all("input[type='text']")
        print(f"   Encontrados {len(inputs)} input(s) de texto")
        
        # Llenar CUIT
        print(f"3. Llenando CUIT: {AFIP_CUIT}")
        cuit_input = await page.query_selector("input[type='text']")
        if cuit_input:
            await cuit_input.clear()
            await asyncio.sleep(0.5)
            await cuit_input.fill(AFIP_CUIT)
            await asyncio.sleep(0.5)
            valor = await cuit_input.input_value()
            print(f"   Valor en input: {valor}")
        
        # Screenshot antes de click
        await page.screenshot(path="debug_antes_siguiente.png")
        print("   Screenshot: debug_antes_siguiente.png")
        
        # Click Siguiente
        print("4. Clickeando 'Siguiente'...")
        button = await page.query_selector("text=Siguiente")
        if button:
            print("   Botón encontrado")
            await button.click()
            print("   Click ejecutado")
        else:
            print("   ERROR: Botón no encontrado")
        
        print("5. Esperando respuesta (3 segundos)...")
        await asyncio.sleep(3)
        
        # Screenshot después
        await page.screenshot(path="debug_despues_siguiente.png")
        print("   Screenshot: debug_despues_siguiente.png")
        print(f"   URL: {page.url}")
        
        # Ver si hay error
        try:
            error_element = await page.query_selector("text=incorrecto")
            if error_element:
                print("   ❌ ERROR: Vemos 'incorrecto' en la página")
        except:
            pass
        
        # Ver si pedimos password
        try:
            password_input = await page.query_selector("input[type='password']")
            if password_input:
                print("   ✓ Input de password encontrado - puede continuar")
        except:
            pass
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
