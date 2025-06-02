#!/bin/bash
# Script para hacer push del checkpoint v3.8.1 a GitHub

echo "🚀 Subiendo checkpoint v3.8.1 a GitHub..."
echo "============================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: No estás en el directorio del proyecto YOMJAI"
    echo "Por favor ejecuta desde /Users/Shared/yolo11_project"
    exit 1
fi

# Mostrar estado actual
echo "📊 Estado actual del repositorio:"
git status --short
echo ""

# Mostrar último commit
echo "📝 Último commit:"
git log --oneline -1
echo ""

# Mostrar tags
echo "🏷️  Tag creado:"
git tag -l | tail -1
echo ""

# Preguntar confirmación
echo "¿Deseas hacer push de estos cambios a GitHub? (s/n)"
read -r respuesta

if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
    echo ""
    echo "📤 Haciendo push..."
    
    # Push del branch principal
    echo "1. Subiendo commits..."
    git push origin main
    
    # Push de los tags
    echo ""
    echo "2. Subiendo tags..."
    git push origin --tags
    
    echo ""
    echo "✅ ¡Listo! Checkpoint v3.8.1 subido exitosamente"
    echo ""
    echo "🔗 Puedes ver el checkpoint en:"
    echo "https://github.com/condor090/yolo11-security-system/releases/tag/v3.8.1-telegram-complete"
else
    echo "❌ Push cancelado"
fi

echo ""
echo "📋 Resumen del checkpoint v3.8.1:"
echo "- Sistema de Alertas Telegram Persistentes"
echo "- Alertas con imágenes al expirar timer"
echo "- Envíos repetidos configurables"
echo "- Documentación completa incluida"
echo ""
echo "🎯 Estado: PRODUCCIÓN READY"
