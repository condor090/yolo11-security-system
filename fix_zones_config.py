#!/usr/bin/env python3
"""
Agregar configuración de zonas faltante al sistema
"""

import requests
import json

# Obtener configuración actual
resp = requests.get('http://localhost:8889/api/config')
config = resp.json()['config']

# Agregar configuración de zonas si no existe
if 'zones' not in config:
    config['zones'] = {
        'entrance_door_0': {
            'name': 'Puerta Principal',
            'delay': 15,
            'enabled': True
        },
        'entrance': {
            'name': 'Entrada General',
            'delay': 25,
            'enabled': True
        },
        'door_1': {
            'name': 'Puerta Secundaria',
            'delay': 30,
            'enabled': True
        },
        'loading': {
            'name': 'Zona de Carga',
            'delay': 300,
            'enabled': True
        },
        'emergency': {
            'name': 'Salida de Emergencia',
            'delay': 5,
            'enabled': True
        }
    }
    
    print("Agregando configuración de zonas...")
    
    # Enviar actualización
    update_resp = requests.put('http://localhost:8889/api/config', json=config)
    
    if update_resp.status_code == 200:
        print("✅ Zonas configuradas correctamente")
        
        # Verificar
        verify_resp = requests.get('http://localhost:8889/api/config')
        new_config = verify_resp.json()['config']
        zones = new_config.get('zones', {})
        
        print("\nZonas configuradas:")
        for zone_id, zone_data in zones.items():
            print(f"  - {zone_id}: {zone_data.get('name')} (delay: {zone_data.get('delay')}s)")
    else:
        print(f"❌ Error: {update_resp.text}")
else:
    print("Las zonas ya están configuradas:")
    for zone_id, zone_data in config['zones'].items():
        print(f"  - {zone_id}: {zone_data.get('name')}")

print("\n✅ Ahora el sistema debería enviar alertas a Telegram cuando detecte puertas abiertas")
