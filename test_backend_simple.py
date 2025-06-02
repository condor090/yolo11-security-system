#!/usr/bin/env python3
"""
Script de prueba del backend con funcionalidad mínima
Para verificar que todo esté funcionando
"""

import asyncio
import logging
from pathlib import Path
import sys
import json

# Agregar el directorio al path
sys.path.append(str(Path(__file__).parent))

from backend.camera_manager import CameraManager
from alerts.alert_manager_v2_simple import AlertManager

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_backend():
    """Prueba básica del backend"""
    logger.info("🚀 Iniciando prueba del backend...")
    
    # 1. Probar CameraManager
    logger.info("\n📹 Probando CameraManager...")
    camera_manager = CameraManager()
    logger.info(f"  ✅ Cámaras configuradas: {len(camera_manager.configs)}")
    
    # 2. Probar AlertManager
    logger.info("\n🚨 Probando AlertManager...")
    alert_config = Path(__file__).parent / 'alerts' / 'alert_config_v2.json'
    if alert_config.exists():
        alert_manager = AlertManager(str(alert_config))
        logger.info(f"  ✅ AlertManager inicializado")
        logger.info(f"  📊 Delays configurados: {alert_manager.timer_delays}")
    else:
        logger.warning(f"  ⚠️ No se encontró {alert_config}")
    
    # 3. Simular detección de puerta abierta
    logger.info("\n🚪 Simulando detección de puerta abierta...")
    if 'alert_manager' in locals():
        # Simular detección
        test_detection = {
            'class_name': 'gate_open',
            'confidence': 0.95,
            'bbox': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}
        }
        
        alert_manager.process_detections([test_detection], door_id='door_1')
        logger.info("  ✅ Detección procesada")
        
        # Verificar temporizadores
        timers = alert_manager.get_active_timers()
        logger.info(f"  ⏱️ Temporizadores activos: {len(timers)}")
        
        if timers:
            timer = timers[0]
            logger.info(f"    - Puerta: {timer['door_id']}")
            logger.info(f"    - Tiempo transcurrido: {timer['time_elapsed']:.1f}s")
            logger.info(f"    - Tiempo restante: {timer['time_remaining']:.1f}s")
    
    # 4. Estado del sistema
    logger.info("\n📊 Estado del sistema:")
    logger.info(f"  - Cámaras: {len(camera_manager.configs)}")
    logger.info(f"  - Temporizadores: {len(timers) if 'timers' in locals() else 0}")
    logger.info(f"  - Estado: {'Con alertas' if timers else 'Normal'}")
    
    logger.info("\n✅ Prueba completada exitosamente!")
    
    # Mantener corriendo por 5 segundos para ver temporizadores
    logger.info("\n⏳ Esperando 5 segundos para ver evolución de temporizadores...")
    for i in range(5):
        await asyncio.sleep(1)
        if 'alert_manager' in locals():
            timers = alert_manager.get_active_timers()
            if timers:
                logger.info(f"  {i+1}s - Timer: {timers[0]['time_elapsed']:.1f}s / {timers[0]['timer_delay']}s")

if __name__ == "__main__":
    asyncio.run(test_backend())
