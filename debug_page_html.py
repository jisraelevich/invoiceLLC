#!/usr/bin/env python3
"""
Debug: Ver HTML de la página de login
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Navegando a login...")
        await page.goto("https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono", wait_until="domcontentloaded")
        
        print("Esperando 2 segundos...")
        await asyncio.sleep(2)
        
        # Tomar screenshot
        await page.screenshot(path="debug_page_load.png")
        print("Screenshot: debug_page_load.png")
        
        # Ver HTML
        html = await page.content()
        print("\n=== HTML CONTENT ===")
        # Buscar inputs
        lines = html.split('\n')
        for i, line in enumerate(lines):
            if 'input' in line.lower() or 'cuit' in line.lower():
                print(f"Línea {i}: {line[:150]}")
        
        # También buscar botones
        print("\n=== BOTONES ===")
        for i, line in enumerate(lines):
            if 'button' in line.lower() or 'siguiente' in line.lower():
                print(f"Línea {i}: {line[:150]}")
        
        # Esperar a que el usuario vea la página
        print("\nElementos encontrados. Presiona Ctrl+C para cerrar...")
        await asyncio.sleep(10)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
