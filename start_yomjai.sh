#!/bin/bash
# Script simple para iniciar YOMJAI con limpieza de puertos

echo "🦅 INICIANDO YOMJAI"
echo "=================="

# Limpiar puertos SIEMPRE
echo "🧹 Limpiando puertos..."
lsof -ti:8889 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
sleep 2

# Iniciar Backend
echo "🚀 Iniciando Backend (puerto 8889)..."
cd /Users/Shared/yolo11_project/backend
python3 main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "   PID Backend: $BACKEND_PID"

# Esperar a que el backend esté listo
echo "   Esperando backend..."
sleep 10

# Iniciar Frontend
echo "🚀 Iniciando Frontend (puerto 3000)..."
cd /Users/Shared/yolo11_project/frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   PID Frontend: $FRONTEND_PID"

echo ""
echo "✅ SISTEMA INICIADO"
echo "=================="
echo "Backend:  http://localhost:8889"
echo "Frontend: http://localhost:3000"
echo ""
echo "Para detener: kill $BACKEND_PID $FRONTEND_PID"
