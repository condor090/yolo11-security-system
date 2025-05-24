#!/usr/bin/env python3
"""
Script de verificación del sistema YOLO11 Security
Verifica que todos los componentes estén correctamente instalados y configurados
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import yaml

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def check_system_requirements():
    """Verificar requisitos del sistema"""
    print_header("VERIFICACIÓN DE REQUISITOS DEL SISTEMA")
    
    # Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print_error(f"Python {python_version.major}.{python_version.minor} - Se requiere Python 3.8+")
    
    # Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"Docker: {result.stdout.strip()}")
        else:
            print_error("Docker no encontrado")
    except FileNotFoundError:
        print_error("Docker no está instalado")
    
    # Docker Compose
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"Docker Compose: {result.stdout.strip()}")
        else:
            print_warning("Docker Compose no encontrado (opcional)")
    except FileNotFoundError:
        print_warning("Docker Compose no está instalado (opcional)")
    
    # NVIDIA Docker (opcional)
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("NVIDIA GPU detectada")
            print_info("Ejecutando test de NVIDIA Docker...")
            gpu_test = subprocess.run([
                'docker', 'run', '--rm', '--gpus', 'all', 
                'nvidia/cuda:11.0-base', 'nvidia-smi'
            ], capture_output=True, text=True)
            if gpu_test.returncode == 0:
                print_success("NVIDIA Docker configurado correctamente")
            else:
                print_warning("NVIDIA Docker no configurado - usando CPU")
        else:
            print_info("GPU NVIDIA no disponible - usando CPU")
    except FileNotFoundError:
        print_info("nvidia-smi no encontrado - usando CPU")

def check_project_structure():
    """Verificar estructura del proyecto"""
    print_header("VERIFICACIÓN DE ESTRUCTURA DEL PROYECTO")
    
    base_path = Path("/Users/Shared/yolo11_project")
    
    required_files = [
        "Dockerfile.security",
        "docker-compose.yml", 
        "deploy.sh",
        "README.md",
        "TESTING_GUIDE.md"
    ]
    
    required_dirs = [
        "ultralytics-main",
        "project_files",
        "project_files/scripts",
        "project_files/configs",
        "project_files/apps"
    ]
    
    # Verificar archivos
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print_success(f"Archivo: {file_path}")
        else:
            print_error(f"Archivo faltante: {file_path}")
    
    # Verificar directorios
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists() and full_path.is_dir():
            print_success(f"Directorio: {dir_path}")
        else:
            print_error(f"Directorio faltante: {dir_path}")

def check_configuration_files():
    """Verificar archivos de configuración"""
    print_header("VERIFICACIÓN DE ARCHIVOS DE CONFIGURACIÓN")
    
    base_path = Path("/Users/Shared/yolo11_project")
    
    # Verificar configuración del dataset
    config_file = base_path / "project_files/configs/security_dataset.yaml"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            print_success("Configuración del dataset cargada")
            print_info(f"  - Número de clases: {config.get('nc', 'No especificado')}")
            print_info(f"  - Clases: {list(config.get('names', {}).values())}")
            
            if 'train_config' in config:
                train_cfg = config['train_config']
                print_info(f"  - Épocas: {train_cfg.get('epochs', 'No especificado')}")
                print_info(f"  - Batch size: {train_cfg.get('batch_size', 'No especificado')}")
        
        except Exception as e:
            print_error(f"Error leyendo configuración: {e}")
    else:
        print_error("Archivo de configuración no encontrado")

def check_docker_setup():
    """Verificar configuración de Docker"""
    print_header("VERIFICACIÓN DE CONFIGURACIÓN DOCKER")
    
    base_path = Path("/Users/Shared/yolo11_project")
    
    # Verificar Dockerfile
    dockerfile = base_path / "Dockerfile.security"
    if dockerfile.exists():
        print_success("Dockerfile.security encontrado")
        # Verificar contenido básico
        with open(dockerfile, 'r') as f:
            content = f.read()
            if 'FROM pytorch/pytorch' in content:
                print_success("  - Base image correcta (PyTorch)")
            if 'YOLO11' in content or 'yolo11' in content:
                print_success("  - Configurado para YOLO11")
    else:
        print_error("Dockerfile.security no encontrado")
    
    # Verificar docker-compose
    compose_file = base_path / "docker-compose.yml"
    if compose_file.exists():
        print_success("docker-compose.yml encontrado")
        try:
            with open(compose_file, 'r') as f:
                content = f.read()
                if 'yolo11-dashboard' in content:
                    print_success("  - Servicio dashboard configurado")
                if 'yolo11-training' in content:
                    print_success("  - Servicio training configurado")
        except Exception as e:
            print_warning(f"Error leyendo docker-compose.yml: {e}")
    else:
        print_warning("docker-compose.yml no encontrado (opcional)")

def check_scripts():
    """Verificar scripts principales"""
    print_header("VERIFICACIÓN DE SCRIPTS")
    
    base_path = Path("/Users/Shared/yolo11_project")
    scripts_dir = base_path / "project_files/scripts"
    
    required_scripts = [
        "security_system.py",
        "train_security_model.py", 
        "data_utils.py"
    ]
    
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print_success(f"Script: {script}")
            # Verificar que es ejecutable (contiene shebang o main)
            with open(script_path, 'r') as f:
                content = f.read()
                if 'if __name__ == "__main__"' in content or content.startswith('#!/'):
                    print_info(f"  - {script} es ejecutable")
        else:
            print_error(f"Script faltante: {script}")
    
    # Verificar deploy.sh
    deploy_script = base_path / "deploy.sh"
    if deploy_script.exists():
        print_success("deploy.sh encontrado")
        if os.access(deploy_script, os.X_OK):
            print_success("  - deploy.sh es ejecutable")
        else:
            print_warning("  - deploy.sh no es ejecutable (ejecutar: chmod +x deploy.sh)")
    else:
        print_error("deploy.sh no encontrado")

def create_data_directories():
    """Crear directorios de datos si no existen"""
    print_header("CONFIGURACIÓN DE DIRECTORIOS DE DATOS")
    
    base_path = Path("/Users/Shared/yolo11_project")
    
    directories = [
        "data/train/images",
        "data/train/labels", 
        "data/val/images",
        "data/val/labels",
        "data/test/images",
        "data/test/labels",
        "data/test_images",
        "models",
        "runs",
        "logs",
        "exports",
        "notebooks"
    ]
    
    created_dirs = []
    for dir_path in directories:
        full_path = base_path / dir_path
        if not full_path.exists():
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(dir_path)
            except Exception as e:
                print_error(f"Error creando {dir_path}: {e}")
        else:
            print_success(f"Directorio existe: {dir_path}")
    
    if created_dirs:
        print_info(f"Directorios creados: {len(created_dirs)}")
        for dir_path in created_dirs:
            print_info(f"  - {dir_path}")

def test_docker_build():
    """Probar construcción de Docker (sin ejecutar)"""
    print_header("PRUEBA DE CONSTRUCCIÓN DOCKER")
    
    base_path = Path("/Users/Shared/yolo11_project")
    dockerfile = base_path / "Dockerfile.security"
    
    if not dockerfile.exists():
        print_error("Dockerfile.security no encontrado")
        return
    
    print_info("Verificando sintaxis del Dockerfile...")
    try:
        # Verificar sintaxis básica
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        # Verificaciones básicas
        if content.startswith('FROM'):
            print_success("Dockerfile tiene FROM statement válido")
        else:
            print_error("Dockerfile no tiene FROM statement al inicio")
        
        if 'WORKDIR' in content:
            print_success("WORKDIR especificado")
        
        if 'COPY' in content or 'ADD' in content:
            print_success("Instrucciones de copia encontradas")
        
        if 'RUN' in content:
            print_success("Instrucciones RUN encontradas")
        
        print_info("Sintaxis del Dockerfile parece correcta")
        print_warning("Para construir la imagen, ejecuta: ./deploy.sh build")
        
    except Exception as e:
        print_error(f"Error verificando Dockerfile: {e}")

def generate_test_report():
    """Generar reporte de configuración"""
    print_header("GENERANDO REPORTE DE CONFIGURACIÓN")
    
    base_path = Path("/Users/Shared/yolo11_project")
    report_file = base_path / "system_check_report.json"
    
    report = {
        "timestamp": subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "system_info": {},
        "docker_available": False,
        "gpu_available": False,
        "project_structure": {
            "complete": True,
            "missing_files": []
        }
    }
    
    # Docker check
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        report["docker_available"] = result.returncode == 0
        if result.returncode == 0:
            report["docker_version"] = result.stdout.strip()
    except:
        pass
    
    # GPU check
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        report["gpu_available"] = result.returncode == 0
    except:
        pass
    
    # Verificar archivos requeridos
    required_files = [
        "Dockerfile.security",
        "docker-compose.yml",
        "deploy.sh",
        "project_files/scripts/security_system.py",
        "project_files/configs/security_dataset.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (base_path / file_path).exists():
            missing_files.append(file_path)
    
    report["project_structure"]["missing_files"] = missing_files
    report["project_structure"]["complete"] = len(missing_files) == 0
    
    # Guardar reporte
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print_success(f"Reporte guardado en: {report_file}")
    except Exception as e:
        print_error(f"Error guardando reporte: {e}")
    
    return report

def show_next_steps(report):
    """Mostrar próximos pasos basados en la verificación"""
    print_header("PRÓXIMOS PASOS RECOMENDADOS")
    
    if not report["docker_available"]:
        print_error("CRÍTICO: Docker no está disponible")
        print_info("1. Instalar Docker: https://docs.docker.com/get-docker/")
        print_info("2. Reiniciar este script después de la instalación")
        return
    
    if not report["project_structure"]["complete"]:
        print_warning("Estructura del proyecto incompleta")
        missing = report["project_structure"]["missing_files"]
        print_info(f"Archivos faltantes: {', '.join(missing)}")
        return
    
    print_success("Sistema listo para usar!")
    print_info("\nPasos para comenzar:")
    print_info("1. Construir imagen Docker:")
    print_info("   ./deploy.sh build")
    print_info("")
    print_info("2. Configurar directorios:")
    print_info("   ./deploy.sh setup")
    print_info("")
    print_info("3. Iniciar dashboard web:")
    print_info("   ./deploy.sh run-dashboard")
    print_info("   Acceder a: http://localhost:8501")
    print_info("")
    print_info("4. Para modo interactivo:")
    print_info("   ./deploy.sh run-interactive")
    
    if not report["gpu_available"]:
        print_warning("\nNOTA: GPU no disponible - el sistema usará CPU")
        print_info("Para mejor rendimiento, considera configurar NVIDIA Docker")
    else:
        print_success("\nGPU disponible - rendimiento optimizado")

def main():
    """Función principal"""
    print("🔍 YOLO11 Security System - Verificación del Sistema")
    print("="*60)
    
    # Ejecutar todas las verificaciones
    check_system_requirements()
    check_project_structure()
    check_configuration_files()
    check_docker_setup()
    check_scripts()
    create_data_directories()
    test_docker_build()
    
    # Generar reporte
    report = generate_test_report()
    
    # Mostrar próximos pasos
    show_next_steps(report)
    
    print_header("VERIFICACIÓN COMPLETADA")
    
    if report["project_structure"]["complete"] and report["docker_available"]:
        print_success("✨ Sistema listo para usar!")
        print_info("Consulta TESTING_GUIDE.md para instrucciones detalladas")
    else:
        print_warning("⚠️  Se requieren acciones adicionales antes de usar el sistema")
    
    print_info(f"Reporte detallado guardado en: system_check_report.json")

if __name__ == "__main__":
    main()
