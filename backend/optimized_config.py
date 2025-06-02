"""
Configuración optimizada para reducir consumo de CPU
"""

# Configuración de detección
DETECTION_CONFIG = {
    "enabled": True,
    "interval": 2.0,  # Detectar cada 2 segundos (antes 0.5)
    "confidence_threshold": 0.75,
    "max_fps": 15,  # Limitar FPS (antes 30)
    "jpeg_quality": 60,  # Reducir calidad (antes 70)
    "enable_motion_detection": True,  # Solo detectar si hay movimiento
    "motion_threshold": 0.02,  # Umbral de movimiento
    "idle_timeout": 10,  # Pausar detección después de 10s sin movimiento
}

# Configuración de recursos
RESOURCE_CONFIG = {
    "max_workers": 2,  # Limitar threads
    "buffer_size": 30,  # Reducir buffer de frames (antes 60)
    "enable_gpu": False,  # Desactivar GPU por ahora
    "batch_size": 1,  # Procesar de a 1 frame
}

# Configuración de cámara
CAMERA_CONFIG = {
    "resolution": (640, 480),  # Reducir resolución
    "capture_fps": 15,  # Capturar a 15 FPS
    "buffer_frames": False,  # No almacenar frames extras
}
