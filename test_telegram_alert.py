#!/usr/bin/env python3
"""
Script para simular una detección y verificar envío a Telegram
"""

import requests
import time
import json
from PIL import Image
import numpy as np
import base64
import io

def test_telegram_alert():
    """Simular una detección de puerta abierta y verificar alerta"""
    
    # Primero verificar configuración
    print("1. Verificando configuración de Telegram...")
    config_resp = requests.get("http://localhost:8889/api/config")
    config = config_resp.json()['config']
    
    telegram_config = config.get('telegram', {})
    print(f"   - Habilitado: {telegram_config.get('enabled', False)}")
    print(f"   - Chat ID: {telegram_config.get('chat_id', 'No configurado')}")
    
    # Crear imagen de prueba
    print("\n2. Creando imagen de prueba con puerta abierta...")
    # Imagen roja para simular detección
    img = Image.new('RGB', (640, 480), color='red')
    
    # Convertir a bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Preparar archivo para subir
    files = {
        'file': ('test_door.jpg', img_byte_arr, 'image/jpeg')
    }
    
    print("\n3. Enviando imagen al endpoint de detección...")
    detect_resp = requests.post(
        "http://localhost:8889/api/detect",
        files=files
    )
    
    if detect_resp.status_code == 200:
        result = detect_resp.json()
        print(f"   - Detecciones encontradas: {len(result.get('detections', []))}")
        
        # Verificar si se detectó algo
        if result.get('detections'):
            print("   ✅ Detección procesada correctamente")
            print(f"   - Timers activos: {len(result.get('timers', []))}")
            
            # Esperar un momento para que se envíe el telegram
            print("\n4. Esperando envío de Telegram...")
            time.sleep(2)
            
            print("\n✅ Si Telegram está configurado correctamente, deberías haber recibido una notificación")
        else:
            print("   ❌ No se detectaron puertas (el modelo necesita una imagen real)")
    else:
        print(f"   ❌ Error: {detect_resp.status_code}")
        print(f"   - Detalle: {detect_resp.text}")
    
    # Alternativa: Enviar mensaje de prueba directo
    print("\n5. Enviando mensaje de prueba directo...")
    test_resp = requests.post("http://localhost:8889/api/telegram/test", 
                             json=telegram_config)
    
    if test_resp.status_code == 200:
        print("   ✅ Mensaje de prueba enviado correctamente")
    else:
        print(f"   ❌ Error enviando mensaje de prueba: {test_resp.text}")

if __name__ == "__main__":
    test_telegram_alert()
