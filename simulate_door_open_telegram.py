#!/usr/bin/env python3
"""
Simular una puerta abierta para activar alarma y Telegram
"""

import cv2
import numpy as np
import requests
import base64
import time

def simulate_door_open():
    """Simular una imagen con puerta abierta para activar el sistema"""
    
    print("🚪 Simulando puerta abierta...")
    
    # Crear imagen que simule una puerta abierta
    # El modelo está entrenado para detectar puertas, así que necesitamos
    # una imagen que se parezca a lo que espera
    
    # Crear imagen base
    img = np.ones((640, 480, 3), dtype=np.uint8) * 200  # Fondo gris claro
    
    # Dibujar rectángulo que simule una puerta abierta
    # Puerta abierta = rectángulo negro (hueco)
    cv2.rectangle(img, (200, 100), (440, 400), (50, 50, 50), -1)  # Puerta oscura
    cv2.rectangle(img, (200, 100), (440, 400), (0, 0, 0), 5)      # Marco
    
    # Agregar algo de textura para que sea más realista
    # Manija
    cv2.circle(img, (420, 250), 10, (150, 150, 150), -1)
    
    # Agregar texto
    cv2.putText(img, "PUERTA ABIERTA - TEST", (150, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Guardar imagen para verificar
    cv2.imwrite('/Users/Shared/yolo11_project/test_door_open.jpg', img)
    print("✅ Imagen guardada en test_door_open.jpg")
    
    # Enviar al endpoint de detección
    _, buffer = cv2.imencode('.jpg', img)
    files = {
        'file': ('door_open.jpg', buffer.tobytes(), 'image/jpeg')
    }
    
    print("\n📤 Enviando al sistema de detección...")
    response = requests.post('http://localhost:8889/api/detect', files=files)
    
    if response.status_code == 200:
        result = response.json()
        detections = result.get('detections', [])
        
        if detections:
            print(f"\n✅ {len(detections)} detección(es) encontrada(s):")
            for det in detections:
                print(f"   - Clase: {det['class_name']}")
                print(f"   - Confianza: {det['confidence']:.2%}")
                print(f"   - ID Puerta: {det['door_id']}")
            
            timers = result.get('timers', [])
            if timers:
                print(f"\n⏰ {len(timers)} timer(s) activo(s):")
                for timer in timers:
                    print(f"   - Zona: {timer.get('zone_name', timer['door_id'])}")
                    print(f"   - Tiempo restante: {timer['time_remaining']}s")
                    
            print("\n📱 Si Telegram está configurado, deberías recibir una notificación")
        else:
            print("\n❌ No se detectaron puertas")
            print("   El modelo puede necesitar una imagen más realista")
            
            # Mostrar imagen anotada si está disponible
            if 'image' in result:
                print("\n📸 Imagen procesada guardada como 'annotated_result.jpg'")
                # Decodificar y guardar
                img_data = result['image'].split(',')[1]
                img_bytes = base64.b64decode(img_data)
                with open('/Users/Shared/yolo11_project/annotated_result.jpg', 'wb') as f:
                    f.write(img_bytes)
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    simulate_door_open()
    
    print("\n⏳ Esperando 5 segundos para dar tiempo al sistema...")
    time.sleep(5)
    
    # Verificar timers activos
    print("\n🔍 Verificando timers activos...")
    timers_resp = requests.get('http://localhost:8889/api/timers')
    if timers_resp.status_code == 200:
        timers = timers_resp.json().get('timers', [])
        if timers:
            print(f"✅ {len(timers)} timer(s) activo(s)")
        else:
            print("❌ No hay timers activos")
