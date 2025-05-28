"""
Modo Eco Inteligente para optimización de recursos
Reduce consumo de CPU hasta 90% en períodos de inactividad
"""

import cv2
import time
import numpy as np
from enum import Enum
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SystemState(Enum):
    """Estados del sistema según actividad"""
    IDLE = "idle"        # Sin actividad
    ALERT = "alert"      # Movimiento detectado
    ACTIVE = "active"    # Puerta abierta detectada

class EcoModeManager:
    """
    Gestor del Modo Eco Inteligente
    Ajusta recursos según la actividad detectada
    """
    
    def __init__(self):
        self.current_state = SystemState.IDLE
        self.last_motion_time = time.time()  # Inicializar con tiempo actual
        self.last_detection_time = time.time()  # Inicializar con tiempo actual
        self.previous_frame = None
        self.motion_threshold = 0.02  # 2% de píxeles cambiados
        self.frame_count = 0  # Contador de frames procesados
        
        # Configuración por estado
        self.state_configs = {
            SystemState.IDLE: {
                'detection_interval': 5.0,    # Detectar cada 5s
                'fps': 5,                     # Solo 5 FPS
                'yolo_enabled': False,        # YOLO apagado
                'resolution_scale': 0.5,      # Mitad de resolución
                'jpeg_quality': 50            # Calidad mínima
            },
            SystemState.ALERT: {
                'detection_interval': 2.0,    # Detectar cada 2s
                'fps': 15,                    # 15 FPS
                'yolo_enabled': True,         # YOLO activo
                'resolution_scale': 0.75,     # 75% resolución
                'jpeg_quality': 60            # Calidad media
            },
            SystemState.ACTIVE: {
                'detection_interval': 0.5,    # Máxima frecuencia
                'fps': 30,                    # Máximo FPS
                'yolo_enabled': True,         # YOLO activo
                'resolution_scale': 1.0,      # Resolución completa
                'jpeg_quality': 70            # Calidad alta
            }
        }
        
        # Timeouts para cambio de estado
        self.idle_timeout = 30.0      # 30s sin movimiento → IDLE
        self.alert_timeout = 10.0     # 10s sin detección → ALERT
        
        logger.info(f"Modo Eco Inteligente inicializado en estado {self.current_state.value}")
        logger.info(f"Configuración: motion_threshold={self.motion_threshold}, idle_timeout={self.idle_timeout}s")
    
    def detect_motion(self, frame: np.ndarray) -> bool:
        """
        Detecta movimiento comparando frames con manejo robusto de errores
        """
        try:
            # Validar frame de entrada
            if frame is None or frame.size == 0:
                return False
                
            # Reducir resolución para análisis rápido y consistente
            target_width = 320
            target_height = 240
            
            # Redimensionar a tamaño fijo para evitar problemas de tamaño
            small_frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            
            # Aplicar desenfoque gaussiano para reducir ruido
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # Primera vez, inicializar frame anterior
            if self.previous_frame is None:
                self.previous_frame = gray.copy()
                logger.debug("Frame inicial capturado para detección de movimiento")
                return False
            
            # Asegurar que ambos frames tengan el mismo tamaño
            if self.previous_frame.shape != gray.shape:
                logger.warning(f"Tamaño de frame cambió: {self.previous_frame.shape} -> {gray.shape}")
                self.previous_frame = gray.copy()
                return False
            
            # Calcular diferencia absoluta entre frames
            frame_diff = cv2.absdiff(self.previous_frame, gray)
            
            # Aplicar threshold para obtener imagen binaria
            _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
            
            # Aplicar operaciones morfológicas para eliminar ruido
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            thresh = cv2.dilate(thresh, kernel, iterations=2)
            
            # Encontrar contornos para validar que es movimiento real
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contornos pequeños (ruido)
            min_area = 500  # Área mínima para considerar movimiento real
            valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
            
            # Calcular área total de movimiento
            total_motion_area = sum(cv2.contourArea(c) for c in valid_contours)
            total_frame_area = target_width * target_height
            motion_percentage = total_motion_area / total_frame_area
            
            # Actualizar frame anterior con factor de aprendizaje
            # Esto ayuda a adaptarse a cambios graduales de iluminación
            alpha = 0.1  # Factor de aprendizaje
            self.previous_frame = cv2.addWeighted(gray, alpha, self.previous_frame, 1.0 - alpha, 0)
            
            # Detectar si hay movimiento significativo
            has_motion = motion_percentage > self.motion_threshold
            
            if has_motion:
                self.last_motion_time = time.time()
                logger.info(f"Movimiento detectado: {motion_percentage:.2%} del frame ({len(valid_contours)} objetos)")
                
                # Si estamos en IDLE y detectamos movimiento, cambiar a ALERT
                if self.current_state == SystemState.IDLE:
                    self.current_state = SystemState.ALERT
                    logger.info("Estado cambiado: IDLE → ALERT por detección de movimiento")
            
            return has_motion
            
        except Exception as e:
            logger.error(f"Error en detección de movimiento: {e}")
            # En caso de error, resetear el frame anterior
            self.previous_frame = None
            return False
    
    def update_state(self, detection_found: bool = False):
        """
        Actualiza el estado del sistema según la actividad
        """
        current_time = time.time()
        previous_state = self.current_state
        
        if detection_found:
            # Si se detectó una puerta abierta → ACTIVE
            self.current_state = SystemState.ACTIVE
            self.last_detection_time = current_time
            
        elif self.current_state == SystemState.ACTIVE:
            # En estado ACTIVE, verificar si debe bajar a ALERT
            if current_time - self.last_detection_time > self.alert_timeout:
                self.current_state = SystemState.ALERT
                
        elif self.current_state == SystemState.ALERT:
            # En estado ALERT, verificar si debe bajar a IDLE
            if current_time - self.last_motion_time > self.idle_timeout:
                self.current_state = SystemState.IDLE
                
        elif self.current_state == SystemState.IDLE:
            # En estado IDLE, verificar si hay movimiento
            # (esto se maneja externamente con detect_motion)
            pass
        
        # Log cambios de estado
        if previous_state != self.current_state:
            logger.info(f"Estado cambiado: {previous_state.value} → {self.current_state.value}")
            self._log_resource_usage()
    
    def should_run_detection(self) -> bool:
        """
        Determina si debe ejecutar detección YOLO según el estado
        """
        config = self.get_current_config()
        return config['yolo_enabled']
    
    def get_current_config(self) -> dict:
        """
        Obtiene la configuración actual según el estado
        """
        return self.state_configs[self.current_state]
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Procesa un frame según el estado actual del sistema
        
        Args:
            frame: Frame original de la cámara
            
        Returns:
            Tuple de (frame procesado, configuración actual)
        """
        if frame is None or frame.size == 0:
            return frame, self.get_current_config()
            
        config = self.get_current_config()
        
        # Solo ajustar resolución si es necesario y diferente de 1.0
        if config['resolution_scale'] < 1.0:
            height, width = frame.shape[:2]
            new_width = int(width * config['resolution_scale'])
            new_height = int(height * config['resolution_scale'])
            
            # Asegurar dimensiones pares para evitar problemas con codecs
            new_width = new_width if new_width % 2 == 0 else new_width + 1
            new_height = new_height if new_height % 2 == 0 else new_height + 1
            
            try:
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            except Exception as e:
                logger.error(f"Error redimensionando frame: {e}")
        
        return frame, config
    
    def get_frame_delay(self) -> float:
        """
        Obtiene el delay entre frames según FPS configurado
        """
        config = self.get_current_config()
        return 1.0 / config['fps']
    
    def get_detection_interval(self) -> float:
        """
        Obtiene el intervalo de detección según estado
        """
        config = self.get_current_config()
        return config['detection_interval']
    
    def _log_resource_usage(self):
        """
        Log del uso estimado de recursos por estado
        """
        estimates = {
            SystemState.IDLE: "~5% CPU, 100MB RAM",
            SystemState.ALERT: "~20% CPU, 300MB RAM",
            SystemState.ACTIVE: "~50% CPU, 800MB RAM"
        }
        
        logger.info(f"Uso estimado en estado {self.current_state.value}: {estimates[self.current_state]}")
    
    def get_status(self) -> dict:
        """
        Obtiene el estado actual del sistema
        """
        config = self.get_current_config()
        current_time = time.time()
        
        return {
            'state': self.current_state.value,
            'config': config,
            'time_since_motion': current_time - self.last_motion_time,
            'time_since_detection': current_time - self.last_detection_time,
            'motion_threshold': self.motion_threshold,
            'estimated_cpu': {
                'idle': '5%',
                'alert': '20%',
                'active': '50%'
            }[self.current_state.value]
        }
