import asyncio
from playwright.async_api import async_playwright
import os
import json

# Domain for cookies
DOMAIN = "encuentraempleo.trabajo.gob.ec"
URL = f"https://{DOMAIN}/socioEmpleo-war/paginas/aspirante/busquedaOferta.jsf"

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(SCRIPT_DIR, "config", "cookies.json")

# Arc CDP endpoint (default when Arc is running with --remote-debugging-port=9222)
CDP_ENDPOINT = "http://localhost:9222"

async def get_cookies_from_arc():
    """Connect to Arc via CDP and extract fresh cookies."""
    async with async_playwright() as p:
        print(f"Connecting to Arc via CDP at {CDP_ENDPOINT}...")
        try:
            browser = await p.chromium.connect_over_cdp(CDP_ENDPOINT)
            print("✅ Connected to Arc!")
            
            # Find the context with the Encuentra Empleo tab
            contexts = browser.contexts
            target_context = None
            target_page = None
            
            for ctx in contexts:
                pages = ctx.pages
                for page in pages:
                    try:
                        url = page.url
                        if DOMAIN in url:
                            target_context = ctx
                            target_page = page
                            print(f"Found Encuentra Empleo tab: {url}")
                            break
                    except:
                        pass
                if target_context:
                    break
            
            if not target_context:
                print("❌ No Encuentra Empleo tab found in Arc.")
                print("Please open https://encuentraempleo.trabajo.gob.ec in Arc and log in.")
                await browser.close()
                return False
            
            # Navigate to the job search page if not already there
            if "busquedaOferta.jsf" not in target_page.url:
                print("Navigating to busquedaOferta.jsf...")
                await target_page.goto(URL, timeout=40000)
                await target_page.wait_for_timeout(3000)
            
            # Check if we're on the right page (not redirected to login)
            if "index.jsf" in target_page.url and "busquedaOferta.jsf" not in target_page.url:
                print("❌ Session expired - redirected to login page.")
                print("Please log in manually in Arc, then run this script again.")
                await browser.close()
                return False
            
            # Extract cookies
            print("Extracting cookies...")
            cookies = await target_context.cookies()
            
            jsessionid = None
            nsc = None
            for cookie in cookies:
                if cookie["name"] == "JSESSIONID" and DOMAIN in cookie["domain"]:
                    jsessionid = cookie["value"]
                elif cookie["name"] == "NSC_JOmnkwatc53jecrcfmkoaierrq1sab2":
                    nsc = cookie["value"]
            
            if not jsessionid:
                print("❌ JSESSIONID not found in cookies.")
                await browser.close()
                return False
            
            print(f"✅ JSESSIONID: {jsessionid[:20]}...")
            print(f"✅ NSC: {nsc[:20] if nsc else 'Not found'}...")
            
            # Save cookies
            cookie_data = {
                "JSESSIONID": jsessionid,
                "NSC_JOmnkwatc53jecrcfmkoaierrq1sab2": nsc or ""
            }
            
            with open(COOKIES_PATH, "w", encoding="utf-8") as f:
                json.dump(cookie_data, f, indent=2)
            
            print(f"✅ Fresh cookies saved to {COOKIES_PATH}")
            await browser.close()
            return True
            
        except Exception as e:
            print(f"❌ CDP connection error: {e}")
            print("Make sure Arc is running with --remote-debugging-port=9222")
            return False

if __name__ == "__main__":
    print("=== Extracting cookies from Arc via CDP ===")
    print("Prerequisite: Arc must be running with --remote-debugging-port=9222")
    print("Run: /Applications/Arc.app/Contents/MacOS/Arc --remote-debugging-port=9222")
    print()
    asyncio.run(get_cookies_from_arc())