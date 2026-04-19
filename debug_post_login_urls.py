#!/usr/bin/env python3
"""
Quick test: Ver a dónde llegamos después del login
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
        
        print(f"\nURL después del login: {page.url}")
        
        # Buscar links a /rcel/jsp/ o facturación
        links = await page.query_selector_all("a")
        print(f"\n=== LINKS QUE CONTIENEN 'rcel' O 'factura' ===")
        for link in links:
            href = await link.get_attribute("href")
            text = await link.text_content()
            if href and ('rcel' in href.lower() or 'factura' in href.lower() or 'comproban' in href.lower()):
                print(f"  {href} -> {text.strip()[:60]}")
        
        # Listar todos los links para ver la estructura
        print(f"\n=== TODOS LOS LINKS ({len(links)} total) ===")
        for i, link in enumerate(links[:20]):
            href = await link.get_attribute("href")
            text = await link.text_content()
            print(f"  {i}: {href} -> {text.strip()[:40]}")
        
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
