#!/usr/bin/env python3
"""
Monitor de diagnóstico para ver por qué se eliminan las alarmas
"""

import asyncio
import json
import time

async def diagnose_system():
    print("🔍 DIAGNÓSTICO: ¿Por qué se eliminan las alarmas?")
    print("=" * 60)
    
    # Monitor continuo
    prev_detections = []
    prev_timers = []
    
    for i in range(30):
        # Obtener datos
        cmd_zones = "curl -s http://localhost:8889/api/zones"
        cmd_timers = "curl -s http://localhost:8889/api/timers"
        
        proc_zones = await asyncio.create_subprocess_shell(cmd_zones, stdout=asyncio.subprocess.PIPE)
        proc_timers = await asyncio.create_subprocess_shell(cmd_timers, stdout=asyncio.subprocess.PIPE)
        
        zones_out, _ = await proc_zones.communicate()
        timers_out, _ = await proc_timers.communicate()
        
        try:
            zones = json.loads(zones_out.decode())
            timers = json.loads(timers_out.decode())
            
            # Analizar zonas
            current_detections = []
            for zone_id, zone_data in zones.get('zones', {}).items():
                detection_info = f"{zone_id}:{zone_data['last_state']}:{zone_data['alert_active']}"
                current_detections.append(detection_info)
                
                # Verificar cambios
                if detection_info not in prev_detections:
                    print(f"\n[{time.strftime('%H:%M:%S')}] CAMBIO EN ZONA:")
                    print(f"  ID: {zone_id}")
                    print(f"  Estado: {zone_data['last_state']}")
                    print(f"  Alerta activa: {zone_data['alert_active']}")
                    print(f"  Detecciones: {zone_data['detection_count']}")
                    print(f"  Confianza: {zone_data['average_confidence']:.2%}")
            
            # Analizar timers
            current_timer_ids = [t['door_id'] for t in timers.get('timers', [])]
            
            # Timers nuevos
            for timer in timers.get('timers', []):
                if timer['door_id'] not in prev_timers:
                    print(f"\n[{time.strftime('%H:%M:%S')}] ✅ NUEVO TIMER CREADO:")
                    print(f"  ID: {timer['door_id']}")
                    print(f"  Delay: {timer['delay_seconds']}s")
            
            # Timers eliminados
            for timer_id in prev_timers:
                if timer_id not in current_timer_ids:
                    print(f"\n[{time.strftime('%H:%M:%S')}] ❌ TIMER ELIMINADO: {timer_id}")
                    print(f"  ¿Por qué se eliminó?")
                    
                    # Buscar la razón
                    has_closed_door = any('gate_closed' in d for d in current_detections)
                    if has_closed_door:
                        print(f"  → Se detectó puerta CERRADA")
                    elif not any(timer_id in d for d in current_detections):
                        print(f"  → Zona ya no está en detecciones")
                    else:
                        print(f"  → RAZÓN DESCONOCIDA")
            
            # Mostrar estado actual
            if i % 5 == 0:
                print(f"\n[{time.strftime('%H:%M:%S')}] Estado actual:")
                print(f"  Timers activos: {len(timers.get('timers', []))}")
                for timer in timers.get('timers', []):
                    print(f"    - {timer['door_id']}: {timer['time_elapsed']:.1f}s/{timer['delay_seconds']}s")
            
            prev_detections = current_detections
            prev_timers = current_timer_ids
            
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(diagnose_system())
    except KeyboardInterrupt:
        print("\n\nDiagnóstico detenido")
