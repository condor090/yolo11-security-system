#!/usr/bin/env python3
"""
Script de emergencia para reducir el consumo de CPU
"""

import requests
import time

API_URL = "http://localhost:8889"

print("=== OPTIMIZACIÓN DE EMERGENCIA ===\n")

# 1. Detener todas las alarmas
print("1. Deteniendo alarmas...")
try:
    requests.post(f"{API_URL}/api/alarms/stop-all")
    print("   ✓ Alarmas detenidas")
except:
    pass

# 2. Matar procesos Python de alto consumo
print("\n2. Deteniendo backend...")
import os
os.system("lsof -ti:8889 | xargs kill -9 2>/dev/null")
time.sleep(2)

print("\n✅ Sistema detenido para enfriamiento")
print("\nRECOMENDACIONES:")
print("1. Esperar 2-3 minutos para que el Mac se enfríe")
print("2. Al reiniciar, usar configuración optimizada:")
print("   - Detección cada 2 segundos (no 500ms)")
print("   - Límite de FPS a 15 (no 30)")
print("   - Desactivar detección cuando no hay movimiento")
