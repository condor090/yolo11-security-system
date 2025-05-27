#!/usr/bin/env python3
"""
Alert Manager V2 Simplificado - Sistema de alertas con temporizador
Versión estable sin dependencias problemáticas
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import threading
import time

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
    COUNTDOWN = "countdown"
    TRIGGERED = "triggered"
    SENT = "sent"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"
    CANCELLED = "cancelled"


@dataclass
class DoorTimer:
    """Temporizador para una puerta específica"""
    door_id: str
    first_detected: datetime
    last_detected: datetime
    delay_seconds: int
    is_active: bool = True
    alarm_triggered: bool = False
    camera_id: str = "default"
    
    @property
    def time_elapsed(self) -> float:
        """Tiempo transcurrido desde la primera detección"""
        return (datetime.now() - self.first_detected).total_seconds()
    
    @property
    def time_remaining(self) -> float:
        """Tiempo restante antes de activar alarma"""
        remaining = self.delay_seconds - self.time_elapsed
        return max(0, remaining)
    
    @property
    def should_trigger_alarm(self) -> bool:
        """Verificar si debe activar la alarma"""
        return self.is_active and self.time_elapsed >= self.delay_seconds and not self.alarm_triggered


class AlertManager:
    """Gestor principal de alertas con sistema de temporizador"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Inicializar el gestor de alertas"""
        self.config = self._load_config(config_path)
        self.door_timers: Dict[str, DoorTimer] = {}
        self.alert_history = []
        self.alarm_active = False
        
        # Iniciar monitor de temporizadores
        self._start_timer_monitor()
        
        logger.info("AlertManager V2 inicializado")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Cargar configuración desde archivo o usar valores por defecto"""
        default_config = {
            "timer_delays": {
                "default": 30,
                "entrance": 15,
                "loading": 300,
                "emergency": 5,
                "cam1": 30,
                "cam2": 60,
                "cam3": 120
            },
            "timer_units": "seconds",
            "sound_enabled": True,
            "visual_alerts": True
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge configs
                    for key, value in user_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                logger.error(f"Error cargando configuración: {e}")
        
        return default_config
    
    def _start_timer_monitor(self):
        """Iniciar thread monitor de temporizadores"""
        monitor_thread = threading.Thread(target=self._monitor_timers, daemon=True)
        monitor_thread.start()
        logger.info("Monitor de temporizadores iniciado")
    
    def _monitor_timers(self):
        """Thread que monitorea los temporizadores activos"""
        while True:
            try:
                current_time = datetime.now()
                
                # Verificar cada temporizador
                for door_id, timer in list(self.door_timers.items()):
                    if not timer.is_active:
                        continue
                    
                    # Verificar si debe activar alarma
                    if timer.should_trigger_alarm:
                        logger.warning(f"⏰ ALARMA ACTIVADA - Puerta {door_id} abierta por {timer.time_elapsed:.0f} segundos")
                        timer.alarm_triggered = True
                        self.alarm_active = True
                    
                    # Limpiar temporizadores muy antiguos
                    if (current_time - timer.last_detected).total_seconds() > 3600:
                        logger.info(f"Limpiando temporizador antiguo: {door_id}")
                        del self.door_timers[door_id]
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error en monitor: {e}")
                time.sleep(1)
    
    def get_timer_delay(self, door_id: str, camera_id: str = "default") -> int:
        """Obtener delay configurado para una puerta específica"""
        delays = self.config['timer_delays']
        
        if camera_id in delays:
            delay = delays[camera_id]
        elif door_id in delays:
            delay = delays[door_id]
        else:
            delay = delays.get('default', 30)
        
        if self.config.get('timer_units') == 'minutes':
            delay = delay * 60
        
        return delay
    
    async def process_detection(self, detections: List[Dict], camera_id: str = "default", image: Optional[Any] = None):
        """Procesar nuevas detecciones con sistema de temporizador"""
        current_time = datetime.now()
        
        # Identificar puertas abiertas
        open_doors = [d for d in detections if d.get('class_name') == 'gate_open']
        
        # Identificar todas las puertas detectadas
        all_doors = {d.get('door_id', f"door_{i}") for i, d in enumerate(detections)}
        open_door_ids = {d.get('door_id', f"door_{i}") for i, d in enumerate(open_doors)}
        closed_door_ids = all_doors - open_door_ids
        
        # Procesar puertas abiertas
        for door_detection in open_doors:
            door_id = door_detection.get('door_id', f"{camera_id}_door_0")
            
            if door_id in self.door_timers:
                # Actualizar temporizador existente
                timer = self.door_timers[door_id]
                timer.last_detected = current_time
                logger.info(f"Puerta {door_id} sigue abierta. Tiempo: {timer.time_elapsed:.1f}s / {timer.delay_seconds}s")
            else:
                # Crear nuevo temporizador
                delay = self.get_timer_delay(door_id, camera_id)
                timer = DoorTimer(
                    door_id=door_id,
                    first_detected=current_time,
                    last_detected=current_time,
                    delay_seconds=delay,
                    camera_id=camera_id
                )
                self.door_timers[door_id] = timer
                logger.info(f"Nueva puerta abierta: {door_id}. Temporizador: {delay} segundos")
        
        # Procesar puertas cerradas
        for door_id in closed_door_ids:
            if door_id in self.door_timers:
                timer = self.door_timers[door_id]
                if timer.is_active:
                    logger.info(f"✅ Puerta {door_id} cerrada")
                    timer.is_active = False
                    
                    if timer.alarm_triggered:
                        self.alarm_active = False
                        logger.info(f"🔕 Alarma detenida para puerta {door_id}")
                    
                    del self.door_timers[door_id]
    
    def get_active_timers(self) -> List[Dict]:
        """Obtener información de todos los temporizadores activos"""
        active_timers = []
        for door_id, timer in self.door_timers.items():
            if timer.is_active:
                active_timers.append({
                    'door_id': door_id,
                    'camera_id': timer.camera_id,
                    'time_elapsed': timer.time_elapsed,
                    'time_remaining': timer.time_remaining,
                    'delay_seconds': timer.delay_seconds,
                    'alarm_triggered': timer.alarm_triggered,
                    'first_detected': timer.first_detected.isoformat(),
                    'progress_percent': min(100, (timer.time_elapsed / timer.delay_seconds) * 100)
                })
        return active_timers
    
    def stop_all_alarms(self):
        """Detener todas las alarmas activas"""
        self.alarm_active = False
        for timer in self.door_timers.values():
            timer.alarm_triggered = False
        logger.info("Todas las alarmas detenidas")
    
    def acknowledge_alarm(self, door_id: str):
        """Reconocer una alarma específica"""
        if door_id in self.door_timers:
            timer = self.door_timers[door_id]
            timer.alarm_triggered = False
            # Si no hay más alarmas activas, desactivar alarma global
            if not any(t.alarm_triggered for t in self.door_timers.values()):
                self.alarm_active = False
            logger.info(f"Alarma reconocida para puerta {door_id}")
    
    def get_alert_statistics(self, hours: int = 24) -> Dict:
        """Obtener estadísticas básicas"""
        return {
            'total_alerts': len(self.alert_history),
            'active_timers': len(self.get_active_timers()),
            'alarm_active': self.alarm_active,
            'average_confidence': 0.85  # Placeholder
        }
    
    def save_config(self, config_path: str = "alerts/alert_config_v2.json"):
        """Guardar configuración actual"""
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Configuración guardada en {config_path}")
