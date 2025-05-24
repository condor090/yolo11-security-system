#!/bin/bash
# Lanzador de LabelImg para el proyecto YOLO11

echo "🏷️ Iniciando LabelImg para etiquetado de rejas..."
echo ""

# Verificar si hay imágenes para etiquetar
IMG_COUNT=$(ls -1 /Users/Shared/yolo11_project/data/raw_images/gates_open/*.{jpg,jpeg,png} 2>/dev/null | wc -l)

if [ $IMG_COUNT -eq 0 ]; then
    echo "⚠️  No se encontraron imágenes en data/raw_images/gates_open/"
    echo "   Por favor, copie sus imágenes primero."
    exit 1
fi

echo "✅ Encontradas $IMG_COUNT imágenes para etiquetar"
echo ""

# Cambiar al directorio del proyecto
cd /Users/Shared/yolo11_project

# Ejecutar LabelImg con configuración predefinida
/Users/condor/Library/Python/3.9/bin/labelImg \
    data/raw_images/gates_open \
    data/classes.txt \
    data/train/labels

echo ""
echo "✅ LabelImg cerrado. Etiquetado completado."
