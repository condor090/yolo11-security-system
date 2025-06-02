#!/usr/bin/env python3
"""
Script simple para probar las alertas Telegram persistentes
"""

import requests
import time
import json

API_URL = "http://localhost:8889"

print("🚪 YOMJAI - Prueba de Alertas Telegram Persistentes")
print("=" * 50)
print("\nEste test simulará:")
print("1. Una puerta que se abre")
print("2. Timer de 15 segundos (entrada principal)")
print("3. Al expirar, iniciará alertas Telegram cada 5 segundos")
print("\nRevisa tu Telegram para ver los mensajes...")
print("\n⏳ Iniciando prueba...\n")

# Simular puerta abierta
detection_data = {
    "detections": [{
        "class_name": "gate_open",
        "confidence": 0.95,
        "bbox": {"x1": 100, "y1": 100, "x2": 300, "y2": 400},
        "door_id": "entrance_door_0"
    }],
    "camera_id": "cam_001"
}

print("📍 Enviando detección de puerta abierta...")
response = requests.post(f"{API_URL}/api/process-detection", json=detection_data)
print(f"✅ Respuesta: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    timers = result.get('timers', [])
    
    if timers:
        timer = timers[0]
        delay = timer.get('delay_seconds', 15)
        print(f"\n⏱️  Timer activado: {delay} segundos")
        print(f"📍 Zona: Entrada Principal")
        print(f"\n⏳ Esperando que expire el timer...")
        
        # Cuenta regresiva
        for i in range(delay, 0, -1):
            print(f"\r⏰ {i:02d} segundos restantes...", end='', flush=True)
            time.sleep(1)
            
            # Enviar heartbeat cada 3 segundos
            if i % 3 == 0:
                requests.post(f"{API_URL}/api/process-detection", json=detection_data)
        
        print("\n\n🚨 ¡TIMER EXPIRADO!")
        print("📱 Las alertas de Telegram deberían estar activas ahora")
        print("📨 Esperando mensajes cada 5 segundos...\n")
        
        # Mantener la puerta abierta por 30 segundos más
        print("La prueba continuará por 30 segundos más...")
        print("Presiona Ctrl+C para cerrar la puerta y detener las alertas\n")
        
        start_time = time.time()
        try:
            while time.time() - start_time < 30:
                # Enviar heartbeat
                requests.post(f"{API_URL}/api/process-detection", json=detection_data)
                
                elapsed = int(time.time() - start_time)
                print(f"\r⏱️  Prueba en progreso: {elapsed}/30 segundos", end='', flush=True)
                time.sleep(2)
            
            print("\n\n✅ Prueba completada - cerrando puerta...")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrumpido por usuario - cerrando puerta...")
        
        # Cerrar puerta
        closed_data = {
            "detections": [{
                "class_name": "gate_closed",
                "confidence": 0.95,
                "bbox": {"x1": 100, "y1": 100, "x2": 300, "y2": 400},
                "door_id": "entrance_door_0"
            }],
            "camera_id": "cam_001"
        }
        
        response = requests.post(f"{API_URL}/api/process-detection", json=closed_data)
        print("✅ Puerta cerrada - Alertas Telegram canceladas")
        
        # Verificar estado final
        response = requests.get(f"{API_URL}/api/timers")
        final_timers = response.json().get('timers', [])
        
        print(f"\n📊 Estado final:")
        print(f"   - Timers activos: {len(final_timers)}")
        print(f"   - Sistema seguro: {'✅ Sí' if len(final_timers) == 0 else '❌ No'}")
        
print("\n✅ Prueba finalizada")
