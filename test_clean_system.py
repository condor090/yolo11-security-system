#!/usr/bin/env python3
"""
Prueba del comportamiento mejorado: Puerta cerrada = Sistema seguro
"""

import asyncio
import json
import time
from datetime import datetime

async def test_door_behavior():
    print("🧪 PRUEBA: PUERTA CERRADA = SISTEMA SEGURO")
    print("=" * 50)
    print("\nFilosofía implementada:")
    print("✅ Cuando CUALQUIER puerta se cierra, TODAS las alarmas se cancelan")
    print("✅ El sistema considera que si una puerta está cerrada, todo es seguro")
    print("\n" + "=" * 50)
    
    # 1. Estado inicial
    print("\n1️⃣ Verificando estado inicial...")
    cmd = "curl -s http://localhost:8889/api/timers"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
    out, _ = await proc.communicate()
    timers = json.loads(out.decode())
    print(f"   Timers activos: {len(timers['timers'])}")
    print(f"   Alarma global: {timers['alarm_active']}")
    
    # 2. Monitor en tiempo real
    print("\n2️⃣ Monitoreando comportamiento...")
    print("\n   🔴 ABRA LA PUERTA y espere que se active la alarma")
    print("   🟢 Luego CIERRE LA PUERTA para ver la magia\n")
    
    last_state = {}
    door_opened_time = None
    alarm_triggered_time = None
    door_closed_time = None
    
    for i in range(60):  # Monitorear por 60 segundos
        # Obtener estado
        cmd_zones = "curl -s http://localhost:8889/api/zones"
        cmd_timers = "curl -s http://localhost:8889/api/timers"
        
        proc_zones = await asyncio.create_subprocess_shell(cmd_zones, stdout=asyncio.subprocess.PIPE)
        proc_timers = await asyncio.create_subprocess_shell(cmd_timers, stdout=asyncio.subprocess.PIPE)
        
        zones_out, _ = await proc_zones.communicate()
        timers_out, _ = await proc_timers.communicate()
        
        try:
            zones = json.loads(zones_out.decode())
            timers = json.loads(timers_out.decode())
            
            # Verificar cambios
            for zone_id, zone_data in zones.get('zones', {}).items():
                state_key = f"{zone_data['last_state']}:{zone_data['alert_active']}"
                
                if zone_id not in last_state or last_state[zone_id] != state_key:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    if zone_data['last_state'] == 'gate_open' and not door_opened_time:
                        door_opened_time = time.time()
                        print(f"[{timestamp}] 🔴 PUERTA ABIERTA DETECTADA")
                        print(f"            Timer iniciado con 30 segundos...")
                        
                    elif zone_data['last_state'] == 'gate_closed':
                        door_closed_time = time.time()
                        print(f"\n[{timestamp}] 🟢 PUERTA CERRADA DETECTADA")
                        print(f"            🧹 Limpiando TODAS las alarmas...")
                    
                    last_state[zone_id] = state_key
            
            # Mostrar timers activos
            if timers['timers']:
                for timer in timers['timers']:
                    if timer['alarm_triggered'] and not alarm_triggered_time:
                        alarm_triggered_time = time.time()
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚨 ALARMA ACTIVADA")
                        print(f"            Tiempo transcurrido: {timer['time_elapsed']:.1f}s")
            
            # Verificar si se limpiaron los timers
            if door_closed_time and len(timers['timers']) == 0 and 'timers_cleaned' not in last_state:
                elapsed = time.time() - door_closed_time
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ SISTEMA LIMPIO")
                print(f"            Todos los timers eliminados en {elapsed:.2f}s")
                print(f"            Alarma global: {timers['alarm_active']}")
                last_state['timers_cleaned'] = True
                break
                
        except:
            pass
        
        await asyncio.sleep(1)
        
        # Mostrar progreso
        if i % 5 == 0 and i > 0 and not door_closed_time:
            print(f"    ... monitoreando ({i}s)")
    
    # 3. Verificación final
    print("\n3️⃣ Verificación final...")
    await asyncio.sleep(2)
    
    cmd = "curl -s http://localhost:8889/api/timers"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
    out, _ = await proc.communicate()
    final_timers = json.loads(out.decode())
    
    cmd = "curl -s http://localhost:8889/api/zones"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
    out, _ = await proc.communicate()
    final_zones = json.loads(out.decode())
    
    print(f"\n   📊 RESULTADO FINAL:")
    print(f"   - Timers activos: {len(final_timers['timers'])}")
    print(f"   - Alarma global: {final_timers['alarm_active']}")
    print(f"   - Zonas detectadas: {len(final_zones['zones'])}")
    
    if len(final_timers['timers']) == 0 and not final_timers['alarm_active']:
        print("\n   ✅ ÉXITO: El sistema funciona correctamente")
        print("   ✅ Puerta cerrada = Sistema seguro")
    else:
        print("\n   ⚠️  Aún hay timers activos")
        for timer in final_timers['timers']:
            print(f"      - {timer['door_id']}: {timer['time_elapsed']:.1f}s")

if __name__ == "__main__":
    print("\n🦅 Sistema de seguridad con filosofía mejorada")
    print("Presione Ctrl+C para detener\n")
    
    try:
        asyncio.run(test_door_behavior())
    except KeyboardInterrupt:
        print("\n\n👋 Prueba detenida")
