#!/usr/bin/env python3
"""
Test: Intentar navegar a fe.afip.gob.ar después del login Monotributo
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD, HEADLESS

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()
        
        # Login
        print("Realizando login en Monotributo...")
        await page.goto("https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono", wait_until="domcontentloaded")
        await asyncio.sleep(1)
        
        await page.fill("input[id='F1:username']", AFIP_CUIT)
        await page.click("input[id='F1:btnSiguiente']")
        await asyncio.sleep(2)
        
        await page.fill("input[id='F1:password']", AFIP_PASSWORD)
        await page.click("input[id='F1:btnIngresar']")
        await asyncio.sleep(5)
        
        print(f"Login completado, URL: {page.url}")
        
        # Intentar navegación a FE
        print("\nIntentando navegar a fe.afip.gob.ar...")
        try:
            await page.goto("https://fe.afip.gob.ar/rcel/jsp/index_bis.jsp", wait_until="domcontentloaded")
            print(f"Navegación exitosa, URL: {page.url}")
            
            # Ver si hay algo en la página
            text = await page.text_content()
            print(f"Contenido disponible: {len(text)} caracteres")
            
            if "Forbidden" in text or "403" in text:
                print("ERROR: Acceso denegado (403 Forbidden)")
            elif "Seleccione" in text or "empresa" in text.lower():
                print("OK: Página de selección de empresa cargada!")
            else:
                # Listar primeras líneas
                lines = text.split('\n')[:10]
                print("Primeras líneas:")
                for line in lines:
                    if line.strip():
                        print(f"  {line.strip()[:80]}")
                        
            await page.screenshot(path="debug_fe_afterlogin.png")
            print("Screenshot: debug_fe_afterlogin.png")
            
        except Exception as e:
            print(f"ERROR: {e}")
        
        # También intentar otros points de entrada
        print("\nIntentando fe.afip.gob.ar/rcel/jsp/menu_ppal.jsp...")
        try:
            await page.goto("https://fe.afip.gob.ar/rcel/jsp/menu_ppal.jsp", wait_until="domcontentloaded")
            print(f"URL: {page.url}")
            text = await page.text_content()
            if "Forbidden" not in text:
                print("OK: Página cargada!")
            else:
                print("ERROR: 403 Forbidden")
        except Exception as e:
            print(f"ERROR: {e}")
        
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
