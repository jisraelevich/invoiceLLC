#!/usr/bin/env python3
"""
Debug: Inspeccionar Virtual Keyboard
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Navegando a login...")
        await page.goto("https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono", wait_until="domcontentloaded")
        await asyncio.sleep(1)
        
        # Llenar CUIT
        print("Llenando CUIT...")
        await page.fill("input[id='F1:username']", AFIP_CUIT)
        
        # Click Siguiente
        print("Click Siguiente...")
        await page.click("input[id='F1:btnSiguiente']")
        await asyncio.sleep(2)
        
        # Ver HTML para encontrar virtual keyboard
        html = await page.content()
        
        # Buscar elementos del teclado virtual
        print("\n=== Buscando Virtual Keyboard ===")
        lines = html.split('\n')
        for i, line in enumerate(lines):
            if 'teclado' in line.lower() or 'keyboard' in line.lower() or 'F1:password' in line:
                print(f"Línea {i}: {line[:200]}")
        
        # Listar todos los inputs en la página
        print("\n=== TODOS LOS INPUTS ===")
        inputs = await page.query_selector_all("input")
        for inp in inputs:
            inp_id = await inp.get_attribute("id")
            inp_type = await inp.get_attribute("type")
            inp_name = await inp.get_attribute("name")
            print(f"Input: id={inp_id}, type={inp_type}, name={inp_name}")
        
        # Listar todos los botones
        print("\n=== TODOS LOS BOTONES ===")
        buttons = await page.query_selector_all("button")
        for btn in buttons[:10]:
            text = await btn.text_content()
            btn_id = await btn.get_attribute("id")
            print(f"Button: id={btn_id}, text={text.strip()[:50]}")
        
        # Esperar para ver la página
        print("\nPantalla visible 10 segundos...")
        await asyncio.sleep(10)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
