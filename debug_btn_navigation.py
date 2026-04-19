#!/usr/bin/env python3
"""
Debug: Verificar si el click causa navegación o cambio de página
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD, HEADLESS

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()
        
        # Escuchar cambios de navegación
        async def on_response(response):
            print(f"  Response: {response.status} {response.url}")
        
        page.on("response", on_response)
        
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
        
        print(f"\nAntes del click - URL: {page.url}")
        print(f"Antes del click - Title: {await page.title()}")
        
        # Click EMITIR FACTURA con monitoreo
        print("\nClickeando EMITIR FACTURA...")
        boton = await page.query_selector("#bBtn1")
        if boton:
            # Intentar clickear con wait_for_navigation
            try:
                print("  Esperando navegación con timeout...")
                async with page.expect_navigation(timeout=5000):
                    await boton.click()
                print("  NAVEGACIÓN DETECTADA!")
            except:
                print("  No hubo navegación (timeout)")
        
        # Esperar un poco  
        await asyncio.sleep(2)
        
        print(f"\nDespués del click - URL: {page.url}")
        print(f"Después del click - Title: {await page.title()}")
        
        # Ver si hay algún elemento nuevo visible
        print("\n=== Buscar elementos nuevos o visibles ===")
        
        # Buscar divs con formulario
        forms = await page.query_selector_all("form")
        print(f"Formas: {len(forms)}")
        
        # Buscar divs grandes que podrían contener el formulario
        all_divs = await page.query_selector_all("div[style*='display'], div[role='dialog'], div[class*='form']")
        print(f"Divs potenciales: {len(all_divs)}")
        
        # Listar todas las URLs en la página que podrían ser links a formulario
        links = await page.query_selector_all("a")
        print(f"\n=== LINKS EN LA PÁGINA ({len(links)} total) ===")
        for i, link in enumerate(links[:10]):
            href = await link.get_attribute("href")
            text = await link.text_content()
            if 'factura' in text.lower() or 'generar' in text.lower() or 'emitir' in text.lower():
                print(f"  {i}: {href} - {text.strip()[:50]}")
        
        # Intentar método alternativo: ejecutar __doPostBack directamente
        print("\n=== Intentando llamar __doPostBack directamente ===")
        try:
            result = await page.evaluate("""
                () => {
                    console.log("Calling __doPostBack");
                    if (typeof __doPostBack === 'function') {
                        __doPostBack('ctl00$ContentPlaceHolder1$tFacElectronica$bBtn1', '');
                        return "postback_called";
                    } else {
                        return "postback_not_found";
                    }
                }
            """)
            print(f"  Resultado: {result}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Esperar y screenshot final
        await asyncio.sleep(3)
        await page.screenshot(path="debug_btn_click_result.png")
        print("\nScreenshot: debug_btn_click_result.png")
        
        # Fin
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
