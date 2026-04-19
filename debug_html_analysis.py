#!/usr/bin/env python3
"""
Debug: Buscar elementos de formulario en HTML después del postback
"""
import asyncio
import re
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
        
        # HTML antes
        html_antes = await page.content()
        
        # Click EMITIR FACTURA
        print("Clickeando EMITIR FACTURA...")
        boton = await page.query_selector("text=EMITIR FACTURA")
        await boton.click()
        
        # Esperar (aumentar tiempo de espera)
        print("Esperando 5 segundos...")
        await asyncio.sleep(5)
        
        # HTML después
        html_despues = await page.content()
        
        # Mostrar cambios importantes
        print(f"\n=== HTML CAMBIOS ===")
        print(f"HTML antes: {len(html_antes)} bytes")
        print(f"HTML después: {len(html_despues)} bytes")
        print(f"Diferencia: +{len(html_despues) - len(html_antes)} bytes")
        
        # Buscar agregaciones en el HTML
        changes = []
        
        # Buscar palabras clave que aparecieron
        keywords = ['form', 'input', 'fecha', 'cliente', 'cantidad', 'precio', 'monto', 'comprobante', 'factura', 'valor', 'detalle']
        
        for kw in keywords:
            count_antes = len(re.findall(kw, html_antes, re.IGNORECASE))
            count_despues = len(re.findall(kw, html_despues, re.IGNORECASE))
            if count_antes != count_despues:
                changes.append(f"  '{kw}': {count_antes} -> {count_despues} (delta: +{count_despues - count_antes})")
        
        if changes:
            print("\nCambios en palabras clave:")
            for change in changes:
                print(change)
        
        # Buscar secciones nuevas
        print("\n=== NUEVOS ELEMENTOS ===")
        
        # Buscar por patrón <div con id
        antes_divs = set(re.findall(r'<div[^>]*id=["\']([^"\']+)["\']', html_antes))
        despues_divs = set(re.findall(r'<div[^>]*id=["\']([^"\']+)["\']', html_despues))
        
        nuevos_divs = despues_divs - antes_divs
        print(f"Nuevos DIVs: {len(nuevos_divs)}")
        for div_id in list(nuevos_divs)[:5]:
            print(f"  - {div_id}")
        
        # elementos con role
        antes_roles = set(re.findall(r'role=["\']([^"\']*)["\']', html_antes))
        despues_roles = set(re.findall(r'role=["\']([^"\']*)["\']', html_despues))
        
        nuevos_roles = despues_roles - antes_roles
        print(f"\nNuevos roles: {len(nuevos_roles)}")
        for role in nuevos_roles:
            print(f"  - {role}")
        
        # Ver todo el body como texto plano para encontrar el contenido
        body_text = await page.locator("body").text_content()
        
        # Buscar líneas potencialmente relevantes
        print("\n=== CONTENIDO DE TEXTO (primeras líneas relevantes) ===")
        for line in body_text.split('\n')[:100]:
            line = line.strip()
            if line and len(line) > 5 and (
                'factura' in line.lower() or 
                'fecha' in line.lower() or 
                'cliente' in line.lower() or 
                'cantidad' in line.lower() or
                'artículo' in line.lower() or
                'descripción' in line.lower() or
                'importe' in line.lower()
            ):
                print(f"  {line[:100]}")
        
        # Finalmente, contar elementos totales
        print(f"\n=== ESTADÍSTICAS ===")
        inputs = await page.query_selector_all("input")
        outputs = await page.query_selector_all("output")
        labels = await page.query_selector_all("label")
        buttons = await page.query_selector_all("button")
        
        print(f"Inputs: {len(inputs)}")
        print(f"Outputs: {len(outputs)}")
        print(f"Labels: {len(labels)}")
        print(f"Buttons: {len(buttons)}")
        
        # Esperar visualmente
        print("\nSelecciones completadas observa el navegador por 10 segundos...")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
