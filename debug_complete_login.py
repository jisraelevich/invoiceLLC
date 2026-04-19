#!/usr/bin/env python3
"""
Debug: Test complete login flow including error detection
"""
import asyncio
from playwright.async_api import async_playwright
from config import AFIP_CUIT, AFIP_PASSWORD

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"\nTesting AFIP Login")
        print(f"CUIT: {AFIP_CUIT}")
        print(f"PASSWORD: {AFIP_PASSWORD[:3]}***\n")
        
        try:
            # Step 1: CUIT
            print("1. Navigating to login...")
            await page.goto("https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=admin_mono", wait_until="domcontentloaded")
            
            print("2. Entering CUIT...")
            await page.fill("input[id='F1:username']", AFIP_CUIT)
            print("   ✓ CUIT entered")
            
            print("3. Clicking 'Siguiente'...")
            await page.click("input[id='F1:btnSiguiente']")
            print("   ✓ Clicked")
            
            await asyncio.sleep(2)
            
            # Step 2: Password
            print("4. Checking for password field...")
            password_input = await page.query_selector("input[id='F1:password']")
            if not password_input:
                print("   ❌ Password field not found!")
                html = await page.content()
                if "incorrecto" in html.lower():
                    print("   ERROR: CUIT was rejected as 'incorrecto'")
                await page.screenshot(path="debug_nopassword.png")
                return
            
            print("   ✓ Password field found")
            
            print("5. Entering password...")
            await page.fill("input[id='F1:password']", AFIP_PASSWORD)
            print("   ✓ Password entered")
            
            await asyncio.sleep(1)
            
            print("6. Clicking 'Ingresar'...")
            await page.click("input[id='F1:btnIngresar']")
            print("   ✓ Clicked")
            
            print("7. Waiting for response (5 seconds)...")
            await asyncio.sleep(5)
            
            # Check response
            current_url = page.url
            print(f"\n   Current URL: {current_url}")
            
            html = await page.content()
            
            # Check for errors
            if "incorrecto" in html.lower():
                print("   ❌ ERROR: 'incorrecto' found - password or CUIT wrong")
                await page.screenshot(path="debug_error_incorrecto.png")
                return
            
            if "login.xhtml" in current_url and "jsessionid" in current_url:
                print("   ⚠️  Still on login page - authentication failed")
                if "F1:password" in html:
                    print("      Password field still visible - likely credentials wrong")
                await page.screenshot(path="debug_still_on_login.png")
                return
            
            if "auth.afip.gov.ar" in current_url and "login" not in current_url:
                print("   ✓ Successfully logged in! (still on AFIP auth server)")
                await page.screenshot(path="debug_after_login_success.png")
                await asyncio.sleep(3)
                return
            
            # Generic success
            if "auth.afip.gov.ar" not in current_url:
                print("   ✓ Redirected away from login - SUCCESS!")
                await page.screenshot(path="debug_redirected.png")
                return
            
            print("   ? Unknown status - taking screenshot")
            await page.screenshot(path="debug_unknown.png")
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            await page.screenshot(path="debug_exception.png")
        
        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
