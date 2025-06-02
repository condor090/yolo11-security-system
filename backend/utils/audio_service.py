"""
Servicio de Audio para Sistema de Alarmas Multi-Fase
Implementa alarmas sonoras progresivas según el tiempo transcurrido
"""

import pygame
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from pathlib import Path
import json
from enum import Enum
import time

logger = logging.getLogger(__name__)

class AlertPhase(Enum):
    """Fases de escalamiento de alarmas"""
    NONE = "none"
    FRIENDLY = "friendly"      # Fase 1: Recordatorio amigable (0-30s)
    MODERATE = "moderate"      # Fase 2: Alerta moderada (30s-2min)
    CRITICAL = "critical"      # Fase 3: Alarma crítica (>2min)

class AudioAlertService:
    """Servicio para manejo de alertas sonoras progresivas"""
    
    def __init__(self):
        """Inicializa el servicio de audio"""
        # Inicializar pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_enabled = True
            logger.info("🔊 Servicio de audio inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando audio: {e}")
            self.audio_enabled = False
            
        # Rutas de sonidos
        self.sounds_dir = Path(__file__).parent.parent / "sounds"
        self.sounds_dir.mkdir(exist_ok=True)
        
        # Cargar configuración
        self.config = self._load_config()
        
        # Estado de alarmas activas por zona
        self.active_alarms: Dict[str, Dict[str, Any]] = {}
        
        # Control de volumen por horario
        self.volume_schedule = {
            "day": {"start": 8, "end": 20, "volume": 0.8},    # 8am-8pm: volumen normal
            "night": {"start": 20, "end": 8, "volume": 0.5}   # 8pm-8am: volumen reducido
        }
        
        # Configuración de fases por defecto (modo porcentaje)
        self.default_phase_config = {
            "phase_1": {
                "percentage": 50,
                "interval_seconds": 10,
                "sound": "ding_dong.mp3",
                "volume": 0.5,
                "name": "friendly"
            },
            "phase_2": {
                "percentage": 90,
                "interval_seconds": 5,
                "sound": "beep_alert.mp3",
                "volume": 0.7,
                "name": "moderate"
            },
            "phase_3": {
                "percentage": 100,
                "interval_seconds": 0,  # 0 = continuo
                "sound": "alarm_siren.mp3",
                "volume": 1.0,
                "name": "critical"
            }
        }
        
        # Tasks de reproducción activas
        self.playback_tasks: Dict[str, asyncio.Task] = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración de audio"""
        config_path = Path(__file__).parent.parent / "configs" / "audio_config.json"
        default_config = {
            "enabled": True,
            "default_phases": {
                "phase_1": {
                    "percentage": 50,
                    "interval_seconds": 10,
                    "sound": "ding_dong.mp3",
                    "volume": 0.5
                },
                "phase_2": {
                    "percentage": 90,
                    "interval_seconds": 5,
                    "sound": "beep_alert.mp3",
                    "volume": 0.7
                },
                "phase_3": {
                    "percentage": 100,
                    "interval_seconds": 0,
                    "sound": "alarm_siren.mp3",
                    "volume": 1.0
                }
            },
            "zone_audio_configs": {
                "default": {
                    "use_custom": False
                },
                "emergency": {
                    "use_custom": True,
                    "phases": [
                        {
                            "name": "urgent",
                            "duration_seconds": 2,
                            "interval_seconds": 1,
                            "sound": "ding_dong.mp3",
                            "volume": 0.8
                        },
                        {
                            "name": "critical",
                            "duration_seconds": 2,
                            "interval_seconds": 0.5,
                            "sound": "beep_alert.mp3",
                            "volume": 1.0
                        },
                        {
                            "name": "extreme",
                            "duration_seconds": -1,
                            "interval_seconds": 0,
                            "sound": "alarm_siren.mp3",
                            "volume": 1.0
                        }
                    ]
                }
            }
        }
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge con valores por defecto
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                    return default_config
        except Exception as e:
            logger.error(f"Error cargando configuración de audio: {e}")
            
        return default_config
    
    def _get_current_volume(self) -> float:
        """Obtiene el volumen según el horario actual"""
        current_hour = datetime.now().hour
        
        # Verificar si estamos en horario nocturno
        night_start = self.volume_schedule["night"]["start"]
        night_end = self.volume_schedule["night"]["end"]
        
        if night_start <= current_hour or current_hour < night_end:
            return self.volume_schedule["night"]["volume"]
        else:
            return self.volume_schedule["day"]["volume"]
    
    def _get_phase_config(self, zone_id: str, elapsed_seconds: float, total_seconds: float) -> Dict[str, Any]:
        """Obtiene la configuración de fase según zona y tiempo"""
        # Buscar configuración de zona
        zone_config = self.config.get("zone_audio_configs", {}).get(zone_id, 
                     self.config.get("zone_audio_configs", {}).get("default", {}))
        
        if zone_config.get("use_custom", False) and "phases" in zone_config:
            # Usar configuración absoluta
            return self._get_absolute_phase(zone_config["phases"], elapsed_seconds)
        else:
            # Usar configuración por porcentajes
            return self._get_percentage_phase(elapsed_seconds, total_seconds)
    
    def _get_absolute_phase(self, phases: List[Dict], elapsed_seconds: float) -> Dict[str, Any]:
        """Obtiene la fase basada en tiempos absolutos"""
        current_time = 0
        
        for i, phase in enumerate(phases):
            duration = phase.get("duration_seconds", -1)
            
            # Si es la última fase o duración infinita
            if duration == -1 or i == len(phases) - 1:
                return {
                    "name": phase.get("name", f"phase_{i+1}"),
                    "interval": phase.get("interval_seconds", 0),
                    "sound": phase.get("sound", "alarm_siren.mp3"),
                    "volume": phase.get("volume", 1.0),
                    "phase_number": i + 1,
                    "total_phases": len(phases)
                }
            
            # Verificar si estamos en esta fase
            if elapsed_seconds <= current_time + duration:
                return {
                    "name": phase.get("name", f"phase_{i+1}"),
                    "interval": phase.get("interval_seconds", 10),
                    "sound": phase.get("sound", "ding_dong.mp3"),
                    "volume": phase.get("volume", 0.5),
                    "phase_number": i + 1,
                    "total_phases": len(phases),
                    "time_in_phase": elapsed_seconds - current_time,
                    "phase_duration": duration
                }
            
            current_time += duration
        
        # Por defecto, última fase
        return self._get_absolute_phase(phases, elapsed_seconds)
    
    def _get_percentage_phase(self, elapsed_seconds: float, total_seconds: float) -> Dict[str, Any]:
        """Obtiene la fase basada en porcentajes del tiempo total"""
        if total_seconds <= 0:
            total_seconds = 30  # Valor por defecto
            
        percentage = (elapsed_seconds / total_seconds) * 100
        default_phases = self.config.get("default_phases", self.default_phase_config)
        
        # LOG PARA DEBUG
        logger.info(f"🔍 Calculando fase: elapsed={elapsed_seconds:.1f}s, total={total_seconds}s, percentage={percentage:.1f}%")
        
        # Determinar fase según porcentaje
        if percentage < default_phases["phase_1"]["percentage"]:
            phase = default_phases["phase_1"]
            phase_name = "friendly"
            phase_number = 1
        elif percentage < default_phases["phase_2"]["percentage"]:
            phase = default_phases["phase_2"]
            phase_name = "moderate"
            phase_number = 2
        else:
            phase = default_phases["phase_3"]
            phase_name = "critical"
            phase_number = 3
        
        logger.info(f"🔍 Fase determinada: {phase_name} (fase {phase_number})")
        
        return {
            "name": phase_name,
            "interval": phase.get("interval_seconds", 10),
            "sound": phase.get("sound", "ding_dong.mp3"),
            "volume": phase.get("volume", 0.5),
            "phase_number": phase_number,
            "total_phases": 3,
            "percentage": percentage
        }
    
    def _get_alert_phase(self, start_time: datetime, zone_id: str) -> AlertPhase:
        """Mantiene compatibilidad - determina la fase de alerta según el tiempo transcurrido"""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Obtener configuración de la zona para compatibilidad
        zone_config = self.config.get("zone_audio_configs", {}).get(zone_id, {})
        
        if zone_config.get("use_custom", False):
            # Para zonas personalizadas, usar lógica simple
            if elapsed < 5:
                return AlertPhase.FRIENDLY
            elif elapsed < 10:
                return AlertPhase.MODERATE
            else:
                return AlertPhase.CRITICAL
        else:
            # Usar lógica original por defecto
            if elapsed < 30:
                return AlertPhase.FRIENDLY
            elif elapsed < 120:
                return AlertPhase.MODERATE
            else:
                return AlertPhase.CRITICAL
    
    async def start_alarm(self, zone_id: str, zone_name: str, timer_seconds: int = 30):
        """Inicia una alarma para una zona específica"""
        if not self.audio_enabled or not self.config.get("enabled", True):
            return
            
        # Si ya hay una alarma activa para esta zona, no iniciar otra
        if zone_id in self.active_alarms:
            logger.info(f"🔊 Alarma ya activa para zona {zone_id}")
            return
            
        logger.info(f"🔊 Iniciando alarma sonora para zona: {zone_name} (Timer: {timer_seconds}s)")
        
        # Registrar alarma activa
        self.active_alarms[zone_id] = {
            "zone_name": zone_name,
            "start_time": datetime.now(),
            "timer_seconds": timer_seconds,
            "current_phase": None,
            "current_phase_config": None
        }
        
        # Cancelar task anterior si existe
        if zone_id in self.playback_tasks:
            logger.warning(f"⚠️ Cancelando task anterior para zona {zone_id}")
            self.playback_tasks[zone_id].cancel()
            
        # Crear nueva task de reproducción
        logger.info(f"🎯 Creando nueva task de audio para zona {zone_id}")
        task = asyncio.create_task(self._alarm_loop(zone_id))
        self.playback_tasks[zone_id] = task
        logger.info(f"✅ Task creada: {task}")
    
    async def _alarm_loop(self, zone_id: str):
        """Loop principal de reproducción de alarma"""
        logger.info(f"🔄 INICIANDO LOOP DE AUDIO para zona {zone_id}")
        try:
            last_sound_time = 0
            loop_count = 0
            
            while zone_id in self.active_alarms:
                loop_count += 1
                alarm_info = self.active_alarms[zone_id]
                elapsed = (datetime.now() - alarm_info["start_time"]).total_seconds()
                timer_seconds = alarm_info.get("timer_seconds", 30)
                
                # Log cada 5 loops
                if loop_count % 5 == 1:
                    logger.info(f"🔄 Loop #{loop_count} - Zona {zone_id}: elapsed={elapsed:.1f}s")
                
                # Obtener configuración de fase actual
                phase_config = self._get_phase_config(zone_id, elapsed, timer_seconds)
                
                # Si cambió la fase, log del cambio
                if phase_config.get("name") != alarm_info.get("current_phase"):
                    alarm_info["current_phase"] = phase_config.get("name")
                    alarm_info["current_phase_config"] = phase_config
                    logger.info(f"🔊 Zona {zone_id} en fase: {phase_config['name']} ({phase_config.get('phase_number', 0)}/{phase_config.get('total_phases', 0)})")
                    
                    # Reproducir anuncio de voz si está habilitado
                    if self.config.get("enable_voice", False):
                        await self._play_voice_announcement(zone_id, alarm_info["zone_name"], phase_config)
                
                # Determinar si es momento de reproducir sonido
                interval = phase_config.get("interval", 10)
                current_time = time.time()
                
                if interval == 0:
                    # Sonido continuo
                    await self._play_configured_sound(phase_config)
                    await asyncio.sleep(0.5)  # Pequeña pausa para no saturar
                elif current_time - last_sound_time >= interval:
                    # Sonido con intervalo
                    await self._play_configured_sound(phase_config)
                    last_sound_time = current_time
                    await asyncio.sleep(0.1)
                else:
                    # Esperar hasta el próximo intervalo
                    wait_time = interval - (current_time - last_sound_time)
                    await asyncio.sleep(min(wait_time, 0.5))
                    
        except asyncio.CancelledError:
            logger.info(f"🔊 Loop de alarma cancelado para zona {zone_id}")
        except Exception as e:
            logger.error(f"❌ Error en loop de alarma: {e}")
    
    async def _play_configured_sound(self, phase_config: Dict[str, Any]):
        """Reproduce el sonido configurado para una fase"""
        try:
            sound_file = phase_config.get("sound", "ding_dong.mp3")
            sound_path = self.sounds_dir / sound_file
            
            # Si el archivo no existe, usar beep del sistema
            if not sound_path.exists():
                logger.warning(f"⚠️ Archivo de sonido no encontrado: {sound_path}")
                self._play_system_beep_from_config(phase_config)
                return
                
            # Cargar y reproducir sonido
            sound = pygame.mixer.Sound(str(sound_path))
            
            # Ajustar volumen según fase y horario
            base_volume = phase_config.get("volume", 0.5)
            schedule_volume = self._get_current_volume()
            final_volume = base_volume * schedule_volume
            
            sound.set_volume(final_volume)
            sound.play()
            
        except Exception as e:
            logger.error(f"❌ Error reproduciendo sonido: {e}")
            self._play_system_beep_from_config(phase_config)
    
    def _play_system_beep_from_config(self, phase_config: Dict[str, Any]):
        """Genera un beep del sistema basado en la configuración de fase"""
        try:
            # Determinar parámetros según la fase
            phase_name = phase_config.get("name", "friendly")
            if phase_name == "critical" or phase_name == "extreme":
                frequency = 880
                duration = 0.3
            elif phase_name == "moderate" or phase_name == "urgent":
                frequency = 660
                duration = 0.2
            else:
                frequency = 440
                duration = 0.1
            
            # Generar tono con pygame
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            import numpy as np
            arr = np.zeros(frames)
            for i in range(frames):
                arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
                
            arr = (arr * 32767).astype(np.int16)
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
            
            sound = pygame.sndarray.make_sound(arr)
            volume = phase_config.get("volume", 0.5) * self._get_current_volume()
            sound.set_volume(volume)
            sound.play()
            
        except Exception as e:
            logger.error(f"❌ Error generando beep: {e}")
    
    async def _play_phase_sound(self, phase: AlertPhase):
        """Mantiene compatibilidad - reproduce el sonido correspondiente a una fase"""
        try:
            # Mapear fase enum a configuración
            phase_map = {
                AlertPhase.FRIENDLY: "phase_1",
                AlertPhase.MODERATE: "phase_2", 
                AlertPhase.CRITICAL: "phase_3"
            }
            
            phase_key = phase_map.get(phase, "phase_1")
            phase_config = self.config.get("default_phases", self.default_phase_config).get(phase_key, {})
            
            sound_file = phase_config.get("sound", "ding_dong.mp3")
            sound_path = self.sounds_dir / sound_file
            
            # Si el archivo no existe, usar beep del sistema
            if not sound_path.exists():
                logger.warning(f"⚠️ Archivo de sonido no encontrado: {sound_path}")
                self._play_system_beep(phase)
                return
                
            # Cargar y reproducir sonido
            sound = pygame.mixer.Sound(str(sound_path))
            
            # Ajustar volumen según fase y horario
            base_volume = phase_config.get("volume", 0.5)
            schedule_volume = self._get_current_volume()
            final_volume = base_volume * schedule_volume
            
            sound.set_volume(final_volume)
            sound.play()
            
        except Exception as e:
            logger.error(f"❌ Error reproduciendo sonido: {e}")
            self._play_system_beep(phase)
    
    def _play_system_beep(self, phase: AlertPhase):
        """Mantiene compatibilidad - genera un beep del sistema como fallback"""
        try:
            # Generar tono con pygame
            sample_rate = 22050
            if phase == AlertPhase.CRITICAL:
                duration = 0.3
                frequency = 880
            elif phase == AlertPhase.MODERATE:
                duration = 0.2
                frequency = 660
            else:
                duration = 0.1
                frequency = 440
            
            frames = int(duration * sample_rate)
            
            import numpy as np
            arr = np.zeros(frames)
            for i in range(frames):
                arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
                
            arr = (arr * 32767).astype(np.int16)
            arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
            
            sound = pygame.sndarray.make_sound(arr)
            
            # Obtener volumen de la configuración
            phase_map = {
                AlertPhase.FRIENDLY: "phase_1",
                AlertPhase.MODERATE: "phase_2",
                AlertPhase.CRITICAL: "phase_3"
            }
            phase_key = phase_map.get(phase, "phase_1")
            phase_config = self.config.get("default_phases", self.default_phase_config).get(phase_key, {})
            
            volume = phase_config.get("volume", 0.5) * self._get_current_volume()
            sound.set_volume(volume)
            sound.play()
            
        except Exception as e:
            logger.error(f"❌ Error generando beep: {e}")
    
    async def _play_voice_announcement(self, zone_id: str, zone_name: str, phase_config: Dict[str, Any]):
        """Reproduce anuncio de voz (placeholder para TTS futuro)"""
        # Por ahora solo log, en el futuro podemos agregar TTS
        phase_name = phase_config.get("name", "unknown")
        phase_number = phase_config.get("phase_number", 0)
        
        messages = {
            "friendly": f"Puerta {zone_name} abierta",
            "moderate": f"Atención: Puerta {zone_name} abierta por más tiempo",
            "critical": f"ALARMA: Puerta {zone_name} requiere atención inmediata",
            "urgent": f"URGENTE: {zone_name} requiere acción",
            "extreme": f"CRÍTICO: {zone_name} en estado de alarma máxima"
        }
        
        message = messages.get(phase_name, f"Alerta fase {phase_number} en {zone_name}")
        logger.info(f"🔊 ANUNCIO: {message}")
        # TODO: Implementar TTS con pyttsx3 o gTTS
    
    async def stop_alarm(self, zone_id: str):
        """Detiene la alarma de una zona específica"""
        if zone_id not in self.active_alarms:
            return
            
        logger.info(f"🔊 Deteniendo alarma para zona {zone_id}")
        
        # Cancelar task de reproducción
        if zone_id in self.playback_tasks:
            self.playback_tasks[zone_id].cancel()
            del self.playback_tasks[zone_id]
            
        # Eliminar de alarmas activas
        del self.active_alarms[zone_id]
        
        # Detener cualquier sonido en reproducción
        pygame.mixer.stop()
    
    async def stop_all_alarms(self):
        """Detiene todas las alarmas activas"""
        logger.info("🔊 Deteniendo todas las alarmas sonoras")
        
        # Copiar lista de zonas para evitar modificar durante iteración
        zones = list(self.active_alarms.keys())
        
        for zone_id in zones:
            await self.stop_alarm(zone_id)
    
    def get_alarm_status(self, zone_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado actual de una alarma"""
        if zone_id not in self.active_alarms:
            return None
            
        alarm_info = self.active_alarms[zone_id]
        elapsed = (datetime.now() - alarm_info["start_time"]).total_seconds()
        timer_seconds = alarm_info.get("timer_seconds", 30)
        phase_config = alarm_info.get("current_phase_config") or self._get_phase_config(zone_id, elapsed, timer_seconds)
        
        return {
            "zone_id": zone_id,
            "zone_name": alarm_info["zone_name"],
            "elapsed_seconds": int(elapsed),
            "timer_seconds": timer_seconds,
            "current_phase": phase_config.get("name", "unknown"),
            "phase_number": phase_config.get("phase_number", 0),
            "total_phases": phase_config.get("total_phases", 0),
            "interval_seconds": phase_config.get("interval", 0),
            "start_time": alarm_info["start_time"].isoformat()
        }
    
    def get_all_active_alarms(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene información de todas las alarmas activas"""
        result = {}
        for zone_id in self.active_alarms:
            result[zone_id] = self.get_alarm_status(zone_id)
        return result
    
    def set_enabled(self, enabled: bool):
        """Habilita o deshabilita el servicio de audio"""
        self.config["enabled"] = enabled
        if not enabled:
            asyncio.create_task(self.stop_all_alarms())
            
    def update_zone_config(self, zone_id: str, config: Dict[str, Any]):
        """Actualiza la configuración de una zona específica"""
        if "zone_audio_configs" not in self.config:
            self.config["zone_audio_configs"] = {}
            
        self.config["zone_audio_configs"][zone_id] = config
        self._save_config()
    
    def update_default_phases(self, phases_config: Dict[str, Any]):
        """Actualiza la configuración de fases por defecto"""
        self.config["default_phases"] = phases_config
        self._save_config()
    
    def _save_config(self):
        """Guarda la configuración actual"""
        config_path = Path(__file__).parent.parent / "configs" / "audio_config.json"
        config_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("✅ Configuración de audio guardada")
        except Exception as e:
            logger.error(f"Error guardando configuración de audio: {e}")

# Instancia global del servicio
audio_service = AudioAlertService()
