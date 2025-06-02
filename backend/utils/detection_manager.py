"""
Gestor de Detecciones con Deduplicación
Evita múltiples alarmas para la misma puerta/zona
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ZoneState:
    """Estado de una zona específica"""
    zone_id: str
    last_state: str  # 'gate_open' o 'gate_closed'
    last_detection_time: float
    alert_active: bool
    detection_count: int
    confidence_sum: float
    
    @property
    def average_confidence(self) -> float:
        return self.confidence_sum / max(self.detection_count, 1)

class DetectionManager:
    """
    Gestiona las detecciones evitando duplicados y manteniendo estado por zona
    """
    
    def __init__(self, state_timeout: float = 2.0, min_confidence: float = 0.75):
        """
        Args:
            state_timeout: Tiempo sin detecciones para considerar que no hay objeto
            min_confidence: Confianza mínima para procesar detección
        """
        self.zones: Dict[str, ZoneState] = {}
        self.state_timeout = state_timeout
        self.min_confidence = min_confidence
        self.last_cleanup = time.time()
        
    def process_frame_detections(self, detections: List[dict], camera_id: str) -> List[dict]:
        """
        Procesa todas las detecciones de un frame y devuelve solo las que requieren acción
        
        Args:
            detections: Lista de detecciones del frame actual
            camera_id: ID de la cámara
            
        Returns:
            Lista de detecciones que requieren crear/cancelar alertas
        """
        current_time = time.time()
        actions_needed = []
        detected_zones = set()
        
        # Procesar cada detección
        for detection in detections:
            if detection['confidence'] < self.min_confidence:
                continue
                
            zone_id = self._get_zone_id(detection, camera_id)
            detected_zones.add(zone_id)
            
            # Obtener o crear estado de zona
            if zone_id not in self.zones:
                self.zones[zone_id] = ZoneState(
                    zone_id=zone_id,
                    last_state='unknown',
                    last_detection_time=current_time,
                    alert_active=False,
                    detection_count=0,
                    confidence_sum=0
                )
            
            zone = self.zones[zone_id]
            zone.last_detection_time = current_time
            zone.detection_count += 1
            zone.confidence_sum += detection['confidence']
            
            # Verificar cambios de estado
            new_state = detection['class_name']
            
            if new_state == 'gate_open' and not zone.alert_active:
                # Nueva puerta abierta detectada
                zone.alert_active = True
                zone.last_state = new_state
                action = {
                    'action': 'create_alert',
                    'zone_id': zone_id,
                    'detection': detection,
                    'average_confidence': zone.average_confidence
                }
                actions_needed.append(action)
                logger.info(f"Nueva alerta para zona {zone_id}")
                
            elif new_state == 'gate_closed' and zone.alert_active:
                # Puerta cerrada, cancelar alerta
                zone.alert_active = False
                zone.last_state = new_state
                action = {
                    'action': 'cancel_alert',
                    'zone_id': zone_id,
                    'detection': detection
                }
                actions_needed.append(action)
                logger.info(f"Cancelar alerta para zona {zone_id}")
            
            # Actualizar estado sin crear nueva alerta
            zone.last_state = new_state
        
        # Limpiar zonas no detectadas (timeout)
        self._cleanup_old_zones(current_time, detected_zones, actions_needed)
        
        return actions_needed
    
    def _get_zone_id(self, detection: dict, camera_id: str) -> str:
        """
        Genera un ID único para la zona basado en la detección y cámara
        
        Por ahora usa door_id, pero podría usar cuadrantes o áreas definidas
        """
        return detection.get('door_id', f"{camera_id}_default")
    
    def _cleanup_old_zones(self, current_time: float, detected_zones: set, actions_needed: List[dict]):
        """
        Limpia zonas que no han sido detectadas recientemente
        """
        zones_to_remove = []
        
        for zone_id, zone in self.zones.items():
            if zone_id not in detected_zones:
                time_since_last = current_time - zone.last_detection_time
                
                # Si ha pasado el timeout y había alerta activa, cancelarla
                if time_since_last > self.state_timeout and zone.alert_active:
                    zone.alert_active = False
                    action = {
                        'action': 'cancel_alert',
                        'zone_id': zone_id,
                        'detection': {
                            'door_id': zone_id,
                            'class_name': 'timeout',
                            'confidence': 0
                        }
                    }
                    actions_needed.append(action)
                    logger.info(f"Timeout para zona {zone_id}, cancelando alerta")
                
                # Si ha pasado mucho tiempo, eliminar la zona
                if time_since_last > self.state_timeout * 10:
                    zones_to_remove.append(zone_id)
        
        # Eliminar zonas muy antiguas
        for zone_id in zones_to_remove:
            del self.zones[zone_id]
            logger.debug(f"Zona {zone_id} eliminada por inactividad")
    
    def get_zone_states(self) -> Dict[str, dict]:
        """
        Obtiene el estado actual de todas las zonas
        """
        return {
            zone_id: {
                'zone_id': zone_id,
                'last_state': zone.last_state,
                'alert_active': zone.alert_active,
                'detection_count': zone.detection_count,
                'average_confidence': zone.average_confidence,
                'last_seen': time.time() - zone.last_detection_time
            }
            for zone_id, zone in self.zones.items()
        }
    
    def reset_zone(self, zone_id: str):
        """
        Resetea el estado de una zona específica
        """
        if zone_id in self.zones:
            del self.zones[zone_id]
            logger.info(f"Zona {zone_id} reseteada")
    
    def reset_all(self):
        """
        Resetea todos los estados
        """
        self.zones.clear()
        logger.info("Todos los estados de zona reseteados")
