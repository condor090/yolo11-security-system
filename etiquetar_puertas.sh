#!/bin/bash
# Script de inicio rápido para LabelImg
# Configurado específicamente para el proyecto de puertas

echo "🚀 Iniciando LabelImg para etiquetado de puertas..."
echo "📁 Carpeta de imágenes: /data/telegram_photos/"
echo "💾 Carpeta de etiquetas: /data/train/labels/"
echo "📋 Clases: gate_open (0), gate_closed (1)"
echo ""

cd /Users/Shared/yolo11_project/data/train/labels
/Users/condor/Library/Python/3.9/bin/labelImg /Users/Shared/yolo11_project/data/telegram_photos . classes.txt

echo "✅ LabelImg cerrado"
