#!/usr/bin/env python3
"""
Script para login semi-automatizado - maneja popup, Turnstile, y login completo.
Ejecutar cuando las cookies expiren: python3 manual_login.py
"""

import asyncio
from playwright.async_api import async_playwright
import json
import os

DOMAIN = "encuentraempleo.trabajo.gob.ec"
LOGIN_URL = f"https://{DOMAIN}/socioEmpleo-war/paginas/index.jsf"
LOGOUT_URL = f"https://{DOMAIN}/socioEmpleo-war/logout"
BUSQUEDA_URL = f"https://{DOMAIN}/socioEmpleo-war/paginas/aspirante/busquedaOferta.jsf"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(SCRIPT_DIR, "config", "cookies.json")

USERNAME = "1104520281"
PASSWORD = "Conejo2011$"

async def semi_auto_login():
    print("=" * 60)
    print("LOGIN SEMI-AUTOMATIZADO - Encuentra Empleo")
    print("=" * 60)
    print("\nFlujo completo:")
    print("  1. Abre navegador VISIBLE")
    print("  2. Cierra popup inicial si existe")
    print("  3. Click en botón 'Aspirantes' (commandButtonAsp)")
    print("  4. Llena usuario/contraseña automáticamente")
    print("  5. Espera Turnstile (hasta 30s) - detecta 'Success!'")
    print("  6. Click en 'Ingresar' (frmLoginAspirante:commandButtonAsp)")
    print("  7. Verifica sesión en busquedaOferta.jsf")
    print("  8. Guarda cookies frescas en config/cookies.json")
    print("\nIniciando automáticamente...\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. Logout limpio
            print("\n[1/8] Cerrando sesión previa...")
            await page.goto(LOGOUT_URL, timeout=30000)
            await page.wait_for_timeout(2000)
            
            # 2. Ir a login
            print("[2/8] Cargando página de login...")
            await page.goto(LOGIN_URL, timeout=40000)
            await page.wait_for_timeout(3000)
            
            # 3. CERRAR POPUP INICIAL (el que tiene la imagen pop_up_04_2026.jpg)
            print("[3/8] Cerrando popup inicial...")
            try:
                # Buscar y cerrar cualquier modal/overlay
                await page.evaluate("""
                    // Cerrar todos los diálogos PrimeFaces
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
                                if (isDialog) { widget.hide(); }
                            }
                        } catch(e) {}
                    }
                    // Ocultar overlays
                    var overlays = document.querySelectorAll('.ui-widget-overlay, .ui-dialog-mask');
                    overlays.forEach(function(el) { el.style.display = 'none'; });
                    // Buscar popup específico con imagen pop_up_04_2026
                    var imgs = document.querySelectorAll('img[src*="pop_up_04_2026"]');
                    imgs.forEach(function(img) {
                        var parent = img.closest('.ui-dialog, .ui-overlaypanel, [role="dialog"]');
                        if (parent) parent.style.display = 'none';
                    });
                """)
                await page.wait_for_timeout(2000)
                print("     ✅ Popups/overlays cerrados")
            except Exception as e:
                print(f"     ⚠️ Error cerrando popup: {e}")
            
            # 4. Click botón aspirante (commandButtonAsp - el de la imagen Boton_Bus_Empleo.png)
            print("[4/8] Clic en botón 'Aspirantes'...")
            try:
                await page.click("a[id='commandButtonAsp']")
                await page.wait_for_timeout(5000)
                print("     ✅ Formulario de aspirante cargado")
            except Exception as e:
                print(f"     ⚠️ Error click aspirante: {e}")
                # Intentar con JavaScript
                await page.evaluate("""() => {
                    var btn = document.getElementById('commandButtonAsp');
                    if (btn) btn.click();
                }""")
                await page.wait_for_timeout(5000)
            
            # 5. Llenar credenciales
            print("[5/8] Llenando credenciales...")
            await page.fill("input[id='frmLoginAspirante:usernameCandidato']", USERNAME)
            await page.fill("input[id='frmLoginAspirante:passwordCandidato']", PASSWORD)
            print("     ✅ Usuario y contraseña completados")
            
            # 6. Esperar Turnstile - ESPERA AUTOMÁTICA CON POLLING
            print("[6/8] Esperando Turnstile (polling hasta 120s)...")
            print("     Si no se completa solo, resuélvelo manualmente en el navegador visible.")
            turnstile_completed = False
            for i in range(120):
                token = await page.evaluate("() => document.getElementById('frmLoginAspirante:turnstileTokenAspirante').value")
                if token:
                    print(f"     ✅ Turnstile token detectado en {i+1}s")
                    turnstile_completed = True
                    break
                
                success_visible = await page.evaluate("""() => {
                    var successEl = document.getElementById('success');
                    if (successEl) {
                        var style = window.getComputedStyle(successEl);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    }
                    return false;
                }""")
                if success_visible:
                    print(f"     ✅ Turnstile 'Success!' visible en {i+1}s")
                    turnstile_completed = True
                    break
                
                await page.wait_for_timeout(1000)
                if i % 15 == 14:
                    print(f"     Esperando Turnstile... {i+1}/120s (resuelve manualmente si es necesario)")
            
            if not turnstile_completed:
                print("     ⚠️ Turnstile no completado en 120s, intentando login de todos modos...")
            
            # 7. Click en 'Ingresar' (frmLoginAspirante:commandButtonAsp)
            print("[7/8] Enviando login (click en Ingresar)...")
            await page.evaluate("""() => {
                var btn = document.getElementById('frmLoginAspirante:commandButtonAsp');
                if (btn) { btn.click(); }
            }""")
            await page.wait_for_timeout(8000)
            
            # 8. Verificar sesión
            print("[8/8] Verificando sesión en busquedaOferta.jsf...")
            await page.goto(BUSQUEDA_URL, timeout=40000)
            await page.wait_for_timeout(3000)
            
            if "busquedaOferta.jsf" in page.url:
                print("\n" + "=" * 60)
                print("✅ ¡LOGIN EXITOSO! Sesión válida.")
                print("=" * 60)
                
                # Extraer cookies
                cookies = await page.context.cookies()
                jsessionid = None
                nsc = None
                for cookie in cookies:
                    if cookie["name"] == "JSESSIONID" and cookie["domain"] == DOMAIN:
                        jsessionid = cookie["value"]
                    elif cookie["name"] == "NSC_JOmnkwatc53jecrcfmkoaierrq1sab2":
                        nsc = cookie["value"]
                
                if jsessionid:
                    cookie_data = {
                        "JSESSIONID": jsessionid,
                        "NSC_JOmnkwatc53jecrcfmkoaierrq1sab2": nsc or ""
                    }
                    with open(COOKIES_PATH, "w", encoding="utf-8") as f:
                        json.dump(cookie_data, f, indent=2)
                    print(f"\n✅ Cookies guardadas en {COOKIES_PATH}")
                    print(f"   JSESSIONID: {jsessionid[:40]}...")
                    print(f"   NSC: {nsc[:40] if nsc else 'N/A'}...")
                    return True
                else:
                    print("❌ No se encontró JSESSIONID en cookies")
                    return False
            else:
                print(f"\n❌ Login falló - URL actual: {page.url}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(semi_auto_login())