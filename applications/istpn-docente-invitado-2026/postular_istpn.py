"""
Script de postulación automática ISTPN - Docente Invitado Civil
Navega el portal https://postudoc.isupol.edu.ec/ y aplica a la vacante
de Tecnicatura Superior en Investigación en Ciberdelitos (En Línea).
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Configuración
PORTAL_URL = "https://postudoc.isupol.edu.ec/dashboard/postulacionesc"
LOGIN_URL = "https://postudoc.isupol.edu.ec/"
USERNAME = "1104520281"
PASSWORD = "qopmip-setmim-wuZre5"

# Datos de postulación
POSTULACION_DATA = {
    "carrera": "Tecnicatura Superior en Investigación en Ciberdelitos",
    "modalidad": "En Línea",
    "asignatura_preferida": "Ethical Hacking",
    "asignaturas_alternativas": ["Ciberseguridad", "Ciberdefensa", "Inteligencia Artificial"],
}

OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(exist_ok=True)


async def main():
    async with async_playwright() as p:
        # Lanzar navegador visible para depuración
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        page = await context.new_page()

        print(f"[*] Navegando al dashboard: {PORTAL_URL}")
        try:
            response = await page.goto(PORTAL_URL, wait_until="networkidle", timeout=30000)
            print(f"[*] Status HTTP: {response.status}")

            # Screenshot inicial
            await page.screenshot(path=str(OUTPUT_DIR / "istpn_dashboard.png"), full_page=True)
            print(f"[*] Screenshot guardado: istpn_dashboard.png")

            # Verificar si hay login
            current_url = page.url
            page_text = await page.evaluate("document.body.innerText")

            if "login" in current_url.lower() or "iniciar sesión" in page_text.lower() or "autenticar" in page_text.lower():
                print("[!] Detectada pantalla de login. Intentando autenticación...")
                await page.screenshot(path=str(OUTPUT_DIR / "istpn_login.png"), full_page=True)

                # Intentar login con credenciales proporcionadas
                # Buscar campos de usuario/contraseña
                username_input = await page.evaluate("""() => {
                    const inputs = Array.from(document.querySelectorAll('input'));
                    const userField = inputs.find(i => 
                        i.type === 'text' || 
                        i.type === 'email' || 
                        i.name?.toLowerCase().includes('user') ||
                        i.name?.toLowerCase().includes('cedula') ||
                        i.id?.toLowerCase().includes('user') ||
                        i.id?.toLowerCase().includes('cedula') ||
                        i.placeholder?.toLowerCase().includes('usuario') ||
                        i.placeholder?.toLowerCase().includes('cédula')
                    );
                    const passField = inputs.find(i => 
                        i.type === 'password' ||
                        i.name?.toLowerCase().includes('pass') ||
                        i.id?.toLowerCase().includes('pass') ||
                        i.placeholder?.toLowerCase().includes('contraseña')
                    );
                    return {
                        user: userField ? {name: userField.name, id: userField.id, type: userField.type} : null,
                        pass: passField ? {name: passField.name, id: passField.id, type: passField.type} : null
                    };
                }""")

                print(f"[*] Campos detectados: {username_input}")

                if username_input and username_input.get("user") and username_input.get("pass"):
                    # Llenar credenciales
                    user_selector = f"input[name='{username_input['user']['name']}']" if username_input['user']['name'] else f"input#{username_input['user']['id']}"
                    pass_selector = f"input[name='{username_input['pass']['name']}']" if username_input['pass']['name'] else f"input#{username_input['pass']['id']}"

                    await page.fill(user_selector, USERNAME)
                    await page.fill(pass_selector, PASSWORD)

                    # Buscar botón de submit
                    submit_btn = await page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                        const btn = btns.find(b => 
                            b.innerText?.toLowerCase().includes('ingresar') ||
                            b.innerText?.toLowerCase().includes('entrar') ||
                            b.innerText?.toLowerCase().includes('login') ||
                            b.value?.toLowerCase().includes('ingresar') ||
                            b.type === 'submit'
                        );
                        return btn ? {tag: btn.tagName, text: btn.innerText || btn.value, id: btn.id} : null;
                    }""")

                    if submit_btn:
                        print(f"[*] Click en botón: {submit_btn}")
                        if submit_btn['tag'] == 'button':
                            await page.click(f"#{submit_btn['id']}") if submit_btn.get('id') else await page.click(f"text={submit_btn['text']}")
                        else:
                            await page.click(f"input[type='submit']")
                        
                        await page.wait_for_load_state("networkidle", timeout=15000)
                        await page.screenshot(path=str(OUTPUT_DIR / "istpn_post_login.png"), full_page=True)
                        print("[+] Login ejecutado. Verificar screenshot.")
                    else:
                        print("[-] No se encontró botón de submit")
                else:
                    print("[-] No se detectaron campos de login estándar")

            else:
                print("[+] Sesión activa detectada - dashboard accesible")

            # Analizar contenido del dashboard
            print("\n--- CONTENIDO DASHBOARD (primeros 2000 chars) ---")
            print(page_text[:2000])
            print("--- FIN ---\n")

            # Buscar botones/enlaces de postulación
            links = await page.eval_on_selector_all(
                "a[href], button", 
                "els => els.map(e => ({tag: e.tagName, text: (e.innerText || e.textContent || e.getAttribute('aria-label') || '')).trim(), href: e.href || '', id: e.id || '', class: e.className || ''}))"
            )

            postulation_keywords = ["postular", "inscripción", "registro", "nueva", "crear", "participar", "convocatoria"]
            relevant = [l for l in links if any(kw in (l.get("text") or "").lower() for kw in postulation_keywords)]

            if relevant:
                print(f"[+] Enlaces de postulación detectados ({len(relevant)}):")
                for l in relevant[:10]:
                    print(f"    • [{l['tag']}] {l['text'][:60]} -> {l['href'][:80]}")
            else:
                print("[-] No se detectaron enlaces obvios de postulación en el dashboard actual.")

        except Exception as e:
            print(f"[ERROR] {e}")
            await page.screenshot(path=str(OUTPUT_DIR / "istpn_error.png"), full_page=True)
        finally:
            print("\n[*] Navegador abierto. Presioná Ctrl+C para salir o esperá 5 minutos...")
            await asyncio.sleep(300)  # 5 minutos para intervención manual
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
