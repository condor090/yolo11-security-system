#!/usr/bin/env python3
"""
Alert Manager V2 - Sistema de alertas con temporizador inteligente
Incluye delay configurable antes de activar alarmas
"""

import asyncio
import json
import logging
import pygame
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import numpy as np
from PIL import Image
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
    COUNTDOWN = "countdown"  # Nuevo estado: en cuenta regresiva
    TRIGGERED = "triggered"  # Nuevo estado: alarma activada
    SENT = "sent"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"
    CANCELLED = "cancelled"  # Nuevo estado: cancelada (puerta cerrada antes del tiempo)


@dataclass
class Detection:
    """Información de una detección"""
    class_name: str
    confidence: float
    bbox: Dict[str, int]
    timestamp: datetime
    camera_id: str = "default"
    image_path: Optional[str] = None


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


class SoundManager:
    """Gestor de sonidos y alarmas"""
    
    def __init__(self):
        """Inicializar pygame mixer para sonidos"""
        try:
            pygame.mixer.init()
            self.sound_enabled = True
            self.alarm_sound = None
            self.alarm_playing = False
            self._load_sounds()
        except Exception as e:
            logger.error(f"Error inicializando sistema de sonido: {e}")
            self.sound_enabled = False
    
    def _load_sounds(self):
        """Cargar archivos de sonido"""
        # Por ahora usaremos un beep del sistema
        # En producción, cargar archivo .wav o .mp3
        pass
    
    def play_alarm(self):
        """Reproducir alarma de forma continua"""
        if not self.sound_enabled or self.alarm_playing:
            return
        
        self.alarm_playing = True
        # Crear thread para reproducir sonido sin bloquear
        threading.Thread(target=self._alarm_loop, daemon=True).start()
    
    def _alarm_loop(self):
        """Loop de alarma en thread separado"""
        try:
            while self.alarm_playing:
                # Generar beep usando pygame
                frequency = 1000  # Hz
                duration = 500    # milliseconds
                
                # Crear sonido de beep
                sample_rate = 22050
                samples = int(sample_rate * duration / 1000)
                waves = np.sin(2 * np.pi * frequency * np.arange(samples) / sample_rate)
                sound = np.array(waves * 32767, dtype=np.int16)
                sound = np.repeat(sound.reshape(samples, 1), 2, axis=1)
                
                # Reproducir
                sound_array = pygame.sndarray.make_sound(sound)
                sound_array.play()
                
                # Esperar antes de repetir
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error en loop de alarma: {e}")
            self.alarm_playing = False
    
    def stop_alarm(self):
        """Detener alarma"""
        self.alarm_playing = False
        if self.sound_enabled:
            pygame.mixer.stop()


