# Job Applications Scanner & Auto-Applier

Este proyecto automatiza la búsqueda y postulación a ofertas de empleo en la plataforma oficial del Ministerio de Trabajo de Ecuador ("Encuentra Empleo") para salarios superiores a $1000 USD, basándose en el perfil profesional del usuario y excluyendo puestos no aplicables.

## Arquitectura y Componentes

- **`playwright_apply.py`**: El script principal en Python que utiliza Playwright (Headless Chromium) para iniciar sesión (usando las cookies), buscar ofertas por rango salarial, filtrar palabras clave no deseadas, abrir los detalles y aplicar automáticamente.
- **`run_playwright.sh`**: Wrapper de shell script que inicializa el entorno (`PATH`, `HOME`), crea el directorio de logs y redirige la salida del script principal.
- **`com.statick.jobapplications.plist`**: Archivo de configuración de macOS LaunchAgent que programa la ejecución diaria automática del script.
- **`config/cookies.json`**: Contiene la sesión activa (`JSESSIONID` y `NSC_...` cookies) para interactuar con la plataforma.
- **`data/applications.md`**: El registro histórico de todas las postulaciones realizadas con éxito, incluyendo la fecha, cargo, empresa y enlace al screenshot del resultado de postulación.

---

## Automatización y Programación Diaria

Para evitar las limitaciones de TCC en macOS que bloquean las tareas de `cron` al acceder a carpetas de usuario como `~/Documents`, hemos implementado la programación nativa a través de un **LaunchAgent** de macOS.

### Configuración del LaunchAgent

El agente está configurado para ejecutarse **todos los días a las 22:00**.

El archivo plist está en:
`~/Library/LaunchAgents/com.statick.jobapplications.plist`

Y apunta directamente a:
`/Users/statick/Documents/job_applications/run_playwright.sh`

### Comandos de Control

Puedes gestionar el agente desde la terminal usando los siguientes comandos:

- **Verificar el estado del Agente:**
  ```bash
  launchctl list | grep jobapplications
  ```
  *(Si aparece en la lista, está cargado correctamente y listo para ejecutarse en su horario).*

- **Ejecutar manualmente en este momento (Prueba):**
  ```bash
  launchctl start com.statick.jobapplications
  ```

- **Detener o descargar el Agente (Desactivar automatización):**
  ```bash
  launchctl unload ~/Library/LaunchAgents/com.statick.jobapplications.plist
  ```

- **Cargar/Recargar el Agente después de hacer cambios:**
  ```bash
  launchctl load ~/Library/LaunchAgents/com.statick.jobapplications.plist
  ```

---

## Logs y Monitoreo

La ejecución automática guarda el historial detallado de salidas en:
- `logs/execution.log` (salida unificada de stdout y stderr del script de python)
- `logs/launchd_stdout.log` (salida estándar de launchd)
- `logs/launchd_stderr.log` (salida de errores de launchd)

Las notificaciones del sistema se enviarán nativamente a macOS usando AppleScript (`osascript`) para informarte sobre el éxito de las postulaciones o si la sesión ha expirado y requiere actualizar las cookies.
