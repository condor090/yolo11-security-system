#!/usr/bin/env python3
"""
Debug detallado del flujo de detecciones
"""

import requests
import json
import time

print("🔍 DEBUG DETALLADO DEL SISTEMA")
print("=" * 60)

# Primero, limpiar todo
print("1. Limpiando sistema...")
requests.post("http://localhost:8889/api/alarms/stop-all")
time.sleep(1)

print("\n2. Monitoreando detecciones en tiempo real...")
print("   (La puerta debe estar abierta)")
print("-" * 60)

prev_state = None
state_changes = []

for i in range(30):
    try:
        # Obtener todos los datos
        zones = requests.get("http://localhost:8889/api/zones").json()['zones']
        timers = requests.get("http://localhost:8889/api/timers").json()
        
        # Si hay zonas
        if zones:
            for zone_id, zone_data in zones.items():
                current_state = {
                    'state': zone_data['last_state'],
                    'alert': zone_data['alert_active'],
                    'count': zone_data['detection_count']
                }
                
                # Detectar cambios
                if prev_state is None or current_state != prev_state:
                    timestamp = time.strftime('%H:%M:%S')
                    
                    print(f"\n[{timestamp}] CAMBIO DETECTADO:")
                    print(f"  Estado: {current_state['state']}")
                    print(f"  Alerta activa: {current_state['alert']}")
                    print(f"  Total detecciones: {current_state['count']}")
                    
                    if prev_state:
                        print(f"  Cambio: alerta {prev_state['alert']} → {current_state['alert']}")
                    
                    # Registrar cambio
                    state_changes.append({
                        'time': time.time(),
                        'state': current_state['state'],
                        'alert': current_state['alert']
                    })
                    
                    # Mostrar timers
                    print(f"  Timers activos: {len(timers['timers'])}")
                    for timer in timers['timers']:
                        print(f"    - {timer['door_id']}: {timer['time_elapsed']:.1f}s")
                
                prev_state = current_state.copy()
        
        # Punto de progreso
        if i % 5 == 0:
            print(".", end="", flush=True)
            
    except Exception as e:
        print(f"\nError: {e}")
    
    time.sleep(0.5)

# Análisis de patrones
print("\n\n3. ANÁLISIS DE PATRONES:")
print("-" * 60)

if state_changes:
    # Contar oscilaciones
    alert_changes = sum(1 for i in range(1, len(state_changes)) 
                       if state_changes[i]['alert'] != state_changes[i-1]['alert'])
    
    print(f"Total de cambios de estado de alerta: {alert_changes}")
    
    # Mostrar patrón
    print("\nPatrón detectado:")
    for i, change in enumerate(state_changes[-10:]):  # Últimos 10 cambios
        print(f"  {i+1}. Estado: {change['state']}, Alerta: {change['alert']}")
    
    # Calcular frecuencia
    if len(state_changes) > 1:
        time_span = state_changes[-1]['time'] - state_changes[0]['time']
        if time_span > 0:
            freq = alert_changes / time_span
            print(f"\nFrecuencia de cambios: {freq:.2f} cambios/segundo")
            
            if freq > 0.5:
                print("\n⚠️  PROBLEMA DETECTADO: Oscilación rápida de estados")
                print("   Posibles causas:")
                print("   - Detecciones intermitentes del modelo")
                print("   - Lógica de estados incorrecta")
                print("   - Timeouts muy agresivos")

print("\n" + "=" * 60)
print("FIN DEL DEBUG")
