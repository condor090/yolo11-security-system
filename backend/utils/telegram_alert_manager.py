"""
Gestor de Alertas Persistentes de Telegram
Sistema de escalamiento con envíos repetidos configurables
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
from dataclasses import dataclass, field
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TelegramAlert:
    """Representa una alerta activa de Telegram"""
    zone_id: str
    zone_name: str
    camera_id: str
    start_time: datetime
    last_sent: datetime
    send_count: int = 0
    interval_seconds: int = 5
    max_interval: int = 60
    is_active: bool = True
    image_path: Optional[str] = None
    
    def get_next_interval(self) -> int:
        """Calcular el siguiente intervalo de envío (escalamiento progresivo)"""
        # Empezar con 5s, luego 10s, 20s, 30s, hasta max_interval
        if self.send_count == 0:
            return self.interval_seconds
        elif self.send_count == 1:
            return 10
        elif self.send_count == 2:
            return 20
        elif self.send_count == 3:
            return 30
        else:
            return min(self.max_interval, 60)
    
    def should_send_now(self) -> bool:
        """Verificar si es momento de enviar otro mensaje"""
        if not self.is_active:
            return False
        
        time_since_last = (datetime.now() - self.last_sent).total_seconds()
        next_interval = self.get_next_interval()
        
        return time_since_last >= next_interval


class TelegramAlertManager:
    """Gestor de alertas persistentes de Telegram"""
    
    def __init__(self, telegram_service, config_path: Optional[str] = None):
        self.telegram_service = telegram_service
        self.active_alerts: Dict[str, TelegramAlert] = {}
        self.config = self._load_config(config_path)
        self._monitor_task = None
        
        logger.info("TelegramAlertManager inicializado")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Cargar configuración de alertas de Telegram"""
        default_config = {
            "initial_interval": 5,
            "max_interval": 60,
            "intervals_by_zone": {
                "entrance": 5,
                "loading": 30,
                "emergency": 3
            },
            "include_images": True,
            "escalation_enabled": True
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.error(f"Error cargando configuración: {e}")
        
        return default_config
    
    async def start_monitoring(self):
        """Iniciar el monitoreo de alertas"""
        if self._monitor_task and not self._monitor_task.done():
            return
        
        self._monitor_task = asyncio.create_task(self._monitor_alerts())
        logger.info("Monitor de alertas Telegram iniciado")
    
    async def stop_monitoring(self):
        """Detener el monitoreo de alertas"""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Monitor de alertas Telegram detenido")
    
    async def _monitor_alerts(self):
        """Loop principal de monitoreo de alertas"""
        while True:
            try:
                # Verificar cada alerta activa
                for zone_id, alert in list(self.active_alerts.items()):
                    if alert.should_send_now():
                        await self._send_alert_notification(alert)
                
                await asyncio.sleep(1)  # Verificar cada segundo
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en monitor de alertas: {e}")
                await asyncio.sleep(5)
    
    async def _send_alert_notification(self, alert: TelegramAlert, initial_image=None):
        """Enviar notificación de alerta a Telegram"""
        try:
            # Calcular tiempo transcurrido
            time_elapsed = datetime.now() - alert.start_time
            minutes = int(time_elapsed.total_seconds() / 60)
            seconds = int(time_elapsed.total_seconds() % 60)
            
            # Construir mensaje
            urgency = "🚨" * min(alert.send_count + 1, 5)  # Más emojis = más urgente
            
            message = (
                f"{urgency} <b>ALERTA ACTIVA - Puerta Abierta</b>\n\n"
                f"📍 <b>Zona:</b> {alert.zone_name}\n"
                f"📹 <b>Cámara:</b> {alert.camera_id}\n"
                f"⏱️ <b>Tiempo abierta:</b> {minutes}m {seconds}s\n"
                f"📨 <b>Notificación #</b>{alert.send_count + 1}\n\n"
            )
            
            # Agregar mensaje de urgencia según el tiempo
            if minutes >= 5:
                message += "⚠️ <b>CRÍTICO:</b> Requiere atención INMEDIATA\n"
            elif minutes >= 2:
                message += "⚠️ <b>URGENTE:</b> Verificar zona lo antes posible\n"
            else:
                message += "⚠️ <b>ALERTA:</b> Puerta abierta detectada\n"
            
            # Agregar próximo recordatorio
            next_interval = alert.get_next_interval()
            message += f"\n⏰ Próximo recordatorio en {next_interval}s"
            
            # Enviar mensaje
            success = False
            
            # Enviar con imagen solo en el primer mensaje o cada 5 mensajes
            if (alert.send_count == 0 and initial_image is not None) or \
               (alert.send_count % 5 == 0 and self.config.get("include_images", True)):
                
                # Si es el primer mensaje y tenemos imagen inicial
                if alert.send_count == 0 and initial_image is not None:
                    import numpy as np
                    if isinstance(initial_image, np.ndarray):
                        success = await self.telegram_service.send_photo(initial_image, caption=message)
                    else:
                        success = await self.telegram_service.send_message(message)
                
                # Para mensajes posteriores cada 5 envíos, intentar capturar nueva imagen
                elif alert.send_count % 5 == 0 and alert.send_count > 0:
                    try:
                        # Intentar obtener frame actual de la cámara
                        import backend.main
                        if hasattr(backend.main, 'camera_manager') and backend.main.camera_manager:
                            camera_manager = backend.main.camera_manager
                            if alert.camera_id in camera_manager.cameras:
                                camera = camera_manager.cameras[alert.camera_id]
                                frame = camera.get_frame()
                                if frame is not None:
                                    success = await self.telegram_service.send_photo(frame, caption=message)
                                else:
                                    success = await self.telegram_service.send_message(message)
                            else:
                                success = await self.telegram_service.send_message(message)
                        else:
                            success = await self.telegram_service.send_message(message)
                    except Exception as e:
                        logger.warning(f"No se pudo capturar imagen actual: {e}")
                        success = await self.telegram_service.send_message(message)
                else:
                    success = await self.telegram_service.send_message(message)
            else:
                # Enviar solo texto
                success = await self.telegram_service.send_message(message)
            
            if success:
                alert.send_count += 1
                alert.last_sent = datetime.now()
                logger.info(f"Alerta Telegram enviada para {alert.zone_id} (#{alert.send_count})")
            
        except Exception as e:
            logger.error(f"Error enviando alerta Telegram: {e}")
    
    async def create_alert(self, zone_id: str, zone_name: str, camera_id: str, 
                         image=None):
        """Crear nueva alerta persistente"""
        # Si ya existe una alerta activa para esta zona, no crear otra
        if zone_id in self.active_alerts and self.active_alerts[zone_id].is_active:
            logger.info(f"Alerta ya activa para {zone_id}")
            return
        
        # Obtener intervalo inicial para la zona
        initial_interval = self.config.get("intervals_by_zone", {}).get(
            zone_id.split('_')[0],  # Extraer tipo de zona
            self.config.get("initial_interval", 5)
        )
        
        alert = TelegramAlert(
            zone_id=zone_id,
            zone_name=zone_name,
            camera_id=camera_id,
            start_time=datetime.now(),
            last_sent=datetime.now(),
            interval_seconds=initial_interval,
            max_interval=self.config.get("max_interval", 60),
            image_path=None  # Por ahora no guardamos path, usamos la imagen directamente
        )
        
        self.active_alerts[zone_id] = alert
        
        # Enviar primera notificación inmediatamente con imagen si está disponible
        await self._send_alert_notification(alert, initial_image=image)
        
        logger.info(f"Nueva alerta Telegram creada para {zone_id}")
    
    def cancel_alert(self, zone_id: str):
        """Cancelar alerta activa"""
        if zone_id in self.active_alerts:
            self.active_alerts[zone_id].is_active = False
            del self.active_alerts[zone_id]
            logger.info(f"Alerta Telegram cancelada para {zone_id}")
    
    def cancel_all_alerts(self):
        """Cancelar todas las alertas activas"""
        count = len(self.active_alerts)
        self.active_alerts.clear()
        logger.info(f"Todas las alertas Telegram canceladas ({count} alertas)")
    
    def get_active_alerts(self) -> Dict[str, Dict]:
        """Obtener información de alertas activas para el dashboard"""
        alerts_info = {}
        
        for zone_id, alert in self.active_alerts.items():
            if alert.is_active:
                time_elapsed = (datetime.now() - alert.start_time).total_seconds()
                
                alerts_info[zone_id] = {
                    "zone_name": alert.zone_name,
                    "camera_id": alert.camera_id,
                    "start_time": alert.start_time.isoformat(),
                    "time_elapsed_seconds": time_elapsed,
                    "send_count": alert.send_count,
                    "last_sent": alert.last_sent.isoformat(),
                    "next_interval": alert.get_next_interval(),
                    "status": "active"
                }
        
        return alerts_info
    
    def get_alert_statistics(self) -> Dict:
        """Obtener estadísticas de alertas"""
        total_active = len(self.active_alerts)
        total_messages = sum(alert.send_count for alert in self.active_alerts.values())
        
        longest_alert = None
        if self.active_alerts:
            longest = max(self.active_alerts.values(), 
                         key=lambda a: (datetime.now() - a.start_time).total_seconds())
            longest_alert = {
                "zone_id": longest.zone_id,
                "duration_seconds": (datetime.now() - longest.start_time).total_seconds()
            }
        
        return {
            "total_active_alerts": total_active,
            "total_messages_sent": total_messages,
            "longest_active_alert": longest_alert
        }
