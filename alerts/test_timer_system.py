#!/usr/bin/env python3
"""
Script de prueba para el sistema de alertas con temporizadores
Simula detección de puertas abiertas y verifica el comportamiento de los temporizadores
"""

import asyncio
import time
import sys
from pathlib import Path

# Añadir ruta para importar AlertManager
sys.path.append(str(Path(__file__).parent))
from alert_manager_v2 import AlertManager

async def test_timer_system():
    """Prueba completa del sistema de temporizadores"""
    
    print("🧪 INICIANDO PRUEBA DEL SISTEMA DE TEMPORIZADORES")
    print("=" * 60)
    
    # Crear manager con configuración de prueba
    manager = AlertManager()
    
    # Configurar delays cortos para prueba rápida
    manager.config['timer_delays'] = {
        'default': 10,  # 10 segundos por defecto
        'test_door_1': 5,   # 5 segundos
        'test_door_2': 15   # 15 segundos
    }
    manager.config['sound_enabled'] = False  # Desactivar sonido para prueba
    
    print("\n📋 Configuración de prueba:")
    print(f"  - test_door_1: {manager.config['timer_delays']['test_door_1']}s")
    print(f"  - test_door_2: {manager.config['timer_delays']['test_door_2']}s")
    
    # Caso 1: Puerta abierta que activa alarma
    print("\n\n🔴 CASO 1: Puerta que permanece abierta (debe activar alarma)")
    print("-" * 60)
    
    detections_case1 = [{
        'class_name': 'gate_open',
        'confidence': 0.85,
        'bbox': {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400},
        'door_id': 'test_door_1'
    }]
    
    print("Simulando detección de puerta abierta...")
    await manager.process_detection(detections_case1, camera_id='test_cam')
    
    # Monitorear por 7 segundos (más que el delay de 5s)
    for i in range(7):
        await asyncio.sleep(1)
        timers = manager.get_active_timers()
        if timers:
            timer = timers[0]
            print(f"  Tiempo: {i+1}s - Elapsed: {timer['time_elapsed']:.1f}s / {timer['delay_seconds']}s - " +
                  f"Alarma: {'SÍ' if timer['alarm_triggered'] else 'NO'}")
    
    # Caso 2: Puerta que se cierra antes del tiempo
    print("\n\n🟢 CASO 2: Puerta que se cierra antes del tiempo (no debe activar alarma)")
    print("-" * 60)
    
    detections_case2_open = [{
        'class_name': 'gate_open',
        'confidence': 0.90,
        'bbox': {'x1': 400, 'y1': 200, 'x2': 600, 'y2': 400},
        'door_id': 'test_door_2'
    }]
    
    print("Simulando detección de puerta abierta...")
    await manager.process_detection(detections_case2_open, camera_id='test_cam')
    
    # Esperar 8 segundos
    for i in range(8):
        await asyncio.sleep(1)
        timers = manager.get_active_timers()
        timer_info = next((t for t in timers if t['door_id'] == 'test_door_2'), None)
        if timer_info:
            print(f"  Tiempo: {i+1}s - Elapsed: {timer_info['time_elapsed']:.1f}s / {timer_info['delay_seconds']}s")
    
    # Simular cierre de puerta
    detections_case2_closed = [{
        'class_name': 'gate_closed',
        'confidence': 0.95,
        'bbox': {'x1': 400, 'y1': 200, 'x2': 600, 'y2': 400},
        'door_id': 'test_door_2'
    }]
    
    print("\n  ✅ Simulando cierre de puerta...")
    await manager.process_detection(detections_case2_closed, camera_id='test_cam')
    
    # Verificar que el temporizador fue cancelado
    timers = manager.get_active_timers()
    timer_exists = any(t['door_id'] == 'test_door_2' for t in timers)
    print(f"  Temporizador cancelado: {'NO' if timer_exists else 'SÍ'}")
    
    # Caso 3: Múltiples puertas simultáneas
    print("\n\n🔶 CASO 3: Múltiples puertas con diferentes delays")
    print("-" * 60)
    
    detections_multiple = [
        {
            'class_name': 'gate_open',
            'confidence': 0.75,
            'bbox': {'x1': 0, 'y1': 0, 'x2': 100, 'y2': 100},
            'door_id': 'door_a'
        },
        {
            'class_name': 'gate_open',
            'confidence': 0.80,
            'bbox': {'x1': 200, 'y1': 0, 'x2': 300, 'y2': 100},
            'door_id': 'door_b'
        }
    ]
    
    print("Simulando detección de múltiples puertas abiertas...")
    await manager.process_detection(detections_multiple, camera_id='multi_cam')
    
    # Monitorear brevemente
    await asyncio.sleep(2)
    timers = manager.get_active_timers()
    print(f"\n  Temporizadores activos: {len(timers)}")
    for timer in timers:
        print(f"  - {timer['door_id']}: {timer['time_elapsed']:.1f}s / {timer['delay_seconds']}s")
    
    # Resumen final
    print("\n\n📊 RESUMEN DE LA PRUEBA")
    print("=" * 60)
    
    alert_history = manager.alert_history
    print(f"Total de alertas generadas: {len(alert_history)}")
    
    for alert in alert_history:
        print(f"  - {alert.id}: {alert.message}")
    
    timers_active = manager.get_active_timers()
    print(f"\nTemporizadores aún activos: {len(timers_active)}")
    
    # Detener todas las alarmas
    manager.stop_all_alarms()
    
    print("\n✅ Prueba completada")

def test_timer_delays():
    """Prueba rápida de configuración de delays"""
    print("\n🔧 PRUEBA DE CONFIGURACIÓN DE DELAYS")
    print("=" * 60)
    
    manager = AlertManager()
    
    # Probar diferentes configuraciones
    test_cases = [
        ("default", "default"),
        ("entrance", "cam1"),
        ("loading", "cam2"),
        ("unknown", "cam_xyz")
    ]
    
    for door_id, camera_id in test_cases:
        delay = manager.get_timer_delay(door_id, camera_id)
        print(f"Door: {door_id}, Camera: {camera_id} → Delay: {delay}s")

if __name__ == "__main__":
    # Ejecutar pruebas
    print("Sistema de Alertas con Temporizadores - Pruebas")
    
    # Prueba de configuración
    test_timer_delays()
    
    # Prueba completa del sistema
    asyncio.run(test_timer_system())
