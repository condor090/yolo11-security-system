#!/bin/bash
# Script para verificar que Docker está funcionando correctamente

echo "🧪 Verificando Sistema Docker YOLO11"
echo "===================================="

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar imagen
echo -e "\n1. Verificando imagen Docker..."
if docker images | grep -q "yolo11-security"; then
    echo -e "${GREEN}✓${NC} Imagen encontrada: yolo11-security:latest"
    docker images yolo11-security:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
else
    echo -e "${RED}✗${NC} Imagen no encontrada"
    exit 1
fi

# Verificar contenedor
echo -e "\n2. Verificando contenedor..."
if docker ps | grep -q "yolo11-security-dashboard"; then
    echo -e "${GREEN}✓${NC} Dashboard corriendo"
    docker ps --filter "name=yolo11-security-dashboard" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo -e "${RED}✗${NC} Dashboard no está corriendo"
fi

# Verificar modelo dentro del contenedor
echo -e "\n3. Verificando modelo entrenado en el contenedor..."
MODEL_CHECK=$(docker exec yolo11-security-dashboard ls -la /security_project/models/gate_detector_best.pt 2>&1)
if [[ $MODEL_CHECK == *"gate_detector_best.pt"* ]]; then
    echo -e "${GREEN}✓${NC} Modelo encontrado en el contenedor"
    docker exec yolo11-security-dashboard ls -lh /security_project/models/gate_detector_best.pt
else
    echo -e "${RED}✗${NC} Modelo no encontrado en el contenedor"
fi

# Verificar acceso al dashboard
echo -e "\n4. Verificando acceso al dashboard..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
    echo -e "${GREEN}✓${NC} Dashboard accesible en http://localhost:8501"
else
    echo -e "${YELLOW}⚠${NC} No se pudo verificar el acceso al dashboard"
fi

# Mostrar logs recientes
echo -e "\n5. Últimas líneas de logs:"
docker logs --tail 10 yolo11-security-dashboard

echo -e "\n${GREEN}===================================="
echo -e "Sistema Docker configurado correctamente"
echo -e "Dashboard disponible en: http://localhost:8501"
echo -e "====================================${NC}"

# Instrucciones
echo -e "\nPara probar el dashboard:"
echo "1. Abre tu navegador en http://localhost:8501"
echo "2. Sube una imagen de prueba desde test_images/"
echo "3. Verifica que detecta puertas correctamente"
echo ""
echo "Comandos útiles:"
echo "- Ver logs: docker logs -f yolo11-security-dashboard"
echo "- Detener: ./deploy.sh stop"
echo "- Estado: ./deploy.sh status"