class AlertManager:
    """Gestor principal de alertas con sistema de temporizador"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializar el gestor de alertas
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_path)
        self.channels = {}
        self.alert_history = []
        self.door_timers: Dict[str, DoorTimer] = {}  # Temporizadores activos
        self.sound_manager = SoundManager()
        self._setup_channels()
        
        # Iniciar monitor de temporizadores
        self._start_timer_monitor()
        
        logger.info("AlertManager V2 inicializado con sistema de temporizador")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Cargar configuración desde archivo o usar valores por defecto"""
        default_config = {
            "timer_delays": {
                "default": 30,  # 30 segundos por defecto
                "entrance": 15,  # Entrada principal: 15 segundos
                "loading": 300,  # Zona de carga: 5 minutos
                "emergency": 5   # Salida emergencia: 5 segundos
            },
            "timer_units": "seconds",  # seconds, minutes
            "sound_enabled": True,
            "visual_alerts": True,
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
                "database": {"enabled": True},
                "sound": {"enabled": True}
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
                # Merge configs
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        
        return default_config
    
    def _setup_channels(self):
        """Configurar canales de notificación habilitados"""
        for channel_name, channel_config in self.config['channels'].items():
            if channel_config.get('enabled', False):
                logger.info(f"Canal {channel_name} habilitado")
                # TODO: Inicializar canal real
    
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
                        
                        # Activar alarma sonora
                        if self.config['sound_enabled']:
                            self.sound_manager.play_alarm()
                        
                        # Crear alerta formal
                        asyncio.run(self._create_timer_alert(timer))
                    
                    # Limpiar temporizadores muy antiguos (más de 1 hora sin actualización)
                    if (current_time - timer.last_detected).total_seconds() > 3600:
                        logger.info(f"Limpiando temporizador antiguo: {door_id}")
                        del self.door_timers[door_id]
                
                # Esperar antes de la siguiente verificación
                time.sleep(0.5)  # Verificar cada 500ms
                
            except Exception as e:
                logger.error(f"Error en monitor de temporizadores: {e}")
                time.sleep(1)
    
    def get_timer_delay(self, door_id: str, camera_id: str = "default") -> int:
        """
        Obtener delay configurado para una puerta específica
        
        Args:
            door_id: Identificador de la puerta
            camera_id: Identificador de la cámara
            
        Returns:
            Segundos de delay antes de activar alarma
        """
        delays = self.config['timer_delays']
        
        # Buscar configuración específica por cámara o puerta
        if camera_id in delays:
            delay = delays[camera_id]
        elif door_id in delays:
            delay = delays[door_id]
        else:
            delay = delays.get('default', 30)
        
        # Convertir a segundos si está en minutos
        if self.config.get('timer_units') == 'minutes':
            delay = delay * 60
        
        return delay
    
    async def process_detection(self, detections: List[Dict], camera_id: str = "default", image: Optional[np.ndarray] = None):
        """
        Procesar nuevas detecciones con sistema de temporizador
        
        Args:
            detections: Lista de detecciones del modelo
            camera_id: ID de la cámara que detectó
            image: Imagen con las detecciones
        """
        current_time = datetime.now()
        
        # Identificar puertas abiertas
        open_doors = [d for d in detections if d.get('class_name') == 'gate_open']
        
        # Identificar todas las puertas detectadas (para saber cuáles están cerradas)
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
                logger.info(f"Nueva puerta abierta detectada: {door_id}. Temporizador: {delay} segundos")
                
                # Notificar inicio de cuenta regresiva
                if self.config.get('visual_alerts', True):
                    await self._send_countdown_notification(timer)
        
        # Procesar puertas cerradas (cancelar temporizadores)
        for door_id in closed_door_ids:
            if door_id in self.door_timers:
                timer = self.door_timers[door_id]
                if timer.is_active:
                    logger.info(f"✅ Puerta {door_id} cerrada. Cancelando temporizador.")
                    timer.is_active = False
                    
                    # Detener alarma si estaba sonando
                    if timer.alarm_triggered:
                        self.sound_manager.stop_alarm()
                        logger.info(f"🔕 Alarma detenida para puerta {door_id}")
                    
                    # Eliminar temporizador
                    del self.door_timers[door_id]
    
    async def _send_countdown_notification(self, timer: DoorTimer):
        """Enviar notificación de inicio de cuenta regresiva"""
        message = (
            f"⏱️ Puerta {timer.door_id} detectada abierta\n"
            f"Temporizador iniciado: {timer.delay_seconds} segundos\n"
            f"La alarma se activará a las {(timer.first_detected + timedelta(seconds=timer.delay_seconds)).strftime('%H:%M:%S')}"
        )
        logger.info(message)
        # TODO: Enviar por canales configurados
    
    async def _create_timer_alert(self, timer: DoorTimer):
        """Crear alerta formal cuando se activa el temporizador"""
        detection = Detection(
            class_name='gate_open_timeout',
            confidence=1.0,
            bbox={},
            timestamp=timer.first_detected,
            camera_id=timer.camera_id
        )
        
        alert = Alert(
            id=f"timer_alert_{timer.door_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type='gate_timeout',
            severity=AlertSeverity.HIGH,
            detections=[detection],
            message=f"🚨 ALARMA: Puerta {timer.door_id} abierta por {timer.time_elapsed:.0f} segundos",
            timestamp=datetime.now(),
            status=AlertStatus.TRIGGERED,
            metadata={
                'door_id': timer.door_id,
                'camera_id': timer.camera_id,
                'open_duration': timer.time_elapsed,
                'configured_delay': timer.delay_seconds
            }
        )
        
        self.alert_history.append(alert)
        await self.send_alert(alert)
    
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
        self.sound_manager.stop_alarm()
        for timer in self.door_timers.values():
            timer.alarm_triggered = False
        logger.info("Todas las alarmas detenidas")
    
    def acknowledge_alarm(self, door_id: str):
        """Reconocer una alarma específica"""
        if door_id in self.door_timers:
            timer = self.door_timers[door_id]
            timer.alarm_triggered = False
            self.sound_manager.stop_alarm()
            logger.info(f"Alarma reconocida para puerta {door_id}")
    
    async def send_alert(self, alert: Alert) -> bool:
        """Enviar alerta a través de todos los canales habilitados"""
        success_count = 0
        alert.channel_results = {}
        
        # Implementar envío por canales
        # TODO: Implementar canales reales
        
        return success_count > 0
    
    def save_config(self, config_path: str = "alerts/alert_config.json"):
        """Guardar configuración actual"""
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Configuración guardada en {config_path}")


# Ejemplo de uso
if __name__ == "__main__":
    # Test del sistema con temporizador
    manager = AlertManager()
    
    # Simular detecciones
    test_detections = [
        {
            'class_name': 'gate_open',
            'confidence': 0.85,
            'bbox': {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400},
            'door_id': 'main_entrance'
        }
    ]
    
    # Procesar detección
    print("Simulando puerta abierta...")
    asyncio.run(manager.process_detection(test_detections, camera_id='cam1'))
    
    # Mostrar temporizadores activos
    print("\nTemporizadores activos:")
    for timer in manager.get_active_timers():
        print(f"- Puerta {timer['door_id']}: {timer['time_elapsed']:.1f}s / {timer['delay_seconds']}s")
    
    # Simular espera
    print("\nEsperando 5 segundos...")
    time.sleep(5)
    
    # Mostrar estado actualizado
    print("\nEstado actualizado:")
    for timer in manager.get_active_timers():
        print(f"- Puerta {timer['door_id']}: {timer['time_elapsed']:.1f}s / {timer['delay_seconds']}s")
        print(f"  Tiempo restante: {timer['time_remaining']:.1f}s")
