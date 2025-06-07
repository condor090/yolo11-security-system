#!/bin/bash
#
# YOMJAI - Script de Detención Limpia
#

echo "🛑 DETENIENDO YOMJAI"
echo "===================="

PROJECT_DIR="/Users/Shared/yolo11_project"

# Leer PIDs guardados
if [ -f "$PROJECT_DIR/yomjai.pid" ]; then
    source "$PROJECT_DIR/yomjai.pid"
    
    echo "Deteniendo Backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
    
    echo "Deteniendo Frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null
    
    sleep 2
    
    # Verificar si se detuvieron
    if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "✅ Backend detenido"
    else
        echo "⚠️  Forzando detención de Backend..."
        kill -9 $BACKEND_PID 2>/dev/null
    fi
    
    if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "✅ Frontend detenido"
    else
        echo "⚠️  Forzando detención de Frontend..."
        kill -9 $FRONTEND_PID 2>/dev/null
    fi
    
    rm "$PROJECT_DIR/yomjai.pid"
else
    echo "⚠️  No se encontró archivo de PIDs, limpiando puertos..."
fi

# Limpieza adicional de puertos
echo ""
echo "🧹 Limpiando puertos..."
lsof -ti:8889 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

# Verificación final
sleep 1
python3 "$PROJECT_DIR/port_manager.py" check

echo ""
echo "✅ YOMJAI detenido completamente"
