#!/bin/bash
# Script para iniciar todos los servicios del sistema YOLO11 Security

echo "🚀 INICIANDO SISTEMA YOLO11 SECURITY"
echo "===================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ Error: No estamos en el directorio correcto${NC}"
    echo "   Ejecuta desde: /Users/Shared/yolo11_project"
    exit 1
fi

# 1. Iniciar Backend
echo -e "${YELLOW}1. Iniciando Backend...${NC}"
echo "   Puerto: 8889"
echo "   API: http://localhost:8889"
echo ""

# Matar procesos antiguos si existen
pkill -f "python.*main.py" 2>/dev/null

# Iniciar backend en background
cd backend
python3 main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Esperar a que el backend esté listo
echo -n "   Esperando que el backend esté listo"
for i in {1..10}; do
    if curl -s http://localhost:8889/api/health > /dev/null; then
        echo -e "\n   ${GREEN}✅ Backend iniciado correctamente (PID: $BACKEND_PID)${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# 2. Iniciar Frontend
echo ""
echo -e "${YELLOW}2. Iniciando Frontend...${NC}"
echo "   Puerto: 3000"
echo "   URL: http://localhost:3000"
echo ""

cd frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "   ${GREEN}✅ Frontend iniciándose (PID: $FRONTEND_PID)${NC}"
echo "   Espera unos segundos a que compile..."

# 3. Mostrar resumen
echo ""
echo -e "${GREEN}===================================="
echo "✅ SISTEMA INICIADO CORRECTAMENTE"
echo "====================================${NC}"
echo ""
echo "📡 SERVICIOS ACTIVOS:"
echo "   - Backend:  http://localhost:8889 (PID: $BACKEND_PID)"
echo "   - Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "   - WebSocket: ws://localhost:8889/ws"
echo ""
echo "📱 ACCEDER AL SISTEMA:"
echo "   1. Espera ~10 segundos a que el frontend compile"
echo "   2. Abre tu navegador en: http://localhost:3000"
echo ""
echo "🛠️ FUNCIONALIDADES DISPONIBLES:"
echo "   - Dashboard con métricas"
echo "   - Monitor de alertas en tiempo real"
echo "   - Análisis de imágenes"
echo "   - Configuración → Cámaras → 🔍 Buscar Cámaras"
echo ""
echo "🛑 PARA DETENER:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   O ejecuta: pkill -f 'python.*main.py|npm start'"
echo ""
echo "📝 LOGS:"
echo "   - Backend:  tail -f backend.log"
echo "   - Frontend: tail -f frontend.log"
echo ""
echo -e "${YELLOW}⏳ El frontend tardará ~10-15 segundos en estar listo...${NC}"
echo ""
