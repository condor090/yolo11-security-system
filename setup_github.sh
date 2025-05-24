#!/bin/bash
# Script para preparar el repositorio GitHub

echo "🚀 Preparando repositorio YOLO11 Security System para GitHub"
echo "=========================================================="

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Crear estructura de directorios para docs
mkdir -p docs/images
mkdir -p tests
mkdir -p .github/ISSUE_TEMPLATE

# Crear archivos de documentación vacíos
touch docs/images/.gitkeep
touch tests/.gitkeep

# Crear README simplificado si no quiere usar el completo
if [ ! -f "README.md" ]; then
    cp README_GITHUB.md README.md
    echo -e "${GREEN}✓ README.md creado${NC}"
fi

# Agregar archivos al staging
git add .
echo -e "${GREEN}✓ Archivos agregados al staging${NC}"

# Crear primer commit
git commit -m "feat: Initial commit - YOLO11 Security System

- Docker setup for cross-platform deployment
- Streamlit dashboard for real-time monitoring
- Training scripts optimized for Apple Silicon
- Complete documentation and examples"

echo -e "${GREEN}✓ Commit inicial creado${NC}"

echo ""
echo -e "${BLUE}Próximos pasos:${NC}"
echo "1. Crear un repositorio en GitHub:"
echo "   - Ve a https://github.com/new"
echo "   - Nombre sugerido: yolo11-security-system"
echo "   - Descripción: Sistema de Seguridad con YOLO11 - Detección de Rejas y Vehículos"
echo ""
echo "2. Conectar tu repositorio local:"
echo -e "${YELLOW}git remote add origin https://github.com/TU-USUARIO/yolo11-security-system.git${NC}"
echo -e "${YELLOW}git push -u origin main${NC}"
echo ""
echo "3. Configurar secretos en GitHub (opcional):"
echo "   - Settings → Secrets → Actions"
echo "   - Agregar DOCKER_USERNAME y DOCKER_PASSWORD"
echo ""
echo "4. Activar GitHub Pages para documentación (opcional):"
echo "   - Settings → Pages → Source: Deploy from branch"
echo "   - Branch: main → /docs"
echo ""
echo -e "${GREEN}¡Repositorio listo para GitHub!${NC} 🎉"
