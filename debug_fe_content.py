#!/usr/bin/env python3
"""
Test: Verificar contenido de fe.afip.gob.ar
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
        await asyncio.sleep(5)
        
        # Navegar a FE
        print("\nNavegando a fe.afip.gob.ar/rcel/jsp/index_bis.jsp...")
        await page.goto("https://fe.afip.gob.ar/rcel/jsp/index_bis.jsp", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        print(f"URL: {page.url}")
        
        # Ver todo el texto
        body = await page.query_selector("body")
        text = await body.text_content()
        
        print(f"Texto en página ({len(text)} chars):")
        print(text[:1000])
        
        # Buscar botón con id=idcontribuyente
        print("\n=== BUSCANDO BOTÓN ===")
        btn = await page.query_selector("button[id='idcontribuyente']")
        if btn:
            print("Encontrado button[id='idcontribuyente']")
        else:
            print("No encontrado button")
            
        # Buscar input
        inp = await page.query_selector("input[id='idcontribuyente']")
        if inp:
            print("Encontrado input[id='idcontribuyente']")
            inp_type = await inp.get_attribute("type")
            print(f"  type: {inp_type}")
        else:
            print("No encontrado input")
        
        # Buscar por texto ESCALERA
        element = await page.query_selector("text=ESCALERA")
        if element:
            print("Encontrado elemento con 'ESCALERA'")
        
        # Screenshot
        await page.screenshot(path="debug_fe_page.png")
        print("\nScreenshot: debug_fe_page.png")
        
        # Listar todos los elementos clickeables
        print("\n=== BOTONES/INPUTS CLICKEABLES ===")
        buttons = await page.query_selector_all("button")
        print(f"Botones: {len(buttons)}")
        for i, btn in enumerate(buttons[:5]):
            btn_id = await btn.get_attribute("id")
            text = await btn.text_content()
            print(f"  {i}: id={btn_id}, text={text.strip()[:40]}")
        
        inputs_clickeables = await page.query_selector_all("input[type='button'], input[type='submit']")
        print(f"Inputs tipo button/submit: {len(inputs_clickeables)}")
        for i, inp in enumerate(inputs_clickeables[:5]):
            inp_id = await inp.get_attribute("id")
            inp_value = await inp.get_attribute("value")
            print(f"  {i}: id={inp_id}, value={inp_value}")
        
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
