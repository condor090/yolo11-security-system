#!/usr/bin/env python3
"""
Simulador de eventos para probar el sistema
Envía detecciones de puertas abiertas al backend
"""

import requests
import time
import json
import base64
from datetime import datetime
import numpy as np
from PIL import Image
import io

def create_test_image(width=640, height=480, door_open=True):
    """Crear imagen de prueba con puerta"""
    # Crear imagen base
    img = Image.new('RGB', (width, height), color='gray')
    
    # Dibujar una puerta (rectángulo)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Posición de la puerta
    door_x = width // 2 - 50
    door_y = height // 2 - 100
    door_width = 100
    door_height = 200
    
    # Color según estado
    door_color = 'red' if door_open else 'green'
    
    # Dibujar puerta
    draw.rectangle(
        [door_x, door_y, door_x + door_width, door_y + door_height],
        outline=door_color,
        width=3,
        fill=door_color if door_open else None
    )
    
    # Agregar texto
    draw.text((10, 10), f"TEST: Puerta {'ABIERTA' if door_open else 'CERRADA'}", fill='white')
    draw.text((10, 30), f"Hora: {datetime.now().strftime('%H:%M:%S')}", fill='white')
    
    return img

def simulate_detection(door_id="door_1", door_open=True):
    """Simular una detección enviándola al backend"""
    print(f"\n🚪 Simulando detección: Puerta {door_id} {'ABIERTA' if door_open else 'CERRADA'}")
    
    # Crear imagen de prueba
    img = create_test_image(door_open=door_open)
    
    # Convertir a bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_bytes = img_buffer.getvalue()
    
    # Enviar al backend
    files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
    
    try:
        # 1. Enviar imagen para detección
        response = requests.post(
            "http://localhost:8888/api/detect",
            files=files,
            params={'confidence': 0.65}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Detección procesada")
            print(f"   📊 Detecciones: {len(result.get('detections', []))}")
            
            # Simular que la detección viene de una cámara específica
            if door_open and result.get('detections'):
                # Enviar evento de puerta abierta vía WebSocket
                print(f"   📡 Simulando evento de {door_id}")
                
                # El backend debería procesar esto automáticamente
                # pero para testing podemos verificar los timers
                time.sleep(1)
                
                # Verificar timers activos
                stats_response = requests.get("http://localhost:8888/api/statistics")
                if stats_response.status_code == 200:
                    stats = stats_response.json().get('statistics', {})
                    print(f"   ⏱️ Timers activos: {stats.get('active_timers', 0)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error enviando detección: {e}")

def run_simulation():
    """Ejecutar simulación completa"""
    print("🎬 INICIANDO SIMULACIÓN DE EVENTOS")
    print("=" * 50)
    
    scenarios = [
        {"door_id": "door_1", "duration": 10, "desc": "Entrada principal - Apertura corta"},
        {"door_id": "loading", "duration": 35, "desc": "Zona de carga - Apertura normal"},
        {"door_id": "emergency", "duration": 65, "desc": "Salida emergencia - Apertura larga"},
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\n📍 Escenario {i+1}: {scenario['desc']}")
        print(f"   Duración planificada: {scenario['duration']}s")
        
        # 1. Abrir puerta
        simulate_detection(scenario['door_id'], door_open=True)
        
        # 2. Esperar
        print(f"   ⏳ Esperando {scenario['duration']}s...")
        for j in range(scenario['duration']):
            if j % 10 == 0:
                print(f"      {j}s transcurridos...")
            time.sleep(1)
        
        # 3. Cerrar puerta
        simulate_detection(scenario['door_id'], door_open=False)
        
        # 4. Pausa entre escenarios
        if i < len(scenarios) - 1:
            print("\n   💤 Pausa de 5s antes del siguiente escenario...")
            time.sleep(5)
    
    print("\n" + "=" * 50)
    print("✅ SIMULACIÓN COMPLETADA")
    print("\n💡 Revisa el dashboard en http://localhost:3000")
    print("   - Tab Monitor: Ver temporizadores y alertas")
    print("   - Tab Dashboard: Ver estadísticas")
    print("   - Botón 'Ver Video Contextual' en cada timer")

if __name__ == "__main__":
    # Verificar que el backend esté corriendo
    try:
        response = requests.get("http://localhost:8888/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend detectado, iniciando simulación...\n")
            run_simulation()
        else:
            print("❌ Backend no responde correctamente")
    except:
        print("❌ Backend no está corriendo")
        print("💡 Ejecuta primero: python3 backend/main.py")
