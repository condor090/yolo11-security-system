#!/usr/bin/env python3
"""
Simular puerta abierta para probar alertas Telegram persistentes
"""

import requests
import time
import json

API_URL = "http://localhost:8889"

def simulate_door_open():
    """Simular una puerta abierta que active las alertas"""
    
    print("🚪 Simulando apertura de puerta...")
    
    # Crear detección de puerta abierta
    detection_data = {
        "detections": [
            {
                "class_name": "gate_open",
                "confidence": 0.95,
                "bbox": {"x1": 100, "y1": 100, "x2": 300, "y2": 400},
                "door_id": "entrance_door_0"
            }
        ],
        "camera_id": "cam_001",
        "timestamp": time.time()
    }
    
    # Enviar detección
    response = requests.post(
        f"{API_URL}/api/process-detection",
        json=detection_data
    )
    
    if response.status_code == 200:
        print("✅ Detección enviada correctamente")
        result = response.json()
        
        # Obtener información del timer
        timers = result.get('timers', [])
        if timers:
            timer = timers[0]
            delay = timer.get('delay_seconds', 15)
            print(f"⏱️  Timer activado: {delay} segundos")
            print(f"📍 Zona: {timer.get('door_id')}")
            
            # Mostrar cuenta regresiva
            print("\n⏳ Esperando que expire el timer para activar Telegram...")
            for i in range(delay, 0, -1):
                print(f"\r⏰ Tiempo restante: {i:02d} segundos", end='', flush=True)
                time.sleep(1)
            
            print("\n\n🚨 ¡TIMER EXPIRADO! Las alertas de Telegram deberían empezar ahora")
            print("📱 Revisa tu Telegram para ver los mensajes persistentes")
            print("\nLa alerta enviará mensajes cada 5 segundos (entrada principal)")
            print("Presiona Ctrl+C para cerrar la puerta y detener las alertas\n")
            
            # Mantener la puerta abierta
            start_time = time.time()
            try:
                while True:
                    # Enviar heartbeat de puerta abierta
                    requests.post(f"{API_URL}/api/process-detection", json=detection_data)
                    
                    elapsed = int(time.time() - start_time)
                    print(f"\r⏱️  Puerta abierta por: {elapsed} segundos", end='', flush=True)
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                print("\n\n🚪 Cerrando puerta...")
                
                # Enviar detección de puerta cerrada
                closed_data = {
                    "detections": [
                        {
                            "class_name": "gate_closed",
                            "confidence": 0.95,
                            "bbox": {"x1": 100, "y1": 100, "x2": 300, "y2": 400},
                            "door_id": "entrance_door_0"
                        }
                    ],
                    "camera_id": "cam_001",
                    "timestamp": time.time()
                }
                
                response = requests.post(f"{API_URL}/api/process-detection", json=closed_data)
                if response.status_code == 200:
                    print("✅ Puerta cerrada - Alertas canceladas")
                else:
                    print("❌ Error cerrando puerta")
        else:
            print("⚠️  No se activó ningún timer")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("🚀 YOMJAI - Prueba de Alertas Telegram Persistentes")
    print("=" * 50)
    print("\nEste script simulará una puerta abierta que:")
    print("1. Activará un timer de 15 segundos")
    print("2. Al expirar, iniciará alertas Telegram persistentes")
    print("3. Enviará mensajes cada 5 segundos")
    print("4. Presiona Ctrl+C para cerrar la puerta\n")
    
    input("Presiona ENTER para comenzar...")
    
    simulate_door_open()
