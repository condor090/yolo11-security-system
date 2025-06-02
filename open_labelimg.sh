#!/bin/bash
# Comando para abrir LabelImg desde cualquier ubicación
echo "Abriendo LabelImg para etiquetado de puertas..."
osascript -e 'tell application "Terminal" to do script "cd /Users/Shared/yolo11_project && ./etiquetar_puertas.sh"'
