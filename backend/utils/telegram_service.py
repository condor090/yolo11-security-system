"""
Servicio para enviar notificaciones a Telegram
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import io
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = "https://api.telegram.org/bot{}"
        self.enabled = False
        
    def configure(self, bot_token: str, chat_id: str, enabled: bool = True):
        """Configurar el servicio de Telegram"""
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = enabled and bot_token and chat_id
        
        if self.enabled:
            logger.info(f"Telegram configurado - Chat ID: {self.chat_id}")
        else:
            logger.info("Telegram deshabilitado")
    
    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Enviar mensaje de texto a Telegram"""
        if not self.enabled:
            return False
            
        url = self.base_url.format(self.bot_token) + "/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Mensaje enviado a Telegram exitosamente")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Error enviando mensaje a Telegram: {error}")
                        return False
        except Exception as e:
            logger.error(f"Excepción enviando mensaje a Telegram: {e}")
            return False
    
    async def send_photo(self, image: np.ndarray, caption: str = None) -> bool:
        """Enviar imagen con detecciones a Telegram"""
        if not self.enabled:
            return False
            
        url = self.base_url.format(self.bot_token) + "/sendPhoto"
        
        try:
            # Convertir imagen numpy a bytes
            _, buffer = cv2.imencode('.jpg', image)
            image_bytes = buffer.tobytes()
            
            # Crear FormData
            data = aiohttp.FormData()
            data.add_field('chat_id', self.chat_id)
            if caption:
                data.add_field('caption', caption, content_type='text/html')
                data.add_field('parse_mode', 'HTML')
            data.add_field('photo', image_bytes, 
                         filename='detection.jpg',
                         content_type='image/jpeg')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        logger.info("Imagen enviada a Telegram exitosamente")
                        return True
                    else:
                        error = await response.text()
                        logger.error(f"Error enviando imagen a Telegram: {error}")
                        return False
        except Exception as e:
            logger.error(f"Excepción enviando imagen a Telegram: {e}")
            return False
    
    async def send_alert(self, zone_id: str, zone_name: str, 
                        detection_type: str = "puerta_abierta",
                        image: Optional[np.ndarray] = None) -> bool:
        """Enviar alerta formateada a Telegram"""
        if not self.enabled:
            return False
        
        # Formatear mensaje
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        alert_messages = {
            "puerta_abierta": f"🚨 <b>ALERTA - Puerta Abierta</b>\n\n"
                            f"📍 <b>Zona:</b> {zone_name}\n"
                            f"🕐 <b>Hora:</b> {timestamp}\n"
                            f"🔴 <b>Estado:</b> ACTIVA\n\n"
                            f"⚠️ Requiere atención inmediata",
            
            "puerta_cerrada": f"✅ <b>Puerta Cerrada</b>\n\n"
                            f"📍 <b>Zona:</b> {zone_name}\n"
                            f"🕐 <b>Hora:</b> {timestamp}\n"
                            f"🟢 <b>Estado:</b> SEGURO",
            
            "alarma_reconocida": f"👁️ <b>Alarma Reconocida</b>\n\n"
                               f"📍 <b>Zona:</b> {zone_name}\n"
                               f"🕐 <b>Hora:</b> {timestamp}\n"
                               f"🟡 <b>Estado:</b> En seguimiento"
        }
        
        message = alert_messages.get(detection_type, 
                                    f"📢 Evento en {zone_name} - {timestamp}")
        
        # Si hay imagen, enviarla con el caption
        if image is not None:
            return await self.send_photo(image, caption=message)
        else:
            return await self.send_message(message)
    
    async def send_test_message(self) -> bool:
        """Enviar mensaje de prueba"""
        test_message = (
            "🤖 <b>YOMJAI - Sistema de Seguridad</b>\n\n"
            "✅ Conexión con Telegram establecida correctamente\n"
            f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            "Las notificaciones de alertas están activas."
        )
        return await self.send_message(test_message)
    
    async def send_daily_summary(self, stats: Dict[str, Any]) -> bool:
        """Enviar resumen diario de actividad"""
        if not self.enabled:
            return False
        
        summary = (
            f"📊 <b>Resumen Diario - YOMJAI</b>\n"
            f"📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"🚪 <b>Detecciones totales:</b> {stats.get('total_detections', 0)}\n"
            f"🚨 <b>Alertas generadas:</b> {stats.get('total_alerts', 0)}\n"
            f"✅ <b>Alertas resueltas:</b> {stats.get('resolved_alerts', 0)}\n"
            f"⏱️ <b>Tiempo promedio de respuesta:</b> {stats.get('avg_response_time', 'N/A')}\n\n"
            f"💾 <b>Estado del sistema:</b> Operativo\n"
            f"🔋 <b>Modo Eco activo:</b> {stats.get('eco_hours', 0)}h"
        )
        
        return await self.send_message(summary)

# Instancia global del servicio
telegram_service = TelegramService()
