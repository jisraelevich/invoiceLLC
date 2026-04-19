#!/usr/bin/env python3
"""
Debug: Ver qué cambió en la página después del postback
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD, HEADLESS

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()
        
        # Login
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
        
        # Obtener HTML antes
        html_antes = await page.content()
        print(f"\nHTML antes de click: {len(html_antes)} bytes")
        
        # Buscar formulario de factura antes
        if "generar" in html_antes.lower():
            print("  - Encontrado 'generar' en HTML")
        if "factura" in html_antes.lower():
            print("  - Encontrado 'factura' en HTML")
        if "submit" in html_antes.lower():
            print("  - Encontrado 'submit' en HTML")
        
        # Click EMITIR FACTURA
        print("\nClickeando EMITIR FACTURA...")
        boton = await page.query_selector("text=EMITIR FACTURA")
        if boton:
            await boton.click()
        
        # Esperar varios tipos de load states
        print("Esperando loadstate: domcontentloaded...")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=10000)
        except:
            print("  (timeout)")
        
        print("Esperando loadstate: load...")
        try:
            await page.wait_for_load_state("load", timeout=10000)
        except:
            print("  (timeout)")
        
        # Obtener HTML después
        html_despues = await page.content()
        print(f"\nHTML después de click: {len(html_despues)} bytes")
        
        if html_antes == html_despues:
            print("HTML es IDÉNTICO - postback no ocurrió o fue inútil")
        else:
            print(f"HTML CAMBIÓ ({len(html_despues) - len(html_antes):+d} bytes)")
            
            # Mostrar cambios
            lines_antes = html_antes.split('\n')
            lines_despues = html_despues.split('\n')
            
            print(f"  Líneas antes: {len(lines_antes)}, Líneas después: {len(lines_despues)}")
        
        # Buscar formulario/campos después
        print("\nBuscando elementos después del click:")
        
        # Forms
        forms = await page.query_selector_all("form")
        print(f"  Forms: {len(forms)}")
        
        # Inputs (no hidden)
        inputs = await page.query_selector_all("input:not([type='hidden'])")
        print(f"  Inputs (visible): {len(inputs)}")
        
        for i, inp in enumerate(inputs[:5]):
            inp_type = await inp.get_attribute("type")
            inp_name = await inp.get_attribute("name")
            placeholder = await inp.get_attribute("placeholder")
            label = None
            try:
                # Ver si hay label asociado
                inp_id = await inp.get_attribute("id")
                if inp_id:
                    label = await page.locator(f"label[for='{inp_id}']").text_content()
            except:
                pass
            
            print(f"    Input {i}: type={inp_type}, name={inp_name}, placeholder={placeholder}, label={label}")
        
        # Textareas
        textareas = await page.query_selector_all("textarea")
        print(f"  Textareas: {len(textareas)}")
        
        # Buttons
        buttons = await page.query_selector_all("button")
        print(f"  Buttons: {len(buttons)}")
        for i, btn in enumerate(buttons[:3]):
            text = await btn.text_content()
            print(f"    Button {i}: {text.strip()[:50]}")
        
        # Selects
        selects = await page.query_selector_all("select")
        print(f"  Selects: {len(selects)}")
        
        # Scroll para ver si hay más contenido
        print("\nScrolleando página...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await page.screenshot(path="debug_scroll_final.png")
        
        print("\nScreenshot: debug_scroll_final.png")
        
        await asyncio.sleep(3)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
