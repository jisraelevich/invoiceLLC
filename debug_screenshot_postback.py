#!/usr/bin/env python3
"""
Debug: Screenshot inmediato después del postback
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
        
        # Screenshot antes
        await page.screenshot(path="debug_facturacion_antes.png")
        print("Screenshot facturación (antes): debug_facturacion_antes.png")
        
        # Click EMITIR FACTURA
        print("\nClickeando EMITIR FACTURA...")
        boton = await page.query_selector("text=EMITIR FACTURA")
        await boton.click()
        
        # Esperar
        await asyncio.sleep(3)
        
        # Screenshot después
        await page.screenshot(path="debug_facturacion_despues.png")
        print("Screenshot facturación (después): debug_facturacion_despues.png")
        
        # URL
        print(f"URL después: {page.url}")
        
        # Ver si hay algún modal o dialog
        modals = await page.query_selector_all("[role='dialog'], [role='alertdialog'], .modal, .dialog, .popup")
        print(f"Elementos tipo diálogo encontrados: {len(modals)}")
        
        # Buscar iframes
        iframes = await page.query_selector_all("iframe")
        print(f"Iframes encontrados: {len(iframes)}")
        
        # Buscar divs con contenido dinámico
        divs = await page.query_selector_all("div[id*='pnl'], div[id*='modal'], div[id*='dialog']")
        print(f"Divs con id modal/dialog: {len(divs)}")
        
        # Ver el main content
        main_content = await page.query_selector("#page-content, main, [role='main']")
        if main_content:
            content_html = await main_content.evaluate("el => el.outerHTML")
            print(f"\nContenido HTML (primeros 500 chars):\n{content_html[:500]}")
        
        # Listar todos los elementos visibles
        body = await page.query_selector("body")
        if body:
            all_text = await body.text_content()
            print(f"\nTexto visible en página ({len(all_text)} chars):")
            # Print lines that might be a form
            for line in all_text.split('\n'):
                line = line.strip()
                if line and ('fecha' in line.lower() or 'factura' in line.lower() or 'cliente' in line.lower() or 'monto' in line.lower()):
                    print(f"  - {line[:100]}")
        
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
