"""
Conecta a una instancia existente de Chrome via CDP
para obtener cookies de sesión activa de ENCUENTRA EMPLEO.
"""

import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://encuentraempleo.trabajo.gob.ec/socioEmpleo-war/paginas/aspirante/inicioAspirante.jsf"
TARGET_DOMAIN = "encuentraempleo.trabajo.gob.ec"


async def main():
    # Intentar conectar a Chrome en modo debug (puerto 9222)
    try:
        async with async_playwright() as p:
            # Conectar al navegador Chrome existente
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print(f"[+] Conectado a Chrome via CDP. Páginas abiertas: {len(browser.contexts[0].pages)}")

            # Buscar la página de ENCUENTRA EMPLEO
            target_page = None
            for page in browser.contexts[0].pages:
                if TARGET_DOMAIN in page.url:
                    target_page = page
                    break

            if target_page:
                print(f"[+] Página encontrada: {target_page.url}")
            else:
                print(f"[-] No se encontró una página abierta de {TARGET_DOMAIN}")
                print("[*] Abriendo la página en una nueva pestaña...")
                target_page = await browser.contexts[0].new_page()
                await target_page.goto(BASE_URL, wait_until="networkidle", timeout=30000)

            # Screenshot
            await target_page.screenshot(path="screenshots/encuentra_empleo_cdp.png", full_page=True)
            print("[*] Screenshot guardado: screenshots/encuentra_empleo_cdp.png")

            # Obtener cookies del dominio
            cookies = await target_page.context.cookies()
            target_cookies = [c for c in cookies if TARGET_DOMAIN in c.get("domain", "")]

            print(f"\n[+] Cookies de {TARGET_DOMAIN} ({len(target_cookies)} encontradas):")
            for c in target_cookies:
                print(f"    • {c['name']} = {c['value'][:50]}... (expira: {c.get('expires', 'sesión')})")

            # Contenido de la página
            body_text = await target_page.evaluate("document.body.innerText")
            print("\n--- CONTENIDO (primeros 3000 chars) ---")
            print(body_text[:3000])
            print("--- FIN ---\n")

            # Buscar enlaces a vacantes
            vacancy_keywords = ["vacante", "oferta", "postular", "empleo", "desarrollador", "soporte", "analista"]
            links = await target_page.eval_on_selector_all(
                "a[href]", "els => els.map(e => ({text: e.innerText.trim(), href: e.href}))"
            )
            relevant = [l for l in links if any(kw in (l.get("text") or "").lower() for kw in vacancy_keywords)]

            if relevant:
                print(f"[+] Enlaces relevantes ({len(relevant)}):")
                for l in relevant[:20]:
                    print(f"    • {l['text']} -> {l['href']}")

            # Verificar si hay sesión activa
            if any("usuario" in (await target_page.evaluate("document.body.innerText")).lower()[:500]):
                print("\n[+] Parece haber una sesión activa (se detectó 'usuario' en el contenido).")
            else:
                print("\n[-] No se detectó sesión de usuario activa.")

            print("\n[*] Script finalizado. Navegadorgexterno no se cierra (pertenece a tu Chrome).")

    except Exception as e:
        print(f"[ERROR] No se pudo conectar a Chrome en localhost:9222")
        print(f"   Detalle: {e}")
        print("\n[*] Solución: Cerrá todas las ventanas de Chrome y abrí una nueva con:")
        print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
        print("   Luego navegá a encuentraempleo.trabajo.gob.ec, iniciá sesión, y volvé a ejecutar este script.")


if __name__ == "__main__":
    asyncio.run(main())
