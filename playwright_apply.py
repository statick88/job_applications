import asyncio
from playwright.async_api import async_playwright
import os
import json
import time
from datetime import datetime

# Domain for cookies
DOMAIN = "encuentraempleo.trabajo.gob.ec"
URL = f"https://{DOMAIN}/socioEmpleo-war/paginas/aspirante/busquedaOferta.jsf"

# Paths relative to script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(SCRIPT_DIR, "config", "cookies.json")

# Excluded keywords in titles
EXCLUDED_KEYWORDS = [
    "enfermero", "enfermera", "medico", "médico", "odontologo", "odontóloga", 
    "psicologo", "psicóloga", "chofer", "conductor", "obstetriz", "obstetra",
    "terapista", "fisioterapeuta", "odontología", "enfermería", "médica",
    "parvulario", "educación inicial", "mecanico", "mecánico", "soldador",
    "electricista", "albañil", "guardia", "policia", "policía", "militar",
    "auxiliar de enfermeria", "auxiliar de enfermería"
]

# Salary ranges to scan (values from select dropdown)
SALARY_CODES = ["560618", "560619", "562154", "562155", "562156", "562157", "562158"]

def clean_text(text):
    return " ".join(text.split()) if text else ""

def send_notification(title, message):
    print(f"NOTIFICATION: [{title}] {message}")
    # Escape quotes for AppleScript
    safe_message = message.replace('"', '\\"').replace("'", "'")
    safe_title = title.replace('"', '\\"').replace("'", "'")
    cmd = f'osascript -e \'display notification "{safe_message}" with title "{safe_title}"\''
    os.system(cmd)

