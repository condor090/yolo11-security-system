#!/bin/bash
# Script de construcción y despliegue del sistema de seguridad YOLO11

set -e

echo "🚀 YOLO11 Security System - Build & Deploy Script"
echo "================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado"
        exit 1
    fi
    log_success "Docker encontrado"
}

# Verificar NVIDIA Docker (opcional)
check_nvidia_docker() {
    if docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
        log_success "NVIDIA Docker configurado correctamente"
        export DOCKER_GPU="--gpus all"
    else
        log_warning "NVIDIA Docker no disponible - usando CPU"
        export DOCKER_GPU=""
    fi
}

# Construir imagen Docker
build_image() {
    log_info "Construyendo imagen Docker..."
    
    docker build -f Dockerfile.security -t yolo11-security:latest . \
        --build-arg BUILDKIT_INLINE_CACHE=1
    
    if [ $? -eq 0 ]; then
        log_success "Imagen construida exitosamente"
    else
        log_error "Error construyendo la imagen"
        exit 1
    fi
}

# Crear directorios necesarios
setup_directories() {
    log_info "Creando estructura de directorios..."
    
    mkdir -p data/{train,val,test}/{images,labels}
    mkdir -p models runs logs exports notebooks
    mkdir -p datasets/raw datasets/processed
    
    log_success "Directorios creados"
}

# Descargar modelos base
download_models() {
    log_info "Descargando modelos base..."
    
    if [ ! -f "models/yolo11m.pt" ]; then
        wget -O models/yolo11m.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11m.pt
        log_success "Modelo YOLO11m descargado"
    else
        log_info "Modelo YOLO11m ya existe"
    fi
}

# Ejecutar contenedor
run_container() {
    local mode=$1
    
    log_info "Ejecutando contenedor en modo: $mode"
    
    case $mode in
        "interactive")
            docker run -it --rm $DOCKER_GPU \
                -v $(pwd)/data:/security_project/data \
                -v $(pwd)/models:/security_project/models \
                -v $(pwd)/runs:/security_project/runs \
                -v $(pwd)/logs:/security_project/logs \
                -p 8000:8000 -p 8501:8501 -p 6006:6006 \
                --name yolo11-security \
                yolo11-security:latest bash
            ;;
        "training")
            docker run -d $DOCKER_GPU \
                -v $(pwd)/data:/security_project/data \
                -v $(pwd)/models:/security_project/models \
                -v $(pwd)/runs:/security_project/runs \
                -v $(pwd)/logs:/security_project/logs \
                --name yolo11-security-train \
                yolo11-security:latest python scripts/train_security_model.py
            ;;
        "dashboard")
            docker run -d $DOCKER_GPU \
                -v $(pwd)/data:/security_project/data \
                -v $(pwd)/models:/security_project/models \
                -v $(pwd)/runs:/security_project/runs \
                -v $(pwd)/logs:/security_project/logs \
                -p 8501:8501 \
                --name yolo11-security-dashboard \
                yolo11-security:latest streamlit run apps/security_dashboard.py --server.port 8501 --server.address 0.0.0.0
            ;;
        "inference")
            docker run -d $DOCKER_GPU \
                -v $(pwd)/data:/security_project/data \
                -v $(pwd)/models:/security_project/models \
                -v $(pwd)/runs:/security_project/runs \
                -v $(pwd)/logs:/security_project/logs \
                --name yolo11-security-inference \
                yolo11-security:latest python scripts/security_system.py
            ;;
        *)
            log_error "Modo no válido. Usar: interactive, training, dashboard, inference"
            exit 1
            ;;
    esac
}

# Mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  build                 Construir imagen Docker"
    echo "  setup                 Configurar directorios y descargar modelos"
    echo "  run-interactive       Ejecutar contenedor interactivo"
    echo "  run-training         Ejecutar entrenamiento en background"
    echo "  run-dashboard        Ejecutar dashboard web"
    echo "  run-inference        Ejecutar sistema de inferencia"
    echo "  stop                 Detener todos los contenedores"
    echo "  clean                Limpiar imágenes y contenedores"
    echo "  logs [container]     Ver logs de contenedor"
    echo "  status               Ver estado de contenedores"
    echo "  help                 Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 build && $0 setup && $0 run-dashboard"
    echo "  $0 run-interactive"
    echo "  $0 logs yolo11-security-dashboard"
}

# Detener contenedores
stop_containers() {
    log_info "Deteniendo contenedores..."
    
    docker ps -q --filter "name=yolo11-security*" | xargs -r docker stop
    docker ps -aq --filter "name=yolo11-security*" | xargs -r docker rm
    
    log_success "Contenedores detenidos"
}

# Limpiar sistema
clean_system() {
    log_info "Limpiando sistema..."
    
    stop_containers
    docker image rm yolo11-security:latest 2>/dev/null || true
    docker system prune -f
    
    log_success "Sistema limpio"
}

# Ver logs
show_logs() {
    local container_name=$1
    
    if [ -z "$container_name" ]; then
        log_info "Contenedores disponibles:"
        docker ps --filter "name=yolo11-security*" --format "table {{.Names}}\t{{.Status}}"
        return
    fi
    
    docker logs -f "$container_name"
}

# Ver estado
show_status() {
    log_info "Estado de contenedores:"
    docker ps --filter "name=yolo11-security*" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    log_info "Uso de recursos:"
    docker stats --no-stream --filter "name=yolo11-security*" --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Función principal
main() {
    case $1 in
        "build")
            check_docker
            check_nvidia_docker
            build_image
            ;;
        "setup")
            setup_directories
            download_models
            ;;
        "run-interactive")
            check_docker
            check_nvidia_docker
            run_container "interactive"
            ;;
        "run-training")
            check_docker
            check_nvidia_docker
            run_container "training"
            ;;
        "run-dashboard")
            check_docker
            check_nvidia_docker
            run_container "dashboard"
            log_success "Dashboard disponible en: http://localhost:8501"
            ;;
        "run-inference")
            check_docker
            check_nvidia_docker
            run_container "inference"
            ;;
        "stop")
            stop_containers
            ;;
        "clean")
            clean_system
            ;;
        "logs")
            show_logs $2
            ;;
        "status")
            show_status
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            log_error "Opción no válida: $1"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
