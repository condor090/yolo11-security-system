#!/usr/bin/env python3
"""
Script para limpiar y verificar el estado del sistema
"""

import requests
import json
import time

API_URL = "http://localhost:8889"

print("=== LIMPIEZA Y VERIFICACIÓN DEL SISTEMA ===\n")

# 1. Detener todas las alarmas
print("1. Limpiando alarmas...")
try:
    response = requests.post(f"{API_URL}/api/alarms/stop-all")
    print(f"   ✓ {response.json()['message']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

time.sleep(1)

# 2. Verificar timers
print("\n2. Verificando timers...")
try:
    response = requests.get(f"{API_URL}/api/timers")
    data = response.json()
    print(f"   Timers activos: {len(data['timers'])}")
    if len(data['timers']) > 0:
        for timer in data['timers']:
            print(f"   - {timer['door_id']} ({timer['camera_id']})")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 3. Verificar zonas
print("\n3. Verificando zonas del sistema de detección...")
try:
    response = requests.get(f"{API_URL}/api/zones")
    data = response.json()
    for zone_id, info in data['zones'].items():
        print(f"   - Zona: {zone_id}")
        print(f"     Estado: {info['last_state']}")
        print(f"     Alerta activa: {info['alert_active']}")
        print(f"     Detecciones: {info['detection_count']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 4. Estado del Modo Eco
print("\n4. Estado del Modo Eco...")
try:
    response = requests.get(f"{API_URL}/api/eco-mode")
    data = response.json()
    eco = data['eco_mode']
    print(f"   Estado: {eco['current_state'].upper()}")
    print(f"   CPU estimado: {eco['status']['estimated_cpu']}")
    print(f"   FPS actual: {eco['status']['config']['fps']}")
    print(f"   YOLO activo: {eco['status']['config']['yolo_enabled']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n=== SISTEMA VERIFICADO ===")
print("\nRECOMENDACIONES:")
print("1. Si persisten alarmas, recargue la página (F5)")
print("2. Para probar detección, mueva algo frente a la cámara")
print("3. El sistema debería detectar automáticamente puertas abiertas/cerradas")
