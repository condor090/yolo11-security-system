#!/usr/bin/env python3
"""
Monitor de detecciones YOLO en tiempo real
"""

import requests
import time
import json

print("🔍 MONITOR DE DETECCIONES YOLO")
print("=" * 50)

prev_zones = {}
detection_history = []

for i in range(60):
    try:
        # Obtener zonas
        zones_resp = requests.get("http://localhost:8889/api/zones")
        zones = zones_resp.json()['zones']
        
        # Obtener eco mode
        eco_resp = requests.get("http://localhost:8889/api/eco-mode")
        eco_state = eco_resp.json()['eco_mode']['current_state']
        
        # Analizar cada zona
        for zone_id, zone_data in zones.items():
            # Registrar detección
            detection = {
                'time': time.time(),
                'state': zone_data['last_state'],
                'confidence': zone_data['average_confidence'],
                'count': zone_data['detection_count']
            }
            
            # Verificar cambios
            if zone_id not in prev_zones or prev_zones[zone_id]['last_state'] != zone_data['last_state']:
                print(f"\n[{time.strftime('%H:%M:%S')}] CAMBIO DE ESTADO:")
                print(f"  Zona: {zone_id}")
                print(f"  Estado: {zone_data['last_state']}")
                print(f"  Confianza: {zone_data['average_confidence']:.2%}")
                print(f"  Modo Eco: {eco_state}")
            
            # Analizar oscilaciones
            detection_history.append((zone_data['last_state'], time.time()))
            
            # Mantener solo últimos 10 segundos
            detection_history = [(s, t) for s, t in detection_history if time.time() - t < 10]
            
            # Detectar oscilaciones rápidas
            if len(detection_history) > 10:
                changes = sum(1 for i in range(1, len(detection_history)) 
                            if detection_history[i][0] != detection_history[i-1][0])
                
                if changes > 5:
                    print(f"\n⚠️  OSCILACIÓN DETECTADA: {changes} cambios en 10 segundos")
                    
                    # Contar estados
                    open_count = sum(1 for s, _ in detection_history if s == 'gate_open')
                    closed_count = sum(1 for s, _ in detection_history if s == 'gate_closed')
                    
                    print(f"  Detecciones gate_open: {open_count}")
                    print(f"  Detecciones gate_closed: {closed_count}")
                    
                    # Limpiar historial
                    detection_history = []
        
        prev_zones = zones.copy()
        
        # Mostrar resumen cada 5 segundos
        if i % 5 == 0 and i > 0:
            if zones:
                zone = list(zones.values())[0]
                print(f"\n[{time.strftime('%H:%M:%S')}] Estado estable:")
                print(f"  Estado: {zone['last_state']}")
                print(f"  Detecciones totales: {zone['detection_count']}")
                print(f"  Modo Eco: {eco_state}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(1)

print("\n\n📊 RESUMEN FINAL:")
if prev_zones:
    for zone_id, zone_data in prev_zones.items():
        print(f"  Zona {zone_id}: {zone_data['last_state']}")
        print(f"  Confianza final: {zone_data['average_confidence']:.2%}")
