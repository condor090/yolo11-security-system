#!/usr/bin/env python3
"""
Monitor en tiempo real para observar el comportamiento del sistema
"""

import asyncio
import json
import time
from datetime import datetime

async def monitor_door_opening():
    print("🦅 MONITOR DEL CÓNDOR - OBSERVANDO EL SISTEMA")
    print("=" * 50)
    print("📹 Esperando que abra la puerta...")
    print("⏱️  El sistema debería:")
    print("   1. Detectar 'gate_open' inmediatamente")
    print("   2. Crear un timer de 30 segundos")
    print("   3. Activar alarma si pasa el tiempo")
    print("   4. Cancelar todo cuando cierre la puerta")
    print("\n" + "=" * 50 + "\n")
    
    last_state = {}
    start_time = time.time()
    
    while True:
        # Obtener estado actual
        cmd_zones = "curl -s http://localhost:8889/api/zones"
        cmd_timers = "curl -s http://localhost:8889/api/timers"
        
        # Ejecutar comandos
        proc_zones = await asyncio.create_subprocess_shell(
            cmd_zones,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        proc_timers = await asyncio.create_subprocess_shell(
            cmd_timers,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        zones_out, _ = await proc_zones.communicate()
        timers_out, _ = await proc_timers.communicate()
        
        try:
            zones = json.loads(zones_out.decode())
            timers = json.loads(timers_out.decode())
            
            # Verificar cambios en zonas
            for zone_id, zone_data in zones.get('zones', {}).items():
                current_state = f"{zone_data['last_state']}:{zone_data['alert_active']}"
                
                if zone_id not in last_state or last_state[zone_id] != current_state:
                    # Cambio detectado!
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    if zone_data['last_state'] == 'gate_open':
                        print(f"\n🔴 [{timestamp}] ¡PUERTA ABIERTA DETECTADA!")
                        print(f"   Zona: {zone_id}")
                        print(f"   Confianza promedio: {zone_data['average_confidence']:.2%}")
                        print(f"   Alerta activa: {zone_data['alert_active']}")
                        
                    elif zone_data['last_state'] == 'gate_closed':
                        print(f"\n🟢 [{timestamp}] PUERTA CERRADA DETECTADA")
                        print(f"   Zona: {zone_id}")
                        print(f"   Alerta debería cancelarse automáticamente...")
                    
                    last_state[zone_id] = current_state
            
            # Mostrar timers activos
            active_timers = timers.get('timers', [])
            if active_timers:
                for timer in active_timers:
                    if timer['time_elapsed'] < 5 or timer['time_elapsed'] % 5 < 0.5:  # Mostrar cada 5 segundos
                        print(f"\n⏱️  Timer Activo: {timer['door_id']}")
                        print(f"   Tiempo: {timer['time_elapsed']:.1f}s / {timer['delay_seconds']}s")
                        print(f"   Progreso: {'█' * int(timer['progress_percent']/10)}{'░' * (10-int(timer['progress_percent']/10))} {timer['progress_percent']:.0f}%")
                        
                        if timer['alarm_triggered']:
                            print(f"   🚨 ¡ALARMA ACTIVADA!")
                        else:
                            print(f"   ⏳ Quedan {timer['time_remaining']:.1f} segundos")
            
            # Verificar alarma global
            if timers.get('alarm_active', False):
                if 'alarm_shown' not in last_state:
                    print("\n🚨🚨🚨 ¡ALARMA GLOBAL ACTIVADA! 🚨🚨🚨")
                    last_state['alarm_shown'] = True
            else:
                if 'alarm_shown' in last_state:
                    print("\n✅ Alarma desactivada")
                    del last_state['alarm_shown']
            
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Error: {e}")
        
        # Esperar un poco antes de la siguiente verificación
        await asyncio.sleep(0.5)
        
        # Mostrar que está monitoreando
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0 and elapsed > 0:
            print(f"\n⏰ Monitoreando... ({elapsed}s)")

if __name__ == "__main__":
    print("Presione Ctrl+C para detener el monitoreo\n")
    try:
        asyncio.run(monitor_door_opening())
    except KeyboardInterrupt:
        print("\n\n👋 Monitor detenido")
