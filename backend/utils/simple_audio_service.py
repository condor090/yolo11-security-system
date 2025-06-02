"""
Parche temporal para el sistema de audio
Ejecuta el audio en threads separados para evitar problemas con asyncio
"""

import threading
import time
import pygame
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class SimpleAudioService:
    """Servicio de audio simplificado que funciona con threads"""
    
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds_dir = Path(__file__).parent.parent / "sounds"
        self.active_threads = {}
        self.stop_flags = {}
        
    def start_alarm(self, zone_id: str, zone_name: str, timer_seconds: int = 30):
        """Inicia alarma en un thread separado"""
        # Detener thread anterior si existe
        if zone_id in self.active_threads:
            self.stop_alarm(zone_id)
            
        # Crear flag de parada
        self.stop_flags[zone_id] = threading.Event()
        
        # Crear y arrancar thread
        thread = threading.Thread(
            target=self._alarm_worker,
            args=(zone_id, zone_name, timer_seconds),
            daemon=True
        )
        self.active_threads[zone_id] = thread
        thread.start()
        logger.info(f"🔊 Thread de audio iniciado para {zone_id}")
        
    def _alarm_worker(self, zone_id: str, zone_name: str, timer_seconds: int):
        """Worker que ejecuta el loop de alarma"""
        start_time = datetime.now()
        last_sound_time = 0
        
        while not self.stop_flags[zone_id].is_set():
            elapsed = (datetime.now() - start_time).total_seconds()
            percentage = (elapsed / timer_seconds) * 100
            
            # Determinar fase
            if percentage < 50:
                phase = "friendly"
                interval = 2
                sound_file = "ding_dong.mp3"
            elif percentage < 90:
                phase = "moderate"
                interval = 1
                sound_file = "beep_alert.mp3"
            else:
                phase = "critical"
                interval = 0
                sound_file = "alarm_siren.mp3"
            
            # Log cada cambio de fase
            if not hasattr(self, f"_last_phase_{zone_id}") or getattr(self, f"_last_phase_{zone_id}") != phase:
                logger.info(f"🔊 {zone_id} - Fase: {phase} ({elapsed:.1f}s / {percentage:.1f}%)")
                setattr(self, f"_last_phase_{zone_id}", phase)
            
            # Reproducir sonido
            current_time = time.time()
            if interval == 0 or current_time - last_sound_time >= interval:
                self._play_sound(sound_file)
                last_sound_time = current_time
                
            # Esperar un poco
            time.sleep(0.1 if interval == 0 else 0.5)
            
    def _play_sound(self, sound_file: str):
        """Reproduce un sonido"""
        try:
            sound_path = self.sounds_dir / sound_file
            if sound_path.exists():
                sound = pygame.mixer.Sound(str(sound_path))
                sound.set_volume(0.5)  # Modo nocturno
                sound.play()
            else:
                # Beep del sistema
                import numpy as np
                sample_rate = 22050
                duration = 0.2
                frequency = 880 if "alarm" in sound_file else 440
                frames = int(duration * sample_rate)
                
                arr = np.zeros(frames)
                for i in range(frames):
                    arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
                    
                arr = (arr * 32767).astype(np.int16)
                arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
                
                sound = pygame.sndarray.make_sound(arr)
                sound.set_volume(0.5)
                sound.play()
        except Exception as e:
            logger.error(f"Error reproduciendo sonido: {e}")
            
    def stop_alarm(self, zone_id: str):
        """Detiene la alarma de una zona"""
        if zone_id in self.stop_flags:
            self.stop_flags[zone_id].set()
            logger.info(f"🔊 Deteniendo alarma para {zone_id}")
            
        if zone_id in self.active_threads:
            thread = self.active_threads[zone_id]
            thread.join(timeout=1)
            del self.active_threads[zone_id]
            
        pygame.mixer.stop()
        
    def stop_all_alarms(self):
        """Detiene todas las alarmas"""
        for zone_id in list(self.active_threads.keys()):
            self.stop_alarm(zone_id)

# Instancia global
simple_audio_service = SimpleAudioService()
