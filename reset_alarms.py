#!/usr/bin/env python3
"""
Script para forzar limpieza de alarmas y resetear el estado
"""

import requests
import json

API_URL = "http://localhost:8889"

def reset_system():
    print("=== RESETEANDO SISTEMA DE ALARMAS ===\n")
    
    # 1. Detener todas las alarmas
    print("1. Deteniendo todas las alarmas...")
    try:
        response = requests.post(f"{API_URL}/api/alarms/stop-all")
        print(f"   Respuesta: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 2. Verificar estado de timers
    print("\n2. Verificando timers...")
    try:
        response = requests.get(f"{API_URL}/api/timers")
        data = response.json()
        print(f"   Timers activos: {len(data['timers'])}")
        print(f"   Alarma activa: {data['alarm_active']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Verificar zonas
    print("\n3. Verificando zonas...")
    try:
        response = requests.get(f"{API_URL}/api/zones")
        data = response.json()
        print(f"   Zonas detectadas: {len(data['zones'])}")
        for zone_id, zone_info in data['zones'].items():
            print(f"   - {zone_id}: estado={zone_info['last_state']}, alerta={zone_info['alert_active']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== SISTEMA RESETEADO ===")
    print("\nNOTA: Si el frontend sigue mostrando alarmas:")
    print("1. Recarga la página (F5)")
    print("2. O haz clic en 'Detener Alarmas' en la UI")

if __name__ == "__main__":
    reset_system()
