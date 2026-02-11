#!/bin/bash
# Script de desarrollo para Linux/Mac

echo "🚀 Iniciando entorno de desarrollo Cantina Tita..."

# Activar entorno virtual si existe
if [ -f ".venv/bin/activate" ]; then
    echo "🐍 Activando entorno virtual..."
    source .venv/bin/activate
fi

# Ejecutar servidor de desarrollo
python3 dev_server.py "$@"