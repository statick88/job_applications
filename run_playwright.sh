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

# Crear directorio de logs si no existe
mkdir -p "$PROJECT_DIR/logs"

LOG_FILE="$PROJECT_DIR/logs/execution.log"

echo "=== INICIO DE EJECUCIÓN: $(date) ===" >> "$LOG_FILE"

# Ejecutar el script de Playwright
python3 playwright_apply.py >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "=== FIN DE EJECUCIÓN: $(date) (Exit Code: $EXIT_CODE) ===" >> "$LOG_FILE"

exit $EXIT_CODE
