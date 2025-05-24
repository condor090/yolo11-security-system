#!/bin/bash
# Script para preparar etiquetado de imágenes

echo "🏷️ Preparando ambiente de etiquetado..."

# Crear directorios
mkdir -p data/raw_images/gates_open
mkdir -p data/raw_images/gates_closed
mkdir -p data/train/images
mkdir -p data/train/labels
mkdir -p data/val/images
mkdir -p data/val/labels

# Crear archivo de clases
cat > data/classes.txt << EOF
gate_open
gate_closed
authorized_person
unauthorized_person
truck
car
motorcycle
EOF

echo "✅ Estructura creada"
echo ""
echo "📋 Próximos pasos:"
echo "1. Copie sus 60 imágenes a: data/raw_images/gates_open/"
echo "2. Instale LabelImg: pip install labelImg"
echo "3. Ejecute: labelImg data/raw_images/gates_open data/classes.txt"
echo "4. Configure LabelImg:"
echo "   - Change Save Dir: data/train/labels"
echo "   - View > Auto Save Mode ✓"
echo "   - Format: YOLO"
echo ""
echo "💡 Tips de etiquetado:"
echo "- Presione 'W' para crear caja"
echo "- Presione 'D' para siguiente imagen"
echo "- Presione 'A' para imagen anterior"
echo "- Ctrl+S para guardar"
echo ""
echo "🎯 Meta: 5-10 segundos por imagen = 5-10 minutos total"
