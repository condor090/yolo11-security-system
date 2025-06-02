#!/usr/bin/env python3
"""
Script para configurar las credenciales de la cámara correctamente
"""
import json
import getpass
from pathlib import Path

def configure_camera():
    config_path = Path("/Users/Shared/yolo11_project/backend/cameras/camera_config.json")
    
    # Leer configuración actual
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("🎥 Configurador de Cámara Hikvision")
    print("=" * 60)
    print(f"\nCámara actual: {config['cam_001']['name']}")
    print(f"IP: {config['cam_001']['ip']}")
    print(f"Usuario actual: {config['cam_001']['username']}")
    print()
    
    # Solicitar nuevas credenciales
    print("Ingrese las credenciales correctas:")
    username = input(f"Usuario [{config['cam_001']['username']}]: ").strip()
    if not username:
        username = config['cam_001']['username']
    
    password = getpass.getpass("Contraseña: ")
    if not password:
        print("❌ La contraseña es requerida")
        return
    
    # Actualizar configuración
    config['cam_001']['username'] = username
    config['cam_001']['password'] = password
    
    # Guardar
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Configuración actualizada")
    print("\n🔄 Reiniciando el backend para aplicar cambios...")
    
    # Encontrar y matar el proceso del backend
    import subprocess
    try:
        # Buscar proceso de backend
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'python' in line and 'backend/main.py' in line:
                pid = line.split()[1]
                subprocess.run(['kill', '-9', pid])
                print(f"   Backend detenido (PID: {pid})")
                break
    except:
        pass
    
    print("\n✅ Listo! Las credenciales han sido actualizadas.")
    print("\nPara reiniciar el sistema completo, ejecute:")
    print("   cd /Users/Shared/yolo11_project")
    print("   ./start_system.sh")

if __name__ == "__main__":
    configure_camera()
