#!/usr/bin/env python3
"""
Alert Manager - Sistema central de gestión de alertas
Fase 2: Sistema de Alertas para YOLO11 Security
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import numpy as np
from PIL import Image

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Niveles de severidad de alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Estados de una alerta"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class Detection:
    """Información de una detección"""
    class_name: str
    confidence: float
    bbox: Dict[str, int]
    timestamp: datetime
    image_path: Optional[str] = None


@dataclass
class Alert:
    """Estructura de una alerta"""
    id: str
    type: str
    severity: AlertSeverity
    detections: List[Detection]
    message: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.PENDING
    channel_results: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        """Convertir a diccionario para serialización"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        data['detections'] = [
            {
                **d,
                'timestamp': d['timestamp'].isoformat() if isinstance(d.get('timestamp'), datetime) else d.get('timestamp')
            } for d in data['detections']
        ]
        return data


class AlertManager:
    """Gestor principal de alertas del sistema"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializar el gestor de alertas
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_path)
        self.channels = {}
        self.alert_history = []
        self.cooldown_tracker = {}
        self._setup_channels()
        
        logger.info("AlertManager inicializado")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Cargar configuración desde archivo o usar valores por defecto"""
        default_config = {
            "cooldown_minutes": 5,
            "max_alerts_per_hour": 10,
            "severity_thresholds": {
                "low": 0.5,
                "medium": 0.65,
                "high": 0.75,
                "critical": 0.85
            },
            "channels": {
                "email": {"enabled": False},
                "telegram": {"enabled": False},
                "database": {"enabled": True}
            },
            "working_hours": {
                "enabled": False,
                "start": "08:00",
                "end": "22:00"
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _setup_channels(self):
        """Configurar canales de notificación habilitados"""
        # Por ahora solo configuramos la estructura
        # La implementación real vendrá después
        for channel_name, channel_config in self.config['channels'].items():
            if channel_config.get('enabled', False):
                logger.info(f"Canal {channel_name} habilitado")
                # TODO: Inicializar canal real
    
    def calculate_severity(self, detections: List[Detection]) -> AlertSeverity:
        """
        Calcular severidad basada en las detecciones
        
        Args:
            detections: Lista de detecciones
            
        Returns:
            Nivel de severidad calculado
        """
        if not detections:
            return AlertSeverity.LOW
        
        # Calcular confianza máxima y promedio
        confidences = [d.confidence for d in detections]
        max_confidence = max(confidences)
        avg_confidence = np.mean(confidences)
        
        # Considerar número de detecciones
        detection_count = len(detections)
        
        # Lógica de severidad
        thresholds = self.config['severity_thresholds']
        
        if max_confidence >= thresholds['critical'] or detection_count >= 3:
            return AlertSeverity.CRITICAL
        elif max_confidence >= thresholds['high'] or detection_count >= 2:
            return AlertSeverity.HIGH
        elif max_confidence >= thresholds['medium']:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def should_send_alert(self, detection_type: str) -> bool:
        """
        Verificar si se debe enviar una alerta basado en cooldown y límites
        
        Args:
            detection_type: Tipo de detección (ej: 'gate_open')
            
        Returns:
            True si se debe enviar la alerta
        """
        now = datetime.now()
        
        # Verificar horario de trabajo si está habilitado
        if self.config['working_hours']['enabled']:
            start_time = datetime.strptime(self.config['working_hours']['start'], "%H:%M").time()
            end_time = datetime.strptime(self.config['working_hours']['end'], "%H:%M").time()
            current_time = now.time()
            
            if not (start_time <= current_time <= end_time):
                logger.info("Fuera de horario de trabajo, alerta suprimida")
                return False
        
        # Verificar cooldown
        cooldown_key = f"cooldown_{detection_type}"
        if cooldown_key in self.cooldown_tracker:
            last_alert_time = self.cooldown_tracker[cooldown_key]
            cooldown_minutes = self.config['cooldown_minutes']
            
            if now - last_alert_time < timedelta(minutes=cooldown_minutes):
                remaining = (last_alert_time + timedelta(minutes=cooldown_minutes) - now).seconds // 60
                logger.info(f"En cooldown, faltan {remaining} minutos")
                return False
        
        # Verificar límite por hora
        hour_ago = now - timedelta(hours=1)
        recent_alerts = [a for a in self.alert_history 
                        if a.timestamp > hour_ago and a.type == detection_type]
        
        if len(recent_alerts) >= self.config['max_alerts_per_hour']:
            logger.warning(f"Límite de alertas por hora alcanzado ({len(recent_alerts)})")
            return False
        
        return True
    
    async def create_alert(self, detections: List[Dict], image: Optional[np.ndarray] = None) -> Optional[Alert]:
        """
        Crear una nueva alerta basada en detecciones
        
        Args:
            detections: Lista de detecciones del modelo
            image: Imagen con las detecciones (opcional)
            
        Returns:
            Alerta creada o None si no se debe crear
        """
        if not detections:
            return None
        
        # Convertir detecciones a objetos Detection
        detection_objects = []
        for det in detections:
            detection = Detection(
                class_name=det['class_name'],
                confidence=det['confidence'],
                bbox=det['bbox'],
                timestamp=datetime.now()
            )
            detection_objects.append(detection)
        
        # Filtrar solo puertas abiertas
        open_doors = [d for d in detection_objects if d.class_name == 'gate_open']
        
        if not open_doors:
            return None
        
        # Verificar si debemos enviar alerta
        if not self.should_send_alert('gate_open'):
            return None
        
        # Guardar imagen si se proporciona
        image_path = None
        if image is not None:
            image_path = await self._save_alert_image(image, open_doors)
            for detection in detection_objects:
                detection.image_path = image_path
        
        # Crear alerta
        alert = Alert(
            id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.alert_history)}",
            type='gate_open',
            severity=self.calculate_severity(open_doors),
            detections=detection_objects,
            message=self._generate_alert_message(open_doors),
            timestamp=datetime.now(),
            metadata={
                'total_detections': len(detections),
                'open_doors': len(open_doors),
                'max_confidence': max(d.confidence for d in open_doors)
            }
        )
        
        # Actualizar cooldown
        self.cooldown_tracker['cooldown_gate_open'] = datetime.now()
        
        # Agregar a historial
        self.alert_history.append(alert)
        
        logger.info(f"Alerta creada: {alert.id} - Severidad: {alert.severity.value}")
        
        return alert
    
    def _generate_alert_message(self, detections: List[Detection]) -> str:
        """Generar mensaje descriptivo para la alerta"""
        count = len(detections)
        max_conf = max(d.confidence for d in detections)
        
        if count == 1:
            return f"🚨 Puerta abierta detectada con {max_conf:.1%} de confianza"
        else:
            return f"🚨 {count} puertas abiertas detectadas (máx. confianza: {max_conf:.1%})"
    
    async def _save_alert_image(self, image: np.ndarray, detections: List[Detection]) -> str:
        """Guardar imagen de la alerta con las detecciones marcadas"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"alert_{timestamp}.jpg"
        filepath = Path("captured_events/images") / filename
        
        # Asegurar que el directorio existe
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir y guardar imagen
        if isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
            pil_image.save(filepath, quality=85)
            logger.info(f"Imagen guardada: {filepath}")
        
        return str(filepath)
    
    async def send_alert(self, alert: Alert) -> bool:
        """
        Enviar alerta a través de todos los canales habilitados
        
        Args:
            alert: Alerta a enviar
            
        Returns:
            True si al menos un canal envió exitosamente
        """
        success_count = 0
        alert.channel_results = {}
        
        for channel_name, channel in self.channels.items():
            try:
                # TODO: Implementar envío real por cada canal
                logger.info(f"Enviando alerta por {channel_name}")
                alert.channel_results[channel_name] = {"status": "success"}
                success_count += 1
            except Exception as e:
                logger.error(f"Error enviando por {channel_name}: {e}")
                alert.channel_results[channel_name] = {"status": "error", "error": str(e)}
        
        # Actualizar estado
        alert.status = AlertStatus.SENT if success_count > 0 else AlertStatus.FAILED
        
        return success_count > 0
    
    def get_alert_statistics(self, hours: int = 24) -> Dict:
        """
        Obtener estadísticas de alertas
        
        Args:
            hours: Número de horas hacia atrás para calcular
            
        Returns:
            Diccionario con estadísticas
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [a for a in self.alert_history if a.timestamp > cutoff_time]
        
        if not recent_alerts:
            return {
                'total_alerts': 0,
                'by_severity': {},
                'by_hour': {},
                'average_confidence': 0
            }
        
        # Estadísticas por severidad
        by_severity = {}
        for severity in AlertSeverity:
            count = len([a for a in recent_alerts if a.severity == severity])
            by_severity[severity.value] = count
        
        # Estadísticas por hora
        by_hour = {}
        for alert in recent_alerts:
            hour = alert.timestamp.hour
            by_hour[hour] = by_hour.get(hour, 0) + 1
        
        # Confianza promedio
        all_confidences = []
        for alert in recent_alerts:
            all_confidences.extend([d.confidence for d in alert.detections])
        
        avg_confidence = np.mean(all_confidences) if all_confidences else 0
        
        return {
            'total_alerts': len(recent_alerts),
            'by_severity': by_severity,
            'by_hour': by_hour,
            'average_confidence': float(avg_confidence),
            'last_alert': recent_alerts[-1].timestamp.isoformat() if recent_alerts else None
        }
    
    def save_state(self, filepath: str = "alerts/alert_state.json"):
        """Guardar estado del manager para persistencia"""
        state = {
            'config': self.config,
            'alert_history': [alert.to_dict() for alert in self.alert_history[-100:]],  # Últimas 100
            'cooldown_tracker': {k: v.isoformat() for k, v in self.cooldown_tracker.items()},
            'statistics': self.get_alert_statistics()
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Estado guardado en {filepath}")


# Ejemplo de uso
if __name__ == "__main__":
    # Test básico del AlertManager
    manager = AlertManager()
    
    # Simular detecciones
    test_detections = [
        {
            'class_name': 'gate_open',
            'confidence': 0.78,
            'bbox': {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400}
        }
    ]
    
    # Crear alerta
    loop = asyncio.get_event_loop()
    alert = loop.run_until_complete(manager.create_alert(test_detections))
    
    if alert:
        print(f"Alerta creada: {alert.message}")
        print(f"Severidad: {alert.severity.value}")
        print(f"ID: {alert.id}")
    else:
        print("No se creó alerta (posiblemente en cooldown)")
    
    # Mostrar estadísticas
    stats = manager.get_alert_statistics()
    print(f"\nEstadísticas (últimas 24h): {json.dumps(stats, indent=2)}")
    
    # Guardar estado
    manager.save_state()
