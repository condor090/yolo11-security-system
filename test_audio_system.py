#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de audio multi-fase
Simula una detección de puerta abierta y verifica que las alarmas sonoras se activen
"""

import requests
import time
import json

API_URL = "http://localhost:8889"

def test_audio_system():
    print("🧪 Iniciando prueba del sistema de audio multi-fase...")
    
    # 1. Verificar estado del audio
    print("\n1️⃣ Verificando estado del servicio de audio...")
    response = requests.get(f"{API_URL}/api/audio/status")
    audio_status = response.json()
    print(f"   Audio habilitado: {audio_status['enabled']}")
    print(f"   Audio disponible: {audio_status['available']}")
    print(f"   Alarmas activas: {len(audio_status['active_alarms'])}")
    
    # 2. Simular detección de puerta abierta
    print("\n2️⃣ Simulando detección de puerta abierta...")
    
    # Crear imagen de prueba (1x1 pixel negro)
    import base64
    from io import BytesIO
    from PIL import Image
    
    img = Image.new('RGB', (640, 480), color='black')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    
    files = {'file': ('test.jpg', buffer, 'image/jpeg')}
    
    # Enviar para detección (esto creará un timer aunque no detecte nada real)
    response = requests.post(f"{API_URL}/api/detect", files=files)
    print(f"   Respuesta: {response.status_code}")
    
    # 3. Monitorear timers por 2 minutos
    print("\n3️⃣ Monitoreando timers y fases de audio...")
    print("   Fase 1 (Verde): 0-30s - Ding dong suave")
    print("   Fase 2 (Amarillo): 30s-2min - Beep intermitente")
    print("   Fase 3 (Rojo): >2min - Sirena continua")
    print("\n   Tiempo | Fase | Alarmas Sonoras")
    print("   -------|------|----------------")
    
    start_time = time.time()
    
    while time.time() - start_time < 150:  # 2.5 minutos
        elapsed = int(time.time() - start_time)
        
        # Obtener estado de timers
        response = requests.get(f"{API_URL}/api/timers")
        timers = response.json()['timers']
        
        # Obtener estado de audio
        response = requests.get(f"{API_URL}/api/audio/status")
        audio_status = response.json()
        active_alarms = audio_status['active_alarms']
        
        # Determinar fase
        if elapsed < 30:
            phase = "🟢 Friendly"
        elif elapsed < 120:
            phase = "🟡 Moderate"
        else:
            phase = "🔴 Critical"
        
        print(f"   {elapsed:3d}s   | {phase} | {len(active_alarms)} alarmas activas")
        
        # Si hay timers, mostrar detalles
        for timer in timers:
            print(f"          └─ {timer['door_id']}: {timer.get('current_phase', 'unknown')} phase")
        
        time.sleep(5)
    
    # 4. Detener todas las alarmas
    print("\n4️⃣ Deteniendo todas las alarmas...")
    response = requests.post(f"{API_URL}/api/alarms/stop-all")
    print(f"   Respuesta: {response.status_code}")
    
    print("\n✅ Prueba completada!")

if __name__ == "__main__":
    test_audio_system()
