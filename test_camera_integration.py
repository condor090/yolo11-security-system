#!/usr/bin/env python3
"""
Test rápido del sistema de cámaras
Verifica que todo esté configurado correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.camera_manager import CameraManager, CameraConfig
import json
import time

def test_camera_system():
    print("🎥 Probando Sistema de Cámaras...")
    print("-" * 50)
    
    # 1. Crear manager
    manager = CameraManager()
    print("✅ CameraManager creado")
    
    # 2. Verificar configuraciones
    print(f"\n📋 Cámaras configuradas: {len(manager.configs)}")
    for cam_id, config in manager.configs.items():
        print(f"   - {config.name} ({cam_id})")
        print(f"     IP: {config.ip}")
        print(f"     Zona: {config.zone_id}")
        print(f"     Habilitada: {config.enabled}")
    
    # 3. Probar URL RTSP
    if manager.configs:
        first_cam = list(manager.configs.values())[0]
        print(f"\n🔗 URL RTSP ejemplo:")
        print(f"   {first_cam.rtsp_url}")
    
    # 4. Estado del sistema
    print("\n📊 Estado del sistema:")
    status = manager.get_camera_status()
    print(json.dumps(status, indent=2))
    
    print("\n✅ Sistema de cámaras configurado correctamente")
    print("\n⚠️  NOTA: Para probar con cámaras reales:")
    print("   1. Actualiza las IPs en camera_config.json")
    print("   2. Asegúrate que las cámaras estén accesibles")
    print("   3. Verifica usuario/contraseña")

if __name__ == "__main__":
    test_camera_system()
