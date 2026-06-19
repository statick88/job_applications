"""
scrape_encuentra_empleo_with_profile.py
Usa el perfil de Chrome del usuario para mantener sesión autenticada
en ENCUENTRA EMPLEO (evita problemas de SSO/JSESSIONID).
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "https://encuentraempleo.trabajo.gob.ec/socioEmpleo-war/paginas/aspirante/inicioAspirante.jsf"
OUTPUT_DIR = Path(__file__).parent / "screenshots"
OUTPUT_DIR.mkdir(exist_ok=True)

# Ruta al perfil de Chrome en macOS
CHROME_PROFILE = Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default"


async def main():
    if not CHROME_PROFILE.exists():
        print(f"[ERROR] Perfil de Chrome no encontrado en: {CHROME_PROFILE}")
        print("   Verificá que Chrome esté instalado y tengas una sesión activa en encuentraempleo.trabajo.gob.ec")
        sys.exit(1)

    print(f"[*] Perfil Chrome detectado: {CHROME_PROFILE}")

    async with async_playwright() as p:
        # Lanzar Chrome con el perfil del usuario (persiste cookies)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=False,  # Mostrar Chrome para que veas la sesión cargada
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ],
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        # Obtener página existente o crear una
        if browser.pages:
            page = browser.pages[0]
        else:
            page = await browser.new_page()

        print(f"[*] Navegando a: {BASE_URL}")
        try:
            response = await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
            print(f"[*] Status HTTP: {response.status}")

            # Screenshot
            screenshot_path = OUTPUT_DIR / "encuentra_empleo_autenticado.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"[*] Screenshot guardado: {screenshot_path}")

            # Contenido
            body_text = await page.evaluate("document.body.innerText")
            print("\n--- CONTENIDO (primeros 3000 chars) ---")
            print(body_text[:3000])
            print("--- FIN ---\n")

            # Buscar enlaces a vacantes
            vacancy_keywords = ["vacante", "oferta", "postular", "empleo", "desarrollador", "soporte", "analista", "sistemas"]
            links = await page.eval_on_selector_all("a[href]", "els => els.map(e => ({text: e.innerText.trim(), href: e.href}))")
            relevant = [l for l in links if any(kw in (l.get("text") or "").lower() for kw in vacancy_keywords)]

            if relevant:
                print(f"[+] Enlaces relevantes ({len(relevant)}):")
                for l in relevant[:20]:
                    print(f"    • {l['text']} -> {l['href']}")
            else:
                print("[-] No se encontraron enlaces a vacantes en el home.")

            # Verificar si hay formularios de postulación
            forms = await page.eval_on_selector_all("form", "els => els.map(e => ({id: e.id, action: e.action, method: e.method}))")
            if forms:
                print(f"\n[+] Formularios detectados ({len(forms)}):")
                for f in forms[:10]:
                    print(f"    • id={f['id']} action={f['action']} method={f['method']}")

            print("\n[*] Navegador abierto. Cerralo manualmente cuando termines de revisar.")
            await asyncio.sleep(600)  # Mantener abierto 10 minutos

        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