async def apply_to_jobs():
    successful_applications = []
    expired_session = False
    
    # Load cookies from configuration file
    print(f"Reading cookies from {COOKIES_PATH}...")
    try:
        with open(COOKIES_PATH, "r", encoding="utf-8") as f:
            cookie_data = json.load(f)
        jsessionid = cookie_data.get("JSESSIONID", "")
        nsc = cookie_data.get("NSC_JOmnkwatc53jecrcfmkoaierrq1sab2", "")
    except Exception as e:
        print(f"Error loading cookies: {e}")
        send_notification("Encuentra Empleo - Config Error", "No se pudo leer config/cookies.json.")
        return
        
    cookies = [
        {
            "name": "JSESSIONID",
            "value": jsessionid,
            "domain": DOMAIN,
            "path": "/socioEmpleo-war"
        },
        {
            "name": "NSC_JOmnkwatc53jecrcfmkoaierrq1sab2",
            "value": nsc,
            "domain": DOMAIN,
            "path": "/"
        }
    ]

    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Add cookies
        print("Setting cookies...")
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        # Set viewport size
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        # Helper to clear all dialogs/overlays safely (ONLY dialogs and confirm dialogs)
        async def clear_all_dialogs():
            await page.evaluate("""
                for (var widgetName in PrimeFaces.widgets) {
                    var widget = PrimeFaces.widgets[widgetName];
                    try {
                        if (widget && (typeof widget.hide === 'function')) {
                            var isDialog = false;
                            if (widget.constructor && (widget.constructor.name === 'Dialog' || widget.constructor.name === 'ConfirmDialog')) {
                                isDialog = true;
                            } else if (widgetName.toLowerCase().indexOf('dialog') !== -1 || widgetName.toLowerCase().indexOf('dlg') !== -1) {
                                isDialog = true;
                            }
                            
                            if (isDialog) {
                                widget.hide();
                            }
                        }
                    } catch(e) {}
                }
            """)
            await page.wait_for_timeout(1000)
            
        # Helper to wait for the loading spinner/gears to disappear
        async def wait_for_loading():
            await page.wait_for_timeout(1000)
            try:
                await page.wait_for_selector(".ui-blockui", state="hidden", timeout=10000)
                await page.wait_for_selector("div[id*='status']", state="hidden", timeout=10000)
            except Exception:
                pass
            await page.wait_for_timeout(500)
        
        # Helper to open search dialog with retry and page reload if it fails
        async def open_search_dialog(retries=2):
            nonlocal expired_session
            for attempt in range(1, retries + 1):
                print(f"Opening search dialog (Attempt {attempt}/{retries})...")
                try:
                    await clear_all_dialogs()
                    
                    # Wait for the trigger button
                    await page.wait_for_selector("a[id='formBuscaOferta:buscar']", state="visible", timeout=10000)
                    
                    # Click search toggle button
                    await page.click("a[id='formBuscaOferta:buscar']", force=True)
                    
                    # Wait for dialog search button
                    await page.wait_for_selector("a[id='FormSearch:j_idt128']", state="visible", timeout=10000)
                    print("Search dialog opened successfully.")
                    return True
                except Exception as e:
                    print(f"  Warning: Failed to open search dialog on attempt {attempt}: {e}")
                    debug_img = os.path.join(SCRIPT_DIR, f"debug_dialog_fail_attempt_{attempt}.png")
                    try:
                        await page.screenshot(path=debug_img)
                        print(f"  Saved attempt failure screenshot to {debug_img}")
                    except Exception:
                        pass
                    
                    if attempt < retries:
                        print("  Reloading page to refresh ViewState...")
                        await page.goto(URL, timeout=40000)
                        await wait_for_loading()
                        
                        # Detect expired session (redirected to index.jsf / landing page)
                        if "busquedaOferta.jsf" not in page.url:
                            print(f"  Redirect detected during reload: {page.url}. Session is expired.")
                            expired_session = True
                            send_notification("Encuentra Empleo - Sesión Expirada", "La sesión caducó durante la navegación. Por favor actualiza config/cookies.json")
                            raise Exception("SESSION_EXPIRED")
            
            raise Exception("Failed to open search dialog after all retries")

        # Helper to restore search state after a redirect
        async def restore_search_state(sal_code, target_page):
            print(f"Restoring search state (Salary: {sal_code}, Page: {target_page})...")
            await page.goto(URL, timeout=40000)
            
            # Check if session is expired on reload
            if "busquedaOferta.jsf" not in page.url:
                print(f"Redirected to landing page {page.url} during restore. Session is expired.")
                nonlocal expired_session
                expired_session = True
                send_notification("Encuentra Empleo - Sesión Expirada", "La sesión caducó al restaurar el estado. Por favor actualiza config/cookies.json")
                return
                
            await open_search_dialog(retries=2)
            
            await page.eval_on_selector(
                "select[name='FormSearch:remuneracion_input']", 
                "(el, val) => { el.value = val; el.dispatchEvent(new Event('change')); }", 
                sal_code
            )
            await page.wait_for_timeout(500)
            
            await page.eval_on_selector(
                "select[name='FormSearch:provincia_input']", 
                "(el, val) => { el.value = val; el.dispatchEvent(new Event('change')); }", 
                "-1"
            )
            await page.wait_for_timeout(500)
            
            await page.click("a[id='FormSearch:j_idt128']", force=True)
            await page.wait_for_timeout(4000)
            await clear_all_dialogs()
            await page.wait_for_timeout(1000)
            
            if target_page > 1:
                print(f"Restoring page {target_page}...")
                await page.eval_on_selector(
                    "select[name='formBuscaOferta:pagina_input']",
                    "(el, val) => { el.value = val; el.dispatchEvent(new Event('change')); }",
                    str(target_page)
                )
                await page.wait_for_timeout(4000)
        
        try:
            print(f"Navigating to {URL}...")
            await page.goto(URL, timeout=40000)
            
            # Detect expired session (redirected to index.jsf / landing page)
            if "busquedaOferta.jsf" not in page.url:
                print(f"Redirected to landing page {page.url} at startup. Session is expired.")
                expired_session = True
                send_notification("Encuentra Empleo - Sesión Expirada", "Por favor actualiza las cookies en config/cookies.json")
                return
            
            # Wait for main page to load
            await page.wait_for_selector("a[id='formBuscaOferta:buscar']", state="visible", timeout=20000)
            print("Main page loaded successfully.")
            
            # We will loop through the salary codes
            for sal_code in SALARY_CODES:
                print(f"\n--- Scanning Salary Code: {sal_code} ---")
                
                # Open search dialog using our robust helper
                await open_search_dialog(retries=2)
                
                # Select salary code via JS evaluation
                print(f"Selecting salary code {sal_code}...")
                await page.eval_on_selector(
                    "select[name='FormSearch:remuneracion_input']", 
                    "(el, val) => { el.value = val; el.dispatchEvent(new Event('change')); }", 
                    sal_code
                )
                await page.wait_for_timeout(500)
                
                # Make sure province is set to 'Todos' (-1)
                print("Setting province to Todos...")
                await page.eval_on_selector(
                    "select[name='FormSearch:provincia_input']", 
                    "(el, val) => { el.value = val; el.dispatchEvent(new Event('change')); }", 
                    "-1"
                )
                await page.wait_for_timeout(500)
                
                # Wait for any active loaders to clear
                await wait_for_loading()
                
                # Click search button inside dialog
                print("Clicking search...")
                await page.click("a[id='FormSearch:j_idt128']", force=True)
                
                # Wait for AJAX update
                await page.wait_for_timeout(4000)
                await wait_for_loading()
                
                # Clear all dialogs (closes OfertaSearchDialog)
                await clear_all_dialogs()
                
                # Determine total pages
                total_pages = 1
                pagination_select = await page.query_selector("select[name='formBuscaOferta:pagina_input']")
                if pagination_select:
                    options = await pagination_select.query_selector_all("option")
                    total_pages = len(options)
                
                print(f"Total pages found: {total_pages}")
                
                # Loop through pages
                current_page = 1
                while current_page <= total_pages:
                    # Scan job cards on current page
                    job_cards = await page.query_selector_all("fieldset[class*='fieldsetOferta']")
                    print(f"Found {len(job_cards)} job cards on page {current_page}.")
                    
                    idx = 0
                    while idx < len(job_cards):
                        # Re-query elements to ensure correctness
                        job_cards = await page.query_selector_all("fieldset[class*='fieldsetOferta']")
                        if idx >= len(job_cards):
                            break
                            
                        card = job_cards[idx]
                        
                        # Extract details
                        text_content = await card.inner_text()
                        lines = [clean_text(line) for line in text_content.split("\n") if clean_text(line)]
                        
                        company = lines[0] if len(lines) > 0 else "Desconocido"
                        title = lines[1] if len(lines) > 1 else "Desconocido"
                        job_code = lines[2] if len(lines) > 2 else "Desconocido"
                        
                        # Find salary and location
                        salary_str = ""
                        location_str = ""
                        for line in lines:
                            if "remuneración:" in line.lower() or "remuneracion:" in line.lower():
                                salary_str = line
                            elif "hace:" in line.lower() or "dias" in line.lower():
                                location_str = line.split("HACE:")[0].strip()
                                
                        title_lower = title.lower()
                        excluded = any(kw in title_lower for kw in EXCLUDED_KEYWORDS)
                        
                        print(f"\nEvaluating Job {idx+1}: {title} | {company} | {salary_str} | {location_str} | Code: {job_code}")
                        if excluded:
                            print("  -> EXCLUDED (Matches exclusion list)")
                            idx += 1
                            continue
                            
                        # Find clickable link wrapper
                        link_id = ""
                        parent_a = await card.evaluate_handle("el => el.closest('a')")
                        if parent_a:
                            link_id = await parent_a.evaluate("el => el.id")
                            
                        if not link_id:
                            print("  Warning: Link ID not found directly, skipping.")
                            idx += 1
                            continue
                            
                        print(f"  Link ID to click: {link_id}")
                        
                        # Click link to open modal
                        print("  Opening details modal...")
                        await page.click(f"a[id='{link_id}']", force=True)
                        await page.wait_for_timeout(3500)
                        await wait_for_loading()
                        
                        # Check if we were redirected to the CV / Hoja de Vida page
                        if "busquedaOferta.jsf" not in page.url:
                            print(f"  [Redirect Detected] URL changed to: {page.url}")
                            print("  -> Navigating back to search page and restoring state...")
                            await restore_search_state(sal_code, current_page)
                            idx += 1
                            continue
                        
                        # Wait for modal contents to be visible
                        modal = await page.query_selector("#formVerOferta\\:verOfertasearchDlg")
                        if not modal:
                            print("  Error: Modal dialog did not open.")
                            await clear_all_dialogs()
                            idx += 1
                            continue
                            
                        # Check details and click "Aplicar" (ONLY target VISIBLE button)
                        apply_buttons = await page.query_selector_all("button")
                        target_apply_btn = None
                        for btn in apply_buttons:
                            btn_id = await btn.evaluate("el => el.id")
                            btn_text = await btn.inner_text()
                            is_vis = await btn.is_visible()
                            if "formVerOferta" in btn_id and "Aplicar" in btn_text and is_vis:
                                target_apply_btn = btn
                                break
                                
                        if not target_apply_btn:
                            print("  -> Cannot apply: 'Aplicar' button not found/visible.")
                            await clear_all_dialogs()
                            idx += 1
                            continue
                            
                        print("  -> 'Aplicar' button found. Clicking Apply...")
                        await target_apply_btn.click(force=True)
                        await page.wait_for_timeout(2500)
                        await wait_for_loading()
                        
                        # Check if "¡RECUERDA!" or other overlay dialog popped up
                        all_buttons = await page.query_selector_all("button")
                        sig_btn = None
                        for btn in all_buttons:
                            btn_text = await btn.inner_text()
                            is_vis = await btn.is_visible()
                            if "Siguiente" in btn_text and is_vis:
                                sig_btn = btn
                                break
                                
                        if sig_btn:
                            print("  -> '¡RECUERDA!' dialog found. Clicking Siguiente...")
                            await sig_btn.click(force=True)
                            await page.wait_for_timeout(2500)
                            await wait_for_loading()
                        
                        # Check for confirmation warning
                        accept_btn = None
                        buttons = await page.query_selector_all("button")
                        for btn in buttons:
                            btn_id = await btn.evaluate("el => el.id")
                            btn_text = await btn.inner_text()
                            is_vis = await btn.is_visible()
                            if "formVerOferta" in btn_id and "Aceptar" in btn_text and is_vis:
                                accept_btn = btn
                                break
                                
                        if accept_btn:
                            print("  -> Confirmation warning appeared. Clicking Aceptar to confirm...")
                            await accept_btn.click(force=True)
                            await page.wait_for_timeout(3000)
                            await wait_for_loading()
                            
                        # Capture screenshot of postulation result
                        job_folder = os.path.join(SCRIPT_DIR, "applications", job_code.replace(':', '_'))
                        os.makedirs(job_folder, exist_ok=True)
                        screenshot_path = os.path.join(job_folder, "postulation_success.png")
                        await page.screenshot(path=screenshot_path)
                        print(f"  -> Captured screenshot to {screenshot_path}")
                        
                        # Log application
                        was_logged = log_application(company, title, job_code, location_str, salary_str, screenshot_path)
                        if was_logged:
                            successful_applications.append(f"{title} ({company})")
                        
                        # Close details dialog and warning dialogs
                        await clear_all_dialogs()
                        idx += 1
                    
                    # Navigate to next page if applicable
                    current_page += 1
                    if current_page <= total_pages:
                        print(f"Navigating to page {current_page}...")
                        await page.eval_on_selector(
                            "select[name='formBuscaOferta:pagina_input']",
                            "(el, val) => { el.value = val; el.dispatchEvent(new Event('change')); }",
                            str(current_page)
                        )
                        await page.wait_for_timeout(4000)
                        await wait_for_loading()
            
            # Finished scanning all codes
            if len(successful_applications) > 0:
                send_notification("Postulación Completada", f"Se postularon {len(successful_applications)} ofertas con éxito.")
            else:
                send_notification("Postulación Completada", "Escaneo finalizado. No se encontraron nuevas ofertas aplicables.")
                
        except Exception as e:
            if "SESSION_EXPIRED" in str(e):
                print("\nGraceful shutdown: Session is expired. Stopping crawler execution.")
                return
            print(f"\nERROR OCCURRED: {e}")
            error_img = os.path.join(SCRIPT_DIR, "debug_error.png")
            try:
                await page.screenshot(path=error_img)
                print(f"Saved error screenshot to {error_img}")
            except Exception:
                pass
            send_notification("Error de Ejecución", f"Error en postulación automática: {str(e)[:40]}")
            raise e
        finally:
            await browser.close()
            print("\nBrowser closed.")

