#!/usr/bin/env python3
"""
Debug: Ver qué página se carga después del login
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD, HEADLESS

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()
        
        print("1. Navegando a login...")
        await page.goto("https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono", wait_until="networkidle")
        print(f"   URL después de goto: {page.url}")
        
        # CUIT
        print("2. Ingresando CUIT...")
        cuit_input = await page.query_selector("input[type='text']")
        if cuit_input:
            await cuit_input.fill(AFIP_CUIT)
        
        # Click Siguiente
        print("3. Clickeando Siguiente...")
        try:
            await page.click("text=Siguiente", timeout=3000)
        except:
            await page.click("button[type='submit']")
        
        await asyncio.sleep(2)
        print(f"   URL después de Siguiente: {page.url}")
        
        # Password
        print("4. Ingresando contraseña...")
        password_input = await page.query_selector("input[type='password']")
        if password_input:
            await password_input.fill(AFIP_PASSWORD)
        
        # Click Ingresar
        print("5. Clickeando Ingresar...")
        for selector in ["text=Ingresar", "input[type='submit']", "text=Confirmar"]:
            try:
                await page.click(selector, timeout=3000)
                break
            except:
                continue
        
        await asyncio.sleep(3)
        print(f"   URL después de login: {page.url}")
        
        # Tomar screenshot
        await page.screenshot(path="debug_afterlogin.png")
        print("   Screenshot guardado: debug_afterlogin.png")
        
        # Esperar a ver qué hay
        print("\n6. Esperando 5 segundos para ver si redireccionan...")
        await asyncio.sleep(5)
        
        print(f"   URL después de esperar: {page.url}")
        
        # Buscar elemento 'Generar comprobantes'
        print("\n7. Buscando 'Generar comprobantes'...")
        
        selectors_to_try = [
            "text=Generar comprobantes",
            "text=GENERAR COMPROBANTES",
            "a:has-text('Generar')",
            "button:has-text('comprobantes')",
            "a",
            "button"
        ]
        
        for selector in selectors_to_try:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"   Encontrado {len(elements)} elemento(s) con '{selector}'")
                if selector in ["a", "button"]:
                    for elem in elements[:5]:  # Show first 5
                        text = await elem.text_content()
                        href = await elem.get_attribute("href") if selector == "a" else None
                        print(f"      - {text.strip()[:50]}" + (f" (href: {href})" if href else ""))
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
