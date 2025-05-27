#!/bin/bash

echo "🚀 Iniciando Sistema de Seguridad YOLO11 v3.0"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js no encontrado${NC}"
    echo "Instala Node.js desde https://nodejs.org/"
    exit 1
fi

echo -e "${BLUE}📦 Instalando dependencias del backend...${NC}"
cd backend
pip3 install -r requirements.txt

echo -e "${BLUE}📦 Instalando dependencias del frontend...${NC}"
cd ../frontend
npm install

echo ""
echo -e "${GREEN}✅ Instalación completa${NC}"
echo ""
echo "Para iniciar el sistema:"
echo ""
echo "1. Backend (Terminal 1):"
echo "   cd backend"
echo "   python3 main.py"
echo ""
echo "2. Frontend (Terminal 2):"
echo "   cd frontend"
echo "   npm run start"
echo ""
echo "Luego abre http://localhost:3000 en tu navegador"
echo ""
echo -e "${GREEN}🚀 ¡Listo para usar!${NC}"
