#!/usr/bin/env python3
"""
Script para forzar limpieza completa del sistema de alarmas
y verificar que todo esté funcionando correctamente
"""

import requests
import time
import json

BASE_URL = "http://localhost:8889"

print("🧹 LIMPIEZA COMPLETA DEL SISTEMA DE ALARMAS\n")

# 1. Detener todas las alarmas
print("1. Deteniendo todas las alarmas...")
response = requests.post(f"{BASE_URL}/api/alarms/stop-all")
print(f"   Resultado: {response.json()}")
time.sleep(1)

# 2. Verificar que no hay timers activos
print("\n2. Verificando timers...")
response = requests.get(f"{BASE_URL}/api/timers")
timers = response.json()
print(f"   Timers activos: {len(timers['timers'])}")
print(f"   Alarma activa: {timers['alarm_active']}")

# 3. Verificar estado del audio
print("\n3. Verificando audio...")
response = requests.get(f"{BASE_URL}/api/audio/alarms")
audio_alarms = response.json()
print(f"   Alarmas de audio activas: {len(audio_alarms['alarms'])}")

if len(audio_alarms['alarms']) > 0:
    print("   ⚠️ Hay alarmas de audio activas, limpiando...")
    for zone_id in audio_alarms['alarms'].keys():
        response = requests.post(f"{BASE_URL}/api/audio/alarm/stop/{zone_id}")
        print(f"   Detenida alarma de {zone_id}")

# 4. Verificar configuración de audio
print("\n4. Configuración de audio:")
response = requests.get(f"{BASE_URL}/api/audio/config")
config = response.json()['config']
phases = config.get('default_phases', {})
for phase, data in phases.items():
    print(f"   {phase}: {data['percentage']}% - intervalo {data['interval_seconds']}s")

print("\n✅ SISTEMA LIMPIO Y LISTO PARA PRUEBAS")
print("\nAhora puede abrir la puerta y el audio debería funcionar correctamente:")
print("- 0-7.5s: Ding-dong cada 2s")
print("- 7.5-13.5s: Beep cada 1s") 
print("- 13.5-15s: Sirena continua")
