#!/usr/bin/env python3
"""
Test directo del sistema - verificación rápida
"""

import requests
import time
import json
import os

def test_system():
    print("🧪 PRUEBA DEL SISTEMA YOLO11 SECURITY")
    print("=" * 50)
    
    # 1. Verificar si el backend está corriendo
    print("\n1️⃣ Verificando Backend...")
    try:
        response = requests.get("http://localhost:8888/api/health", timeout=2)
        if response.status_code == 200:
            print("   ✅ Backend está activo")
            data = response.json()
            print(f"   📊 Estado: {data}")
        else:
            print("   ❌ Backend responde pero con error:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("   ❌ Backend NO está corriendo")
        print("   💡 Ejecuta: python3 backend/main.py")
        return False
    
    # 2. Verificar cámaras
    print("\n2️⃣ Verificando Cámaras...")
    try:
        response = requests.get("http://localhost:8888/api/cameras", timeout=2)
        if response.status_code == 200:
            cameras = response.json().get('cameras', {})
            print(f"   ✅ {len(cameras)} cámaras configuradas")
            for cam_id, cam_info in cameras.items():
                status = "🟢 Conectada" if cam_info.get('connected') else "🔴 Desconectada"
                print(f"   - {cam_info['name']} ({cam_id}): {status}")
        else:
            print("   ❌ Error obteniendo cámaras")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar frontend
    print("\n3️⃣ Verificando Frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        if response.status_code == 200:
            print("   ✅ Frontend está activo")
        else:
            print("   ⚠️ Frontend responde pero con error:", response.status_code)
    except requests.exceptions.RequestException:
        print("   ❌ Frontend NO está corriendo")
        print("   💡 Ejecuta: cd frontend && npm start")
    
    # 4. Verificar WebSocket
    print("\n4️⃣ Verificando WebSocket...")
    print("   ℹ️ WebSocket en ws://localhost:8888/ws")
    print("   💡 Se conecta automáticamente desde el frontend")
    
    # 5. Archivos de configuración
    print("\n5️⃣ Verificando Configuración...")
    configs = [
        ("cameras/camera_config.json", "Cámaras"),
        ("alerts/alert_config_v2.json", "Alertas"),
    ]
    
    for config_file, name in configs:
        if os.path.exists(config_file):
            print(f"   ✅ {name}: {config_file}")
            with open(config_file, 'r') as f:
                data = json.load(f)
                print(f"      Entradas: {len(data)}")
        else:
            print(f"   ❌ {name}: {config_file} NO encontrado")
    
    print("\n" + "=" * 50)
    print("📝 RESUMEN:")
    print("- Backend: http://localhost:8888")
    print("- Frontend: http://localhost:3000")
    print("- WebSocket: ws://localhost:8888/ws")
    print("\n💡 Para iniciar el sistema completo:")
    print("1. Terminal 1: python3 backend/main.py")
    print("2. Terminal 2: cd frontend && npm start")
    print("3. Abrir navegador en http://localhost:3000")
    
    return True

if __name__ == "__main__":
    test_system()
