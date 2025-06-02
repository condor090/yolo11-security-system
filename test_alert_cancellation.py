#!/usr/bin/env python3
"""
Script para probar el comportamiento de cancelación automática de alarmas
"""

import asyncio
import json
import time

async def test_alert_cancellation():
    """Probar que las alarmas se cancelan cuando la puerta se cierra"""
    
    print("🧪 Iniciando prueba de cancelación automática de alarmas...")
    
    # 1. Verificar estado inicial
    print("\n1️⃣ Verificando estado inicial...")
    cmd = "curl -s http://localhost:8889/api/timers | jq '.timers | length'"
    result = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await result.communicate()
    initial_timers = int(stdout.decode().strip())
    print(f"   Timers activos iniciales: {initial_timers}")
    
    # 2. Limpiar todas las alarmas
    if initial_timers > 0:
        print("\n2️⃣ Limpiando alarmas existentes...")
        cmd = "curl -X POST http://localhost:8889/api/alarms/stop-all"
        result = await asyncio.create_subprocess_shell(cmd)
        await result.wait()
        
        # Esperar un poco
        await asyncio.sleep(1)
    
    # 3. Verificar estado de zonas
    print("\n3️⃣ Verificando estado de zonas...")
    cmd = "curl -s http://localhost:8889/api/zones | jq"
    result = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await result.communicate()
    zones = json.loads(stdout.decode())
    
    print("   Estado de zonas:")
    for zone_id, zone_data in zones.get('zones', {}).items():
        print(f"   - {zone_id}: {zone_data['last_state']} (alerta: {zone_data['alert_active']})")
    
    # 4. Monitorear cambios
    print("\n4️⃣ Monitoreando cambios en tiempo real...")
    print("   (El sistema debería crear/cancelar alarmas automáticamente)")
    
    last_state = {}
    for i in range(10):  # Monitorear por 10 segundos
        cmd = "curl -s http://localhost:8889/api/zones"
        result = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await result.communicate()
        zones = json.loads(stdout.decode())
        
        # Verificar cambios
        for zone_id, zone_data in zones.get('zones', {}).items():
            current = f"{zone_data['last_state']}:{zone_data['alert_active']}"
            if zone_id not in last_state or last_state[zone_id] != current:
                emoji = "🔴" if zone_data['last_state'] == 'gate_open' else "🟢"
                alert_emoji = "🚨" if zone_data['alert_active'] else "✅"
                print(f"   {emoji} Zona {zone_id}: {zone_data['last_state']} {alert_emoji}")
                last_state[zone_id] = current
        
        await asyncio.sleep(1)
    
    # 5. Verificar timers finales
    print("\n5️⃣ Verificando timers finales...")
    cmd = "curl -s http://localhost:8889/api/timers | jq"
    result = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await result.communicate()
    timers = json.loads(stdout.decode())
    
    print(f"   Timers activos: {len(timers.get('timers', []))}")
    print(f"   Alarma global: {timers.get('alarm_active', False)}")
    
    print("\n✅ Prueba completada!")
    print("\n💡 Comportamiento esperado:")
    print("   - Cuando detecta 'gate_open': Crea timer/alarma")
    print("   - Cuando detecta 'gate_closed': Cancela timer/alarma automáticamente")
    print("   - No deben quedar alarmas activas si la puerta está cerrada")

if __name__ == "__main__":
    asyncio.run(test_alert_cancellation())
