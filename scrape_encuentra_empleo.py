"""
scrape_encuentra_empleo.py
Script para verificar sesión en ENCUENTRA EMPLEO
y buscar vacantes usando Playwright + JSESSIONID proporcionado.
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Configuración
BASE_URL = "https://encuentraempleo.trabajo.gob.ec/socioEmpleo-war/paginas/aspirante/inicioAspirante.jsf"
JSESSIONID = "65a548f6769a5f34c8d0a612b95f"
DOMAIN = "encuentraempleo.trabajo.gob.ec"
OUTPUT_DIR = Path(__file__).parent / "screenshots"
OUTPUT_DIR.mkdir(exist_ok=True)


async def main():
    async with async_playwright() as p:
        # Lanzar navegador con contexto persistente para mantener cookies
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        # Establecer cookie JSESSIONID manualmente
        await context.add_cookies([
            {
                "name": "JSESSIONID",
                "value": JSESSIONID,
                "domain": DOMAIN,
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "Strict",
            }
        ])

        page = await context.new_page()

        print(f"[*] Navegando a: {BASE_URL}")
        try:
            response = await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
            print(f"[*] Status HTTP: {response.status}")

            # Capturar screenshot
            screenshot_path = OUTPUT_DIR / "encuentra_empleo_home.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"[*] Screenshot guardado: {screenshot_path}")

            # Extraer contenido textual visible
            body_text = await page.evaluate("document.body.innerText")
            print("\n--- CONTENIDO DE LA PÁGINA (primeros 3000 chars) ---")
            print(body_text[:3000])
            print("--- FIN ---\n")

            # Verificar indicadores de sesión inválida
            invalid_keywords = ["sesión", "iniciar sesión", "login", "autenticación", "no autorizado"]
            body_lower = body_text.lower()
            is_invalid = any(kw in body_lower for kw in invalid_keywords)

            if is_invalid:
                print("[!] ADVERTENCIA: La página podría indicar sesión inválida o requerir autenticación.")
            else:
                print("[+] La página cargó contenido; verificar manualmente el screenshot.")

            # Intentar buscar elementos que indiquen ofertas laborales
            vacancy_keywords = ["vacante", "oferta", "postular", "empleo", "desarrollador", "soporte", "analista"]
            found_vacancies = [kw for kw in vacancy_keywords if kw in body_lower]
            if found_vacancies:
                print(f"[+] Posibles secciones de vacantes detectadas: {found_vacancies}")
            else:
                print("[-] No se detectaron palabras clave de vacantes en el home.")

            # Buscar enlaces que podrían llevar a ofertas
            links = await page.eval_on_selector_all("a[href]", "els => els.map(e => ({text: e.innerText.trim(), href: e.href}))")
            relevant_links = [l for l in links if any(kw in (l.get("text") or "").lower() for kw in vacancy_keywords)]
            if relevant_links:
                print(f"[+] Enlaces relevantes encontrados ({len(relevant_links)}):")
                for l in relevant_links[:15]:
                    print(f"    • {l['text']} -> {l['href']}")
            else:
                print("[-] No se encontraron enlaces obvios a vacantes en el home.")

        except Exception as e:
            print(f"[ERROR] Fallo al navegar: {e}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
