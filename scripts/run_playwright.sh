#!/bin/bash

# ==============================================================================
# Script de ejecución diaria para la postulación de empleos
# Autor: Antigravity (Senior Architect)
# ==============================================================================

# Cambiar al directorio del proyecto
PROJECT_DIR="/Users/statick/Documents/job_applications"
cd "$PROJECT_DIR" || {
    echo "ERROR: No se pudo cambiar al directorio $PROJECT_DIR"
    exit 1
}

# Configurar el PATH para asegurar que Homebrew y Python sean accesibles
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Configurar el entorno HOME
export HOME="/Users/statick"

# Leer credenciales desde macOS Keychain (seguro, no en texto plano)
# Keychain service name: "encuentraempleo"
# Account: tu usuario del portal
KEYCHAIN_SERVICE="encuentraempleo"
KEYCHAIN_ACCOUNT="1104520281"  # Tu cédula/usuario del portal

echo "Reading credentials from Keychain..."
ENCUENTRA_EMPLEO_USER=$(security find-generic-password -a "$KEYCHAIN_ACCOUNT" -s "$KEYCHAIN_SERVICE" -w 2>/dev/null)
ENCUENTRA_EMPLEO_PASS=$(security find-generic-password -a "$KEYCHAIN_ACCOUNT" -s "$KEYCHAIN_SERVICE" -w 2>/dev/null)

if [ -n "$ENCUENTRA_EMPLEO_USER" ] && [ -n "$ENCUENTRA_EMPLEO_PASS" ]; then
    export ENCUENTRA_EMPLEO_USER
    export ENCUENTRA_EMPLEO_PASS
    echo "✅ Credentials loaded from Keychain"
else
    echo "⚠️ No credentials in Keychain - will use existing cookies only"
    echo "   To add: security add-generic-password -a \"$KEYCHAIN_ACCOUNT\" -s \"$KEYCHAIN_SERVICE\" -w \"tu_password\""
fi

# Crear directorio de logs si no existe
mkdir -p "$PROJECT_DIR/logs"

LOG_FILE="$PROJECT_DIR/logs/execution.log"

echo "=== INICIO DE EJECUCIÓN: $(date) ===" >> "$LOG_FILE"

# Ejecutar el script de Playwright
python3 playwright_apply.py >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "=== FIN DE EJECUCIÓN: $(date) (Exit Code: $EXIT_CODE) ===" >> "$LOG_FILE"

exit $EXIT_CODE