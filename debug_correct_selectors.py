#!/usr/bin/env python3
"""
Debug: Login usando los selectores correctos
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"CUIT: {AFIP_CUIT}")
        print(f"PASSWORD: {AFIP_PASSWORD[:5]}***\n")
        
        print("1. Navegando a login...")
        await page.goto("https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono", wait_until="domcontentloaded")
        await asyncio.sleep(1)
        
        print("2. Llenando CUIT usando input[id='F1:username']...")
        await page.fill("input[id='F1:username']", AFIP_CUIT)
        valor = await page.input_value("input[id='F1:username']")
        print(f"   Valor ingresado: {valor}")
        
        print("3. Clickeando input[id='F1:btnSiguiente']...")
        await page.click("input[id='F1:btnSiguiente']")
        
        print("4. Esperando cambio de página (3 segundos)...")
        await asyncio.sleep(3)
        
        await page.screenshot(path="debug_password_page.png")
        print("   Screenshot: debug_password_page.png")
        print(f"   URL: {page.url}")
        
        # Ver si llegamos a password
        password_input = await page.query_selector("input[type='password']")
        if password_input:
            print("   ✓ Vemos input de password")
            print("\n5. Llenando password...")
            await password_input.fill(AFIP_PASSWORD)
            
            # Buscar botón de envío
            print("6. Clickeando botón de envío...")
            submit_buttons = [
                "text=Ingresar",
                "input[id='F1:btnIngresar']",
                "input[type='submit']",
                "button[type='submit']"
            ]
            
            for selector in submit_buttons:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        print(f"   Encontrado botón: {selector}")
                        await elem.click()
                        break
                except:
                    pass
            
            print("7. Esperando después de submit (5 segundos)...")
            await asyncio.sleep(5)
            
            await page.screenshot(path="debug_after_password.png")
            print("   Screenshot: debug_after_password.png")
            print(f"   URL: {page.url}")
        else:
            print("   ❌ No encontramos input de password")
            # Ver HTML para debuggear
            html = await page.content()
            if "incorrecto" in html.lower():
                print("   ⚠️  Vemos 'incorrecto' - CUIT rechazado")
        
        await asyncio.sleep(3)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
