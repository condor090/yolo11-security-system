#!/usr/bin/env python3
"""
Sound Alert Manager - Sistema de alarma sonora para puertas abiertas
Incluye alarma continua hasta que se cierre la puerta
"""

import pygame
import threading
import time
import logging
from typing import Dict, Optional, Set
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class SoundAlertManager:
    """Gestor de alarmas sonoras para el sistema de seguridad"""
    
    def __init__(self, sounds_dir: str = "alerts/sounds"):
        """
        Inicializar gestor de alarmas sonoras
        
        Args:
            sounds_dir: Directorio con archivos de sonido
        """
        self.sounds_dir = Path(sounds_dir)
        self.sounds_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Alarmas activas (door_id -> thread)
        self.active_alarms: Dict[str, threading.Thread] = {}
        self.alarm_stop_flags: Dict[str, threading.Event] = {}
        
        # Configuración de sonidos
        self.sound_config = {
            'warning': {
                'file': 'warning_beep.wav',
                'volume': 0.5,
                'pattern': [0.5, 0.5]  # beep 0.5s, silencio 0.5s
            },
            'alert': {
                'file': 'alert_tone.wav',
                'volume': 0.7,
                'pattern': [1.0, 0.5]  # beep 1s, silencio 0.5s
            },
            'critical': {
                'file': 'alarm_siren.wav',
                'volume': 0.9,
                'pattern': [2.0, 1.0]  # alarma 2s, silencio 1s
            },
            'door_close': {
                'file': 'success_tone.wav',
                'volume': 0.6,
                'pattern': None  # Solo una vez
            }
        }
        
        # Generar sonidos de prueba si no existen
        self._generate_default_sounds()
        
        logger.info("SoundAlertManager inicializado")
    
    def _generate_default_sounds(self):
        """Generar sonidos por defecto usando pygame"""
        import numpy as np
        
        sample_rate = 22050
        
        # Generar tono de advertencia (beep corto)
        if not (self.sounds_dir / 'warning_beep.wav').exists():
            duration = 0.2
            frequency = 800
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.sin(2 * np.pi * frequency * t) * 0.3
            sound = np.array(wave * 32767, dtype=np.int16)
            sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)  # Stereo
            
            pygame.sndarray.make_sound(sound).save(str(self.sounds_dir / 'warning_beep.wav'))
            logger.info("Generado warning_beep.wav")
        
        # Generar tono de alerta (tono medio)
        if not (self.sounds_dir / 'alert_tone.wav').exists():
            duration = 0.5
            frequencies = [600, 800]  # Dos tonos
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.zeros_like(t)
            
            for i, freq in enumerate(frequencies):
                start = i * len(t) // len(frequencies)
                end = (i + 1) * len(t) // len(frequencies)
                wave[start:end] = np.sin(2 * np.pi * freq * t[start:end]) * 0.5
            
            sound = np.array(wave * 32767, dtype=np.int16)
            sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)
            
            pygame.sndarray.make_sound(sound).save(str(self.sounds_dir / 'alert_tone.wav'))
            logger.info("Generado alert_tone.wav")
        
        # Generar alarma crítica (sirena)
        if not (self.sounds_dir / 'alarm_siren.wav').exists():
            duration = 2.0
            t = np.linspace(0, duration, int(sample_rate * duration))
            # Sirena: frecuencia que sube y baja
            frequency = 400 + 400 * np.sin(2 * np.pi * 2 * t)  # Modula a 2Hz
            wave = np.sin(2 * np.pi * frequency * t / sample_rate) * 0.7
            
            sound = np.array(wave * 32767, dtype=np.int16)
            sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)
            
            pygame.sndarray.make_sound(sound).save(str(self.sounds_dir / 'alarm_siren.wav'))
            logger.info("Generado alarm_siren.wav")
        
        # Generar tono de éxito (puerta cerrada)
        if not (self.sounds_dir / 'success_tone.wav').exists():
            duration = 0.3
            frequencies = [523, 659, 784]  # Do, Mi, Sol
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.zeros_like(t)
            
            for i, freq in enumerate(frequencies):
                start = i * len(t) // len(frequencies)
                end = (i + 1) * len(t) // len(frequencies)
                wave[start:end] = np.sin(2 * np.pi * freq * t[start:end]) * 0.4
            
            sound = np.array(wave * 32767, dtype=np.int16)
            sound = np.repeat(sound.reshape(-1, 1), 2, axis=1)
            
            pygame.sndarray.make_sound(sound).save(str(self.sounds_dir / 'success_tone.wav'))
            logger.info("Generado success_tone.wav")
    
    def start_alarm(self, door_id: str, severity: str = 'alert', 
                   grace_remaining: int = 0) -> bool:
        """
        Iniciar alarma sonora para una puerta
        
        Args:
            door_id: ID de la puerta
            severity: Nivel de severidad ('warning', 'alert', 'critical')
            grace_remaining: Segundos restantes del periodo de gracia
            
        Returns:
            True si se inició la alarma, False si ya estaba activa
        """
        if door_id in self.active_alarms:
            logger.warning(f"Alarma ya activa para puerta {door_id}")
            return False
        
        # Crear flag de parada para esta alarma
        stop_flag = threading.Event()
        self.alarm_stop_flags[door_id] = stop_flag
        
        # Crear thread para la alarma
        alarm_thread = threading.Thread(
            target=self._alarm_loop,
            args=(door_id, severity, stop_flag),
            daemon=True
        )
        
        self.active_alarms[door_id] = alarm_thread
        alarm_thread.start()
        
        logger.info(f"Alarma iniciada para puerta {door_id} con severidad {severity}")
        
        # Si hay periodo de gracia, mostrar cuenta regresiva
        if grace_remaining > 0:
            threading.Thread(
                target=self._grace_countdown,
                args=(door_id, grace_remaining),
                daemon=True
            ).start()
        
        return True
    
    def _alarm_loop(self, door_id: str, severity: str, stop_flag: threading.Event):
        """Loop de reproducción de alarma"""
        sound_config = self.sound_config.get(severity, self.sound_config['alert'])
        sound_file = self.sounds_dir / sound_config['file']
        
        if not sound_file.exists():
            logger.error(f"Archivo de sonido no encontrado: {sound_file}")
            return
        
        try:
            # Cargar sonido
            sound = pygame.mixer.Sound(str(sound_file))
            sound.set_volume(sound_config['volume'])
            
            pattern = sound_config['pattern']
            if pattern is None:
                # Reproducir una sola vez
                sound.play()
                return
            
            # Loop continuo con patrón
            while not stop_flag.is_set():
                # Reproducir sonido
                sound.play()
                
                # Esperar duración del sonido
                time.sleep(pattern[0])
                
                # Silencio entre repeticiones
                if len(pattern) > 1 and not stop_flag.is_set():
                    time.sleep(pattern[1])
                    
        except Exception as e:
            logger.error(f"Error en loop de alarma: {e}")
        finally:
            # Limpiar
            if door_id in self.active_alarms:
                del self.active_alarms[door_id]
            if door_id in self.alarm_stop_flags:
                del self.alarm_stop_flags[door_id]
    
    def _grace_countdown(self, door_id: str, seconds: int):
        """Mostrar cuenta regresiva durante periodo de gracia"""
        for remaining in range(seconds, 0, -1):
            if door_id not in self.active_alarms:
                break
                
            if remaining % 10 == 0 or remaining <= 5:
                logger.info(f"Puerta {door_id}: {remaining} segundos para alarma")
                
                # Beep de advertencia en los últimos 5 segundos
                if remaining <= 5:
                    self._play_countdown_beep()
            
            time.sleep(1)
    
    def _play_countdown_beep(self):
        """Reproducir beep corto de cuenta regresiva"""
        try:
            # Generar beep corto
            frequency = 1000
            duration = 0.1
            sample_rate = 22050
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.sin(2 * np.pi * frequency * t) * 0.2
            sound_array = np.array(wave * 32767, dtype=np.int16)
            sound_array = np.repeat(sound_array.reshape(-1, 1), 2, axis=1)
            
            sound = pygame.sndarray.make_sound(sound_array)
            sound.play()
        except:
            pass  # No crítico si falla
    
    def stop_alarm(self, door_id: str, play_success: bool = True):
        """
        Detener alarma de una puerta
        
        Args:
            door_id: ID de la puerta
            play_success: Si reproducir sonido de éxito
        """
        if door_id in self.alarm_stop_flags:
            # Señalar parada
            self.alarm_stop_flags[door_id].set()
            
            # Esperar a que termine el thread
            if door_id in self.active_alarms:
                self.active_alarms[door_id].join(timeout=1.0)
            
            logger.info(f"Alarma detenida para puerta {door_id}")
            
            # Reproducir sonido de éxito
            if play_success:
                self._play_success_sound()
    
    def stop_all_alarms(self):
        """Detener todas las alarmas activas"""
        door_ids = list(self.alarm_stop_flags.keys())
        for door_id in door_ids:
            self.stop_alarm(door_id, play_success=False)
        
        logger.info("Todas las alarmas detenidas")
    
    def _play_success_sound(self):
        """Reproducir sonido de éxito (puerta cerrada)"""
        try:
            sound_file = self.sounds_dir / self.sound_config['door_close']['file']
            if sound_file.exists():
                sound = pygame.mixer.Sound(str(sound_file))
                sound.set_volume(self.sound_config['door_close']['volume'])
                sound.play()
        except Exception as e:
            logger.error(f"Error reproduciendo sonido de éxito: {e}")
    
    def get_active_alarms(self) -> Dict[str, Dict]:
        """Obtener información de alarmas activas"""
        return {
            door_id: {
                'active': thread.is_alive(),
                'door_id': door_id
            }
            for door_id, thread in self.active_alarms.items()
        }
    
    def update_severity(self, door_id: str, new_severity: str):
        """Actualizar severidad de una alarma activa"""
        if door_id in self.active_alarms:
            # Detener alarma actual
            self.stop_alarm(door_id, play_success=False)
            
            # Iniciar con nueva severidad
            time.sleep(0.1)  # Pequeña pausa
            self.start_alarm(door_id, new_severity)
    
    def test_sounds(self):
        """Probar todos los sonidos disponibles"""
        logger.info("=== PRUEBA DE SONIDOS ===")
        
        for sound_name, config in self.sound_config.items():
            logger.info(f"Probando: {sound_name}")
            
            sound_file = self.sounds_dir / config['file']
            if sound_file.exists():
                sound = pygame.mixer.Sound(str(sound_file))
                sound.set_volume(config['volume'])
                sound.play()
                
                # Esperar a que termine
                time.sleep(sound.get_length() + 0.5)
            else:
                logger.error(f"Archivo no encontrado: {sound_file}")
        
        logger.info("Prueba completada")


# Ejemplo de uso y prueba
if __name__ == "__main__":
    import numpy as np
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Crear gestor de sonidos
    sound_manager = SoundAlertManager()
    
    print("=== PRUEBA DE SISTEMA DE ALARMA SONORA ===\n")
    
    # Probar todos los sonidos
    print("1. Probando sonidos disponibles...")
    sound_manager.test_sounds()
    
    print("\n2. Simulando puerta abierta con periodo de gracia...")
    # Simular alarma con cuenta regresiva
    sound_manager.start_alarm("door_1", severity="warning", grace_remaining=10)
    
    print("   Esperando 5 segundos...")
    time.sleep(5)
    
    print("\n3. Escalando severidad...")
    sound_manager.update_severity("door_1", "critical")
    
    print("   Alarma crítica activa por 5 segundos...")
    time.sleep(5)
    
    print("\n4. Simulando cierre de puerta...")
    sound_manager.stop_alarm("door_1")
    
    print("\n5. Estado final:")
    print(f"   Alarmas activas: {sound_manager.get_active_alarms()}")
    
    print("\nPrueba completada!")
