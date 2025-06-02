#!/usr/bin/env python3
"""
Script para simular detecciones de puertas abiertas
Esto activará el sistema de alarmas y las fases de audio
"""

import asyncio
import websockets
import json
import time

async def simulate_door_detection():
    print("🚪 Simulando detección de puerta abierta...")
    
    # Conectar al WebSocket principal
    uri = "ws://localhost:8889/ws"
    
    async with websockets.connect(uri) as websocket:
        print("✅ Conectado al WebSocket")
        
        # Simular detección de puerta abierta
        detection_message = {
            "type": "detection",
            "data": {
                "detections": [
                    {
                        "id": "det_0",
                        "class_name": "gate_open",
                        "confidence": 0.95,
                        "bbox": {"x1": 100, "y1": 100, "x2": 200, "y2": 200},
                        "door_id": "door_test"
                    }
                ],
                "timestamp": time.time()
            }
        }
        
        # Enviar detección cada 2 segundos por 3 minutos
        start_time = time.time()
        phase_times = {
            30: "🟢 Fase 1: Friendly - Ding dong suave",
            120: "🟡 Fase 2: Moderate - Beep intermitente",
            180: "🔴 Fase 3: Critical - Sirena continua"
        }
        
        print("\n⏱️  Iniciando simulación de fases:")
        
        while time.time() - start_time < 180:  # 3 minutos
            elapsed = int(time.time() - start_time)
            
            # Mostrar cambio de fase
            if elapsed in phase_times:
                print(f"\n{phase_times[elapsed]}")
            
            # Enviar detección
            await websocket.send(json.dumps(detection_message))
            
            # Mostrar progreso
            print(f"   {elapsed}s - Detección enviada", end='\r')
            
            await asyncio.sleep(2)
        
        print("\n\n✅ Simulación completada - 3 minutos de detección continua")
        
        # Enviar detección de puerta cerrada para limpiar
        close_message = {
            "type": "detection",
            "data": {
                "detections": [
                    {
                        "id": "det_0",
                        "class_name": "gate_closed",
                        "confidence": 0.95,
                        "bbox": {"x1": 100, "y1": 100, "x2": 200, "y2": 200},
                        "door_id": "door_test"
                    }
                ],
                "timestamp": time.time()
            }
        }
        
        await websocket.send(json.dumps(close_message))
        print("🔒 Puerta cerrada - Sistema seguro")

if __name__ == "__main__":
    print("🔊 PRUEBA DEL SISTEMA DE AUDIO MULTI-FASE")
    print("=" * 50)
    print("Este script simulará una puerta abierta por 3 minutos")
    print("Deberías escuchar:")
    print("  0-30s: Ding dong suave cada 10s")
    print("  30s-2min: Beep intermitente cada 5s")
    print("  >2min: Sirena continua")
    print("=" * 50)
    
    input("\nPresiona ENTER para comenzar...")
    
    asyncio.run(simulate_door_detection())
