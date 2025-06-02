#!/usr/bin/env python3
"""
Debug: Ver qué está pasando exactamente
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import time

# Cargar modelo
model_path = Path(__file__).parent / 'runs' / 'gates' / 'gate_detector_v1' / 'weights' / 'best.pt'
model = YOLO(str(model_path))

# Obtener frame de la cámara vía API
import requests
import base64

print("🔍 ANALIZANDO DETECCIONES DIRECTAMENTE")
print("=" * 50)

for i in range(10):
    try:
        # Obtener frame actual
        resp = requests.get("http://localhost:8889/api/cameras/cam_001/stream")
        if resp.status_code == 200:
            data = resp.json()
            
            # Decodificar imagen
            img_data = data['image'].split(',')[1]
            img_bytes = base64.b64decode(img_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Detectar
            results = model.predict(frame, conf=0.75, verbose=False)
            
            print(f"\n[Intento {i+1}]")
            
            if len(results) > 0 and results[0].boxes is not None:
                print(f"Detecciones encontradas: {len(results[0].boxes)}")
                
                for j, box in enumerate(results[0].boxes):
                    class_name = model.names[int(box.cls)]
                    confidence = float(box.conf)
                    print(f"  {j+1}. {class_name}: {confidence:.2%}")
            else:
                print("No se detectaron objetos")
                
        time.sleep(2)
        
    except Exception as e:
        print(f"Error: {e}")
        
print("\n¿El modelo está detectando consistentemente o hay variaciones?")