def log_application(company, title, code, location, salary, screenshot_path):
    today = datetime.now().strftime("%Y-%m-%d")
    tracker_path = os.path.join(SCRIPT_DIR, "data", "applications.md")
    
    existing_content = ""
    if os.path.exists(tracker_path):
        with open(tracker_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
            
    if code in existing_content:
        print(f"  -> Already logged {code} in applications.md")
        return False
        
    new_entry = f"""
## Postulación Activa

### {company} - {title}

| Campo | Valor |
|-------|-------|
| **Empresa** | {company} |
| **Puesto** | {title} |
| **Código** | {code} |
| **Ubicación** | {location} |
| **Remuneración** | {salary} |
| **Fecha postulación** | {today} |
| **Estado** | ✅ POSTULADO AUTOMÁTICO (Playwright) |
| **Captura** | [Screenshot](file://{os.path.abspath(screenshot_path)}) |

**Seguimiento:**
- {today}: Postulado automáticamente a través de la plataforma Encuentra Empleo.

---
"""
    
    header = "# Applications Tracker\n"
    if header in existing_content:
        content = existing_content.replace(header, header + new_entry)
    else:
        content = header + new_entry + existing_content
        
    os.makedirs(os.path.dirname(tracker_path), exist_ok=True)
    with open(tracker_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"  -> Appended postulation for {code} to {tracker_path}")
    return True

if __name__ == "__main__":
    asyncio.run(apply_to_jobs())
