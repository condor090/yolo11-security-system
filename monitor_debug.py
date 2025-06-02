#!/usr/bin/env python3
"""
Monitor de Debug para Sistema de Alertas
Muestra en tiempo real el estado de las detecciones y alarmas
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import os

API_URL = "http://localhost:8889"

async def monitor_system():
    """Monitor en tiempo real del sistema"""
    os.system('clear')
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Obtener timers
                async with session.get(f"{API_URL}/api/timers") as resp:
                    timers_data = await resp.json()
                
                # Obtener zonas
                async with session.get(f"{API_URL}/api/zones") as resp:
                    zones_data = await resp.json()
                
                # Obtener eco mode
                async with session.get(f"{API_URL}/api/eco-mode") as resp:
                    eco_data = await resp.json()
                
                # Limpiar pantalla
                os.system('clear')
                
                # Header
                print("="*60)
                print(f"MONITOR DE SISTEMA - {datetime.now().strftime('%H:%M:%S')}")
                print("="*60)
                
                # Estado Eco Mode
                eco = eco_data['eco_mode']
                state = eco['current_state']
                state_colors = {'idle': '🟢', 'alert': '🟡', 'active': '🔴'}
                print(f"\nMODO ECO: {state_colors.get(state, '⚪')} {state.upper()}")
                print(f"CPU estimado: {eco['status']['estimated_cpu']}")
                print(f"YOLO activo: {'✅' if eco['status']['config']['yolo_enabled'] else '❌'}")
                
                # Timers activos
                print(f"\n📢 ALARMAS ACTIVAS: {len(timers_data['timers'])}")
                if timers_data['timers']:
                    for timer in timers_data['timers']:
                        print(f"\n  🚨 {timer['door_id']} (Cámara: {timer['camera_id']})")
                        print(f"     Tiempo abierto: {timer['time_elapsed']:.1f}s")
                        print(f"     Alarma: {'🔔 ACTIVA' if timer['alarm_triggered'] else '⏱️  En espera'}")
                        print(f"     Progreso: {'█' * int(timer['progress_percent']/10)}{'░' * (10-int(timer['progress_percent']/10))} {timer['progress_percent']:.0f}%")
                
                # Zonas detectadas
                print(f"\n🎯 ZONAS MONITOREADAS: {len(zones_data['zones'])}")
                if zones_data['zones']:
                    for zone_id, info in zones_data['zones'].items():
                        icon = '🔓' if info['last_state'] == 'gate_open' else '🔒'
                        print(f"\n  {icon} {zone_id}")
                        print(f"     Estado: {info['last_state']}")
                        print(f"     Alerta activa: {'✅' if info['alert_active'] else '❌'}")
                        print(f"     Detecciones: {info['detection_count']}")
                        print(f"     Última vez: hace {info['last_seen']:.1f}s")
                
                print("\n" + "-"*60)
                print("Presiona Ctrl+C para salir")
                
            except Exception as e:
                print(f"Error: {e}")
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(monitor_system())
    except KeyboardInterrupt:
        print("\n\nMonitor detenido.")
