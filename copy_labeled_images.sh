#!/bin/bash

# Script para copiar automáticamente todas las imágenes etiquetadas
# No necesita recordar cuáles fueron - el script las encuentra por usted

echo "🚀 Iniciando copia de imágenes etiquetadas..."

cd /Users/Shared/yolo11_project

# Contador
copied=0
not_found=0

# Procesar cada archivo de etiqueta
for label_file in data/train/labels/*.txt; do
    # Saltar el archivo classes.txt
    if [[ "$label_file" == *"classes.txt" ]]; then
        continue
    fi
    
    # Obtener el nombre base (sin extensión)
    base_name=$(basename "$label_file" .txt)
    
    # Intentar copiar .jpg primero, luego .png
    if [ -f "data/telegram_photos/${base_name}.jpg" ]; then
        cp "data/telegram_photos/${base_name}.jpg" "data/train/images/"
        ((copied++))
        echo -n "."
    elif [ -f "data/telegram_photos/${base_name}.png" ]; then
        cp "data/telegram_photos/${base_name}.png" "data/train/images/"
        ((copied++))
        echo -n "."
    else
        echo ""
        echo "⚠️  No encontrada: ${base_name}"
        ((not_found++))
    fi
done

echo ""
echo "✅ Proceso completado!"
echo "📊 Resumen:"
echo "   - Imágenes copiadas: $copied"
echo "   - No encontradas: $not_found"
echo ""
echo "🎯 Verificación:"
ls -1 data/train/images/*.jpg 2>/dev/null | wc -l | xargs echo "   - Imágenes JPG en train/images:"
ls -1 data/train/labels/*.txt | grep -v classes.txt | wc -l | xargs echo "   - Archivos de etiquetas:"
