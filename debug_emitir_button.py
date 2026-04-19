#!/usr/bin/env python3
"""
Debug: Investigar por qué EMITIR FACTURA no funciona
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD, HEADLESS

async def login_to_facturacion(page):
    """Login y navega a Facturación"""
    # Login
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
    
    print(f"URL actual: {page.url}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()
        
        print("Navegando al login...")
        await login_to_facturacion(page)
        
        # Inspeccionar botón EMITIR FACTURA
        print("\n=== Inspeccionando botón EMITIR FACTURA ===")
        
        botones = await page.query_selector_all("text=EMITIR FACTURA")
        print(f"Encontrados {len(botones)} botones con 'EMITIR FACTURA'")
        
        if botones:
            boton = botones[0]
            
            # Ver propiedades del botón
            boton_html = await boton.evaluate("el => el.outerHTML")
            print(f"\nHTML del botón:\n{boton_html[:500]}")
            
            # Ver si tiene href
            href = await boton.get_attribute("href")
            print(f"\nhref: {href}")
            
            # Ver si es clickable
            is_visible = await boton.is_visible()
            is_enabled = await boton.is_enabled()
            print(f"\nVisible: {is_visible}, Enabled: {is_enabled}")
            
            # Ver padre del botón
            parent_html = await boton.evaluate("el => el.parentElement?.outerHTML")
            print(f"\nHTML del padre:\n{parent_html[:500] if parent_html else 'N/A'}")
            
            # Intentar 3 métodos diferentes de click
            print("\n=== Probando métodos de click ===")
            
            # Método 1: Click normal
            print("\n1. Click normal...")
            await page.screenshot(path="debug_antes_click.png")
            try:
                await boton.click()
                await asyncio.sleep(2)
                await page.screenshot(path="debug_despues_click1.png")
                print(f"   URL luego de click: {page.url}")
            except Exception as e:
                print(f"   Error: {e}")
            
            # Método 2: Si tiene href, usar goto
            if href:
                print(f"\n2. Navegación directa a href: {href}")
                await page.goto(href, wait_until="domcontentloaded")
                await asyncio.sleep(2)
                await page.screenshot(path="debug_goto_href.png")
                print(f"   URL luego de goto: {page.url}")
            
            # Método 3: Usar evaluate para ejecutar JavaScript
            print("\n3. Ejecutar JavaScript del botón...")
            try:
                onclick = await boton.evaluate("el => el.onclick?.toString() || el.getAttribute('onclick')")
                print(f"   onclick: {onclick[:200] if onclick else 'N/A'}")
            except:
                pass
            
            # Ver si es un link simulado
            click_handler = await boton.evaluate("el => el.getAttribute('onclick')")
            print(f"   onclick attribute: {click_handler}")
        
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
