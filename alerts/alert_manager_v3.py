#!/usr/bin/env python3
"""
Alert Manager V3 - Sistema completo con alarma sonora
Integra el tiempo de gracia con alarmas sonoras continuas
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import sys

# Importar las clases necesarias del V2
sys.path.append(str(Path(__file__).parent.parent))
from alerts.alert_manager_v2 import (
    AlertManagerV2, Alert, AlertStatus, AlertSeverity, 
    Detection, MonitoredDoor
)
from alerts.sound_alert_manager import SoundAlertManager

logger = logging.getLogger(__name__)


class AlertManagerV3(AlertManagerV2):
    """
    Versión mejorada del AlertManager con alarma sonora integrada
    """
    
    def __init__(self, config_path: Optional[str] = None, enable_sound: bool = True):
        """
        Inicializar Alert Manager V3
        
        Args:
            config_path: Ruta al archivo de configuración
            enable_sound: Habilitar sistema de sonido
        """
        super().__init__(config_path)
        
        # Inicializar gestor de sonido
        self.enable_sound = enable_sound
        self.sound_manager = SoundAlertManager() if enable_sound else None
        
        # Mapeo de severidad a tipo de sonido
        self.severity_to_sound = {
            AlertSeverity.LOW: 'warning',
            AlertSeverity.MEDIUM: 'alert',
            AlertSeverity.HIGH: 'alert',
            AlertSeverity.CRITICAL: 'critical'
        }
        
        # Configuración extendida para sonido
        self.config['sound'] = self.config.get('sound', {
            'enabled': True,
            'grace_period_warning': True,  # Avisos durante periodo de gracia
            'continuous_alarm': True,       # Alarma continua hasta cierre
            'volume_levels': {
                'day': 0.7,    # 7am - 10pm
                'night': 0.5    # 10pm - 7am
            }
        })
        
        logger.info(f"AlertManager V3 inicializado (sonido: {enable_sound})")
    
    async def process_detection(self, detections: List[Dict], 
                              image: Optional[Any] = None,
                              location: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesar detecciones con sistema de alarma sonora
        """
        result = await super().process_detection(detections, image, location)
        
        # Procesar alarmas sonoras basado en el resultado
        if self.enable_sound and self.sound_manager:
            await self._process_sound_alerts(result, detections, location)
        
        return result
    
    async def _process_sound_alerts(self, process_result: Dict, 
                                   detections: List[Dict],
                                   location: Optional[str]):
        """Gestionar alarmas sonoras basado en detecciones"""
        
        # Si se crearon nuevos monitoreos (puertas recién abiertas)
        if process_result.get('new_monitors', 0) > 0:
            # Buscar las puertas recién agregadas
            for door_id, door in self.monitored_doors.items():
                # Si es una puerta nueva (solo tiene 1 detección)
                if len(door.detections) == 1:
                    # Iniciar alarma de advertencia con cuenta regresiva
                    if self.config['sound']['grace_period_warning']:
                        self.sound_manager.start_alarm(
                            door_id, 
                            severity='warning',
                            grace_remaining=door.grace_period_seconds
                        )
                        logger.info(f"Alarma de advertencia iniciada para puerta {door_id}")
        
        # Si se crearon alertas (periodo de gracia expirado)
        if process_result.get('alerts_created', 0) > 0:
            # Buscar las alertas recién creadas
            recent_alerts = self.alert_history[-process_result['alerts_created']:]
            
            for alert in recent_alerts:
                if alert.type == 'gate_open_timeout':
                    # Escalar a alarma continua
                    door_id = alert.monitored_door_id
                    severity_sound = self.severity_to_sound[alert.severity]
                    
                    if door_id in self.sound_manager.active_alarms:
                        # Actualizar severidad
                        self.sound_manager.update_severity(door_id, severity_sound)
                    else:
                        # Iniciar nueva alarma
                        self.sound_manager.start_alarm(door_id, severity_sound)
                    
                    logger.warning(f"ALARMA CRÍTICA: Puerta {door_id} abierta "
                                 f"por más de {alert.metadata.get('grace_period_seconds')}s")
        
        # Si se cerraron puertas
        if process_result.get('doors_closed', 0) > 0:
            # Detener alarmas de puertas cerradas
            active_alarms = list(self.sound_manager.active_alarms.keys())
            
            for door_id in active_alarms:
                # Si la puerta ya no está en monitoreo, se cerró
                if door_id not in self.monitored_doors:
                    self.sound_manager.stop_alarm(door_id, play_success=True)
                    logger.info(f"Puerta {door_id} cerrada - Alarma detenida")
    
    async def _create_alert_from_monitored(self, monitored: MonitoredDoor, 
                                         image: Optional[Any]) -> Optional[Alert]:
        """Override para incluir gestión de sonido al crear alertas"""
        alert = await super()._create_alert_from_monitored(monitored, image)
        
        if alert and self.enable_sound and self.sound_manager:
            # La alarma ya debería estar sonando desde el periodo de gracia
            # Aquí solo actualizamos la severidad si es necesario
            severity_sound = self.severity_to_sound[alert.severity]
            
            if monitored.id in self.sound_manager.active_alarms:
                self.sound_manager.update_severity(monitored.id, severity_sound)
                logger.info(f"Severidad de alarma actualizada a {severity_sound}")
        
        return alert
    
    def set_volume_by_time(self):
        """Ajustar volumen según la hora del día"""
        if not self.enable_sound or not self.sound_manager:
            return
        
        current_hour = datetime.now().hour
        is_night = current_hour >= 22 or current_hour < 7
        
        volume_multiplier = (self.config['sound']['volume_levels']['night'] 
                           if is_night 
                           else self.config['sound']['volume_levels']['day'])
        
        # Aplicar multiplicador a todos los sonidos
        for sound_config in self.sound_manager.sound_config.values():
            sound_config['volume'] *= volume_multiplier
    
    def mute_all_alarms(self):
        """Silenciar todas las alarmas temporalmente"""
        if self.enable_sound and self.sound_manager:
            self.sound_manager.stop_all_alarms()
            logger.info("Todas las alarmas silenciadas")
    
    def test_alarm_system(self):
        """Probar el sistema de alarmas"""
        if self.enable_sound and self.sound_manager:
            logger.info("=== PRUEBA DEL SISTEMA DE ALARMAS ===")
            self.sound_manager.test_sounds()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema incluyendo alarmas sonoras"""
        status = {
            'monitoring': self.get_monitoring_status(),
            'sound_alarms': {},
            'statistics': self.get_alert_statistics(24)
        }
        
        if self.enable_sound and self.sound_manager:
            status['sound_alarms'] = self.sound_manager.get_active_alarms()
            status['sound_enabled'] = True
        else:
            status['sound_enabled'] = False
        
        return status
    
    def update_grace_period(self, location: str, seconds: int):
        """Actualizar periodo de gracia para una ubicación"""
        if location not in self.config['grace_period']['locations']:
            self.config['grace_period']['locations'][location] = seconds
        else:
            self.config['grace_period']['locations'][location] = seconds
        
        # Guardar configuración actualizada
        self._save_config()
        logger.info(f"Periodo de gracia para {location} actualizado a {seconds}s")
    
    def _save_config(self):
        """Guardar configuración actualizada"""
        config_path = Path("alerts/alert_config_v3.json")
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)


# Función helper para integración con el dashboard
async def process_frame_with_alerts(frame, model, alert_manager: AlertManagerV3, 
                                   camera_location: str = "main_entrance"):
    """
    Procesar un frame con el modelo y gestionar alertas
    
    Args:
        frame: Frame de video/imagen
        model: Modelo YOLO cargado
        alert_manager: Instancia de AlertManagerV3
        camera_location: Ubicación de la cámara
        
    Returns:
        Tuple (detections, alert_status)
    """
    # Ejecutar detección
    results = model(frame)
    
    # Convertir a formato esperado
    detections = []
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                detection = {
                    'class_name': model.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': {
                        'x1': int(box.xyxy[0][0]),
                        'y1': int(box.xyxy[0][1]),
                        'x2': int(box.xyxy[0][2]),
                        'y2': int(box.xyxy[0][3])
                    }
                }
                detections.append(detection)
    
    # Procesar con el sistema de alertas
    alert_result = await alert_manager.process_detection(
        detections, 
        image=frame,
        location=camera_location
    )
    
    return detections, alert_result


# Ejemplo de uso y prueba
if __name__ == "__main__":
    import asyncio
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def test_v3_system():
        print("=== PRUEBA DE ALERT MANAGER V3 CON ALARMA SONORA ===\n")
        
        # Crear manager V3
        manager = AlertManagerV3(enable_sound=True)
        
        # Probar sonidos
        print("1. Probando sistema de sonido...")
        manager.test_alarm_system()
        await asyncio.sleep(2)
        
        # Simular detección de puerta abierta
        print("\n2. Simulando puerta abierta (periodo de gracia 15s)...")
        manager.update_grace_period("test_door", 15)  # 15 segundos para prueba
        
        detection = [{
            'class_name': 'gate_open',
            'confidence': 0.85,
            'bbox': {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400}
        }]
        
        result = await manager.process_detection(detection, location="test_door")
        print(f"   Resultado: {result}")
        print(f"   Estado: {manager.get_system_status()}")
        
        # Esperar 10 segundos
        print("\n3. Esperando 10 segundos (aún en periodo de gracia)...")
        await asyncio.sleep(10)
        
        # Verificar estado
        print(f"   Estado: {manager.get_monitoring_status()}")
        
        # Esperar que expire el periodo de gracia
        print("\n4. Esperando que expire el periodo de gracia...")
        await asyncio.sleep(6)
        
        # Procesar de nuevo para activar alarma crítica
        result = await manager.process_detection(detection, location="test_door")
        print(f"   Resultado: {result}")
        
        # Dejar sonar la alarma
        print("\n5. Alarma crítica sonando por 5 segundos...")
        await asyncio.sleep(5)
        
        # Simular cierre de puerta
        print("\n6. Simulando cierre de puerta...")
        result = await manager.process_detection([], location="test_door")
        print(f"   Resultado: {result}")
        
        # Verificar estado final
        print("\n7. Estado final del sistema:")
        print(f"   {manager.get_system_status()}")
        
        print("\n¡Prueba completada!")
    
    # Ejecutar prueba
    asyncio.run(test_v3_system())
