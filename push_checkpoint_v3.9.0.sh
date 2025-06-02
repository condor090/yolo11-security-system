#!/bin/bash
# Script para push a GitHub con checkpoint v3.9.0

echo "🚀 Iniciando push del checkpoint v3.9.0 a GitHub..."
echo "================================================"

cd /Users/Shared/yolo11_project

# Mostrar estado actual
echo "📊 Estado actual del repositorio:"
git status --short

# Mostrar commits pendientes
echo -e "\n📝 Commits pendientes de push:"
git log origin/main..HEAD --oneline

# Información del repositorio
echo -e "\n📍 Repositorio remoto:"
git remote -v | head -1

# Intentar push
echo -e "\n🔄 Ejecutando push..."
git push origin main

if [ $? -eq 0 ]; then
    echo -e "\n✅ Push completado exitosamente!"
    echo "🎯 Checkpoint v3.9.0 subido a GitHub"
    echo "📅 Fecha: $(date)"
else
    echo -e "\n❌ Error al hacer push"
    echo "💡 Sugerencia: Verificar credenciales de GitHub"
    echo "   - Usar token de acceso personal si es necesario"
    echo "   - Verificar permisos del repositorio"
fi

echo -e "\n================================================"
echo "💡 YOMJAI v3.9.0 - Sistema completo en producción"
echo "🦅 Desarrollado por Virgilio IA"
