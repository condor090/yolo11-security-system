"""
Generador de sonidos de prueba para el sistema de alarmas
Crea archivos de audio básicos para las diferentes fases
"""

import numpy as np
from scipy.io import wavfile
import os
from pathlib import Path

def generate_sine_wave(frequency, duration, sample_rate=44100):
    """Genera una onda sinusoidal"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = np.sin(2 * np.pi * frequency * t)
    return wave

def generate_ding_dong(sample_rate=44100):
    """Genera un sonido ding-dong amigable"""
    # Ding: 523 Hz (C5), Dong: 392 Hz (G4)
    ding = generate_sine_wave(523, 0.3, sample_rate) * 0.5
    silence = np.zeros(int(0.1 * sample_rate))
    dong = generate_sine_wave(392, 0.4, sample_rate) * 0.5
    
    # Aplicar envelope para suavizar
    fade_samples = int(0.05 * sample_rate)
    ding[:fade_samples] *= np.linspace(0, 1, fade_samples)
    ding[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    dong[:fade_samples] *= np.linspace(0, 1, fade_samples)
    dong[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    return np.concatenate([ding, silence, dong])

def generate_beep_alert(sample_rate=44100):
    """Genera un beep de alerta moderada"""
    beep1 = generate_sine_wave(800, 0.1, sample_rate)
    silence = np.zeros(int(0.05 * sample_rate))
    beep2 = generate_sine_wave(800, 0.1, sample_rate)
    
    # Aplicar envelope
    fade_samples = int(0.01 * sample_rate)
    for beep in [beep1, beep2]:
        beep[:fade_samples] *= np.linspace(0, 1, fade_samples)
        beep[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    return np.concatenate([beep1, silence, beep2]) * 0.7

def generate_alarm_siren(sample_rate=44100):
    """Genera una sirena de alarma crítica"""
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Modulación de frecuencia para efecto sirena
    mod_freq = 4  # Hz
    carrier_freq = 800  # Hz
    freq_deviation = 300  # Hz
    
    modulator = np.sin(2 * np.pi * mod_freq * t)
    frequency = carrier_freq + freq_deviation * modulator
    
    # Generar señal con frecuencia variable
    phase = np.cumsum(2 * np.pi * frequency / sample_rate)
    siren = np.sin(phase) * 0.8
    
    return siren

def create_sound_files():
    """Crea todos los archivos de sonido necesarios"""
    sounds_dir = Path(__file__).parent.parent / "sounds"
    sounds_dir.mkdir(exist_ok=True)
    
    sample_rate = 44100
    
    # Generar sonidos
    sounds = {
        "ding_dong.wav": generate_ding_dong(sample_rate),
        "beep_alert.wav": generate_beep_alert(sample_rate),
        "alarm_siren.wav": generate_alarm_siren(sample_rate)
    }
    
    # Guardar archivos WAV
    for filename, audio_data in sounds.items():
        filepath = sounds_dir / filename
        # Convertir a int16 para WAV
        audio_int16 = np.int16(audio_data * 32767)
        wavfile.write(str(filepath), sample_rate, audio_int16)
        print(f"✅ Creado: {filepath}")
    
    # Crear versiones MP3 (simuladas como WAV por ahora)
    # En producción, usar ffmpeg o pydub para convertir
    for wav_file in sounds_dir.glob("*.wav"):
        mp3_file = wav_file.with_suffix(".mp3")
        if not mp3_file.exists():
            # Por ahora, copiar WAV como MP3 (placeholder)
            import shutil
            shutil.copy(wav_file, mp3_file)
            print(f"✅ Creado placeholder: {mp3_file}")
    
    print("\n🔊 Todos los sonidos creados exitosamente")
    
    # Crear configuración de ejemplo
    create_example_config()

def create_example_config():
    """Crea configuración de ejemplo para audio"""
    config = {
        "enabled": True,
        "zone_configs": {
            "default": {
                "friendly_duration": 30,
                "moderate_duration": 120,
                "enable_voice": True,
                "enable_night_mode": True
            },
            "door_1": {
                "friendly_duration": 15,
                "moderate_duration": 60,
                "enable_voice": True,
                "enable_night_mode": True
            },
            "door_2": {
                "friendly_duration": 60,
                "moderate_duration": 180,
                "enable_voice": True,
                "enable_night_mode": True
            }
        },
        "volume_schedule": {
            "day": {"start": 8, "end": 20, "volume": 0.8},
            "night": {"start": 20, "end": 8, "volume": 0.5}
        }
    }
    
    config_path = Path(__file__).parent.parent / "configs" / "audio_config.json"
    config_path.parent.mkdir(exist_ok=True)
    
    import json
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuración creada: {config_path}")

if __name__ == "__main__":
    create_sound_files()
