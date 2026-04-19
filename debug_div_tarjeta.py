#!/usr/bin/env python3
"""
Debug: Ver contenido exacto del divTarjeta
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD, HEADLESS

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()
        
        # Login y navegar a Facturación
        print("Realizando login...")
        await page.goto("https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono", wait_until="domcontentloaded")
        await asyncio.sleep(1)
        
        await page.fill("input[id='F1:username']", AFIP_CUIT)
        await page.click("input[id='F1:btnSiguiente']")
        await asyncio.sleep(2)
        
        await page.fill("input[id='F1:password']", AFIP_PASSWORD)
        await page.click("input[id='F1:btnIngresar']")
        await asyncio.sleep(3)
        
        # Click Facturación
        await page.click("text=Facturación")
        await asyncio.sleep(2)
        
        # Click EMITIR FACTURA
        print("Clickeando EMITIR FACTURA...")
        await page.click("#bBtn1")
        await asyncio.sleep(3)
        
        # Obtener contenido de divTarjeta
        div = await page.query_selector("#divTarjeta")
        if div:
            print("\n=== CONTENIDO DE divTarjeta ===")
            html = await div.evaluate("el => el.outerHTML")
            print(html)
            
            # Ver texto
            print("\n=== TEXTO DE divTarjeta ===")
            text = await div.text_content()
            print(text)
            
            # Ver hijos
            print("\n=== HIJOS DIRECTOS DE divTarjeta ===")
            hijos = await div.evaluate("el => Array.from(el.children).map(c => ({tag: c.tagName, class: c.className, id: c.id}))")
            for hijo in hijos:
                print(f"  {hijo}")
        
        # Ver si hay un iframe que se cargó
        iframes = await page.query_selector_all("iframe")
        print(f"\n=== iframes: {len(iframes)} ===")
        for i, iframe in enumerate(iframes):
            iframe_id = await iframe.get_attribute("id")
            iframe_name = await iframe.get_attribute("name")
            iframe_src = await iframe.get_attribute("src")
            print(f"  Iframe {i}: id={iframe_id}, name={iframe_name}, src={iframe_src}")
        
        # Ver si hay algún elemento oculto que debería ser visible
        print("\n=== ELEMENTOS CON display:none o visibility:hidden ===")
        hidden = await page.query_selector_all("[style*='display:none'], [style*='visibility:hidden']")
        print(f"Encontrados: {len(hidden)}")
        
        # Ver el árbol completo de main
        main = await page.query_selector("main")
        if main:
            main_html = await main.evaluate("el => el.outerHTML")
            print(f"\n=== MAIN HTML (primeros 2000 chars) ===")
            print(main_html[:2000])
        
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
