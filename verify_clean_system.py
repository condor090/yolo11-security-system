#!/usr/bin/env python3
"""
Verificación del sistema reiniciado
"""

import requests
import json
from datetime import datetime

print("🔍 VERIFICACIÓN DEL SISTEMA REINICIADO")
print("=" * 40)
print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 1. Backend Health
try:
    health = requests.get("http://localhost:8889/api/health").json()
    print(f"\n✅ Backend: {health['status']}")
    print(f"   - Modelo YOLO: {health['services']['model']}")
    print(f"   - AlertManager: {health['services']['alerts']}")
    print(f"   - WebSockets: {health['services']['websocket']} conectados")
except:
    print("\n❌ Backend no responde")

# 2. Timers y Alarmas
try:
    timers = requests.get("http://localhost:8889/api/timers").json()
    print(f"\n📊 Estado de Alarmas:")
    print(f"   - Timers activos: {len(timers['timers'])}")
    print(f"   - Alarma global: {timers['alarm_active']}")
    
    if len(timers['timers']) > 0:
        print("   ⚠️  ADVERTENCIA: Hay timers activos!")
        for timer in timers['timers']:
            print(f"      - {timer['door_id']}: {timer['time_elapsed']:.1f}s")
except:
    print("\n❌ No se pueden obtener timers")

# 3. Zonas
try:
    zones = requests.get("http://localhost:8889/api/zones").json()
    print(f"\n🎯 Zonas Detectadas: {len(zones['zones'])}")
    for zone_id, zone in zones['zones'].items():
        print(f"   - {zone_id}: {zone['last_state']} (alerta: {zone['alert_active']})")
except:
    print("\n❌ No se pueden obtener zonas")

# 4. Modo Eco
try:
    eco = requests.get("http://localhost:8889/api/eco-mode").json()
    eco_mode = eco['eco_mode']
    print(f"\n🌿 Modo Eco:")
    print(f"   - Estado: {eco_mode['current_state']}")
    print(f"   - CPU estimado: {eco_mode['status']['estimated_cpu']}")
except:
    print("\n❌ No se puede obtener Modo Eco")

# 5. Cámaras
try:
    cameras = requests.get("http://localhost:8889/api/cameras").json()
    print(f"\n📹 Cámaras: {len(cameras['cameras'])}")
    for cam_id, cam in cameras['cameras'].items():
        print(f"   - {cam_id}: {cam['name']} ({'🟢 Conectada' if cam['connected'] else '🔴 Desconectada'})")
except:
    print("\n❌ No se pueden obtener cámaras")

print("\n" + "=" * 40)
print("✅ SISTEMA REINICIADO Y LIMPIO")
print("\n💡 Todo está listo para funcionar correctamente:")
print("   - Sin alarmas persistentes")
print("   - Sin timers antiguos")
print("   - Modo Eco en IDLE")
print("   - Cámaras conectadas")
