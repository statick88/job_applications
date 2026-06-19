"""
Script de postulación automática ISTPN - Fase 2: Navegación del dashboard
Conecta al navegador existente y navega el dashboard de postulaciones.
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PORTAL_URL = "https://postudoc.isupol.edu.ec/dashboard/postulacionesc"
OUTPUT_DIR = Path(__file__).parent / "screenshots"
OUTPUT_DIR.mkdir(exist_ok=True)


async def main():
    async with async_playwright() as p:
        try:
            # Conectar al navegador existente en modo debug
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("[+] Conectado al navegador existente")

            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()

            # Navegar al dashboard si no estamos ahí
            current_url = page.url
            print(f"[*] URL actual: {current_url}")

            if "postulacionesc" not in current_url:
                print(f"[*] Navegando al dashboard...")
                await page.goto(PORTAL_URL, wait_until="networkidle", timeout=30000)
            else:
                print("[+] Ya estamos en el dashboard")

            # Screenshot del dashboard
            await page.screenshot(path=str(OUTPUT_DIR / "istpn_dashboard_actual.png"), full_page=True)
            print(f"[*] Screenshot guardado: istpn_dashboard_actual.png")

            # Obtener contenido
            page_text = await page.evaluate("document.body.innerText")
            print("\n--- CONTENIDO DASHBOARD (primeros 3000 chars) ---")
            print(page_text[:3000])
            print("--- FIN ---\n")

            # Buscar botones/enlaces de postulación
            links = await page.eval_on_selector_all(
                "a[href], button",
                "els => els.map(e => ({tag: e.tagName, text: (e.innerText || e.textContent || e.getAttribute('aria-label') || '').trim(), href: e.href || '', id: e.id || ''}))"
            )

            postulation_keywords = ["postular", "inscripción", "registro", "nueva", "crear", "participar", "convocatoria", "postulación"]
            relevant = [l for l in links if any(kw in (l.get("text") or "").lower() for kw in postulation_keywords)]

            if relevant:
                print(f"[+] Enlaces de postulación detectados ({len(relevant)}):")
                for l in relevant[:15]:
                    print(f"    • [{l['tag']}] {l['text'][:80]}")
                    if l['href']:
                        print(f"      -> {l['href'][:100]}")
            else:
                print("[-] No se detectaron enlaces obvios de postulación")

            # Buscar tablas o listas de vacantes
            tables = await page.eval_on_selector_all("table", "els => els.map(e => ({id: e.id, headers: e.querySelectorAll('th').length, rows: e.querySelectorAll('tr').length}))")
            if tables:
                print(f"\n[+] Tablas detectadas ({len(tables)}):")
                for t in tables[:5]:
                    print(f"    • id={t['id']}, headers={t['headers']}, rows={t['rows']}")

            # Buscar cards o divs con información de carreras
            cards = await page.evaluate("""() => {
                const cards = Array.from(document.querySelectorAll('[class*="card"], [class*="vacante"], [class*="oferta"], [class*="carrera"]'));
                return cards.slice(0, 10).map(c => ({
                    class: c.className,
                    text: c.innerText?.trim().substring(0, 150) || ''
                }));
            }""")

            if cards:
                print(f"\n[+] Cards/divs detectados ({len(cards)}):")
                for c in cards[:5]:
                    print(f"    • [{c['class'][:50]}] {c['text'][:100]}")

            print("\n[*] Análisis completado. Navegador permanece abierto para intervención manual.")

        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            # No cerramos el navegador - es el del usuario
            pass


if __name__ == "__main__":
    asyncio.run(main())
