#!/usr/bin/env python3
"""
Script de prueba para el sistema de deduplicación de alarmas
"""

import asyncio
import time
from backend.utils.detection_manager import DetectionManager


async def test_detection_manager():
    """Prueba el DetectionManager con escenarios comunes"""
    
    print("=== PRUEBA DE DETECTION MANAGER ===\n")
    
    dm = DetectionManager(state_timeout=2.0, min_confidence=0.75)
    
    # Escenario 1: Múltiples detecciones de la misma puerta abierta
    print("Escenario 1: Múltiples detecciones de puerta abierta")
    print("-" * 50)
    
    # Frame 1: Detecta puerta abierta
    detections1 = [{
        'class_name': 'gate_open',
        'confidence': 0.85,
        'door_id': 'door_1',
        'bbox': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}
    }]
    
    actions = dm.process_frame_detections(detections1, 'cam_001')
    print(f"Frame 1 - Acciones: {len(actions)}")
    for action in actions:
        print(f"  - {action['action']} para {action['zone_id']}")
    
    # Frame 2: Misma puerta abierta (no debe crear nueva alarma)
    await asyncio.sleep(0.1)
    actions = dm.process_frame_detections(detections1, 'cam_001')
    print(f"Frame 2 - Acciones: {len(actions)} (debe ser 0)")
    
    # Frame 3: Misma puerta abierta
    await asyncio.sleep(0.1)
    actions = dm.process_frame_detections(detections1, 'cam_001')
    print(f"Frame 3 - Acciones: {len(actions)} (debe ser 0)")
    
    print(f"\nEstado de zonas: {dm.get_zone_states()}")
    
    # Escenario 2: Puerta se cierra
    print("\n\nEscenario 2: Puerta se cierra")
    print("-" * 50)
    
    detections2 = [{
        'class_name': 'gate_closed',
        'confidence': 0.90,
        'door_id': 'door_1',
        'bbox': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}
    }]
    
    actions = dm.process_frame_detections(detections2, 'cam_001')
    print(f"Acciones: {len(actions)}")
    for action in actions:
        print(f"  - {action['action']} para {action['zone_id']}")
    
    print(f"\nEstado de zonas: {dm.get_zone_states()}")
    
    # Escenario 3: Timeout sin detecciones
    print("\n\nEscenario 3: Timeout (2.5 segundos sin detecciones)")
    print("-" * 50)
    
    # Crear nueva alarma
    detections3 = [{
        'class_name': 'gate_open',
        'confidence': 0.80,
        'door_id': 'door_2',
        'bbox': {'x1': 300, 'y1': 100, 'x2': 400, 'y2': 200}
    }]
    
    actions = dm.process_frame_detections(detections3, 'cam_001')
    print(f"Nueva alarma creada: {len(actions)} acciones")
    
    # Esperar timeout
    print("Esperando timeout...")
    await asyncio.sleep(2.5)
    
    # Frame sin detecciones
    actions = dm.process_frame_detections([], 'cam_001')
    print(f"Después del timeout: {len(actions)} acciones")
    for action in actions:
        print(f"  - {action['action']} para {action['zone_id']}")
    
    print(f"\nEstado final de zonas: {dm.get_zone_states()}")
    
    # Escenario 4: Múltiples puertas
    print("\n\nEscenario 4: Múltiples puertas detectadas")
    print("-" * 50)
    
    dm.reset_all()
    
    detections4 = [
        {
            'class_name': 'gate_open',
            'confidence': 0.85,
            'door_id': 'door_1',
            'bbox': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}
        },
        {
            'class_name': 'gate_open',
            'confidence': 0.88,
            'door_id': 'door_2',
            'bbox': {'x1': 300, 'y1': 100, 'x2': 400, 'y2': 200}
        }
    ]
    
    actions = dm.process_frame_detections(detections4, 'cam_001')
    print(f"Acciones para 2 puertas: {len(actions)}")
    for action in actions:
        print(f"  - {action['action']} para {action['zone_id']}")
    
    print(f"\nEstado de zonas: {dm.get_zone_states()}")
    
    print("\n=== PRUEBA COMPLETADA ===")


if __name__ == "__main__":
    asyncio.run(test_detection_manager())
