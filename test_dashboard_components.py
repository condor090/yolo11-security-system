#!/usr/bin/env python3
"""
Script de prueba para verificar que el dashboard funciona correctamente
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ultralytics import YOLO
from PIL import Image
import numpy as np

def test_dashboard_components():
    """Probar los componentes principales del dashboard"""
    
    print("🧪 Iniciando pruebas del dashboard...")
    
    # 1. Probar carga del modelo
    print("\n1. Probando carga del modelo...")
    model_path = Path('runs/gates/gate_detector_v1/weights/best.pt')
    
    if not model_path.exists():
        print(f"❌ ERROR: Modelo no encontrado en {model_path}")
        return False
    
    try:
        model = YOLO(str(model_path))
        print(f"✅ Modelo cargado correctamente")
        print(f"   - Clases: {list(model.names.values())}")
    except Exception as e:
        print(f"❌ ERROR al cargar modelo: {e}")
        return False
    
    # 2. Probar predicción con imagen de prueba
    print("\n2. Probando predicción con imagen...")
    test_image_path = Path('test_images/imagen1.jpg')
    
    if not test_image_path.exists():
        # Usar cualquier imagen de validación
        test_image_path = Path('data/val/images').glob('*.jpg').__next__()
    
    try:
        image = Image.open(test_image_path)
        results = model.predict(image, conf=0.5, verbose=False)
        
        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            for box in results[0].boxes:
                detection = {
                    'class_name': model.names[int(box.cls)],
                    'confidence': float(box.conf)
                }
                detections.append(detection)
        
        print(f"✅ Predicción exitosa")
        print(f"   - Imagen: {test_image_path.name}")
        print(f"   - Detecciones: {len(detections)}")
        
        for i, det in enumerate(detections):
            print(f"   - Detección {i+1}: {det['class_name']} ({det['confidence']:.2%})")
            
    except Exception as e:
        print(f"❌ ERROR en predicción: {e}")
        return False
    
    # 3. Verificar componentes de visualización
    print("\n3. Probando componentes de visualización...")
    try:
        # Obtener imagen anotada
        annotated = results[0].plot()
        print(f"✅ Imagen anotada generada")
        print(f"   - Dimensiones: {annotated.shape}")
        
        # Calcular métricas
        gate_open = sum(1 for d in detections if d['class_name'] == 'gate_open')
        gate_closed = sum(1 for d in detections if d['class_name'] == 'gate_closed')
        avg_conf = np.mean([d['confidence'] for d in detections]) if detections else 0
        
        print(f"✅ Métricas calculadas:")
        print(f"   - Puertas abiertas: {gate_open}")
        print(f"   - Puertas cerradas: {gate_closed}")
        print(f"   - Confianza promedio: {avg_conf:.2%}")
        
    except Exception as e:
        print(f"❌ ERROR en visualización: {e}")
        return False
    
    print("\n✅ TODAS LAS PRUEBAS PASARON")
    print("\nEl dashboard está listo para usar en http://localhost:8502")
    return True

if __name__ == "__main__":
    success = test_dashboard_components()
    sys.exit(0 if success else 1)
