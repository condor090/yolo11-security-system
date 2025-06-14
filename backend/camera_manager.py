"""
Camera Manager - Gestión de cámaras Hikvision
Maneja streams RTSP y configuración de cámaras
Ahora con almacenamiento en base de datos SQLite
"""

import cv2
import asyncio
import threading
from typing import Dict, Optional, Any
from dataclasses import dataclass
import logging
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

# Importar el gestor de base de datos
try:
    from backend.utils.camera_config_db import camera_config_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    camera_config_db = None

logger = logging.getLogger(__name__)

@dataclass
class CameraConfig:
    """Configuración de una cámara"""
    id: str
    name: str
    ip: str
    username: str
    password: str
    rtsp_port: int = 554
    channel: int = 1
    stream: str = "main"  # main o sub
    zone_id: Optional[str] = None  # Vinculado a door_id
    enabled: bool = True
    
    @property
    def rtsp_url(self) -> str:
        """Generar URL RTSP para Hikvision"""
        # Para Hikvision: canal 1 = 101 (main) o 102 (sub)
        # canal 2 = 201 (main) o 202 (sub), etc.
        stream_suffix = "1" if self.stream == "main" else "2"
        channel_id = f"{self.channel}0{stream_suffix}"
        return f"rtsp://{self.username}:{self.password}@{self.ip}:{self.rtsp_port}/Streaming/Channels/{channel_id}"

class VideoBuffer:
    """Buffer circular para almacenar frames con timestamp"""
    def __init__(self, duration_seconds: int = 60):
        self.duration = duration_seconds
        self.frames = []
        self.timestamps = []
        self.max_frames = duration_seconds * 30  # Asumiendo 30 fps
        
    def add_frame(self, frame: np.ndarray):
        """Agregar frame al buffer"""
        self.frames.append(frame)
        self.timestamps.append(datetime.now())
        
        # Mantener solo los frames necesarios
        if len(self.frames) > self.max_frames:
            self.frames.pop(0)
            self.timestamps.pop(0)
    
    def get_frames_range(self, start_time: datetime, end_time: datetime):
        """Obtener frames en un rango de tiempo"""
        frames_in_range = []
        for i, timestamp in enumerate(self.timestamps):
            if start_time <= timestamp <= end_time:
                frames_in_range.append((self.frames[i], timestamp))
        return frames_in_range

class CameraStream:
    """Maneja un stream individual de cámara"""
    def __init__(self, config: CameraConfig):
        self.config = config
        self.cap = None
        self.is_running = False
        self.thread = None
        self.current_frame = None
        self.buffer = VideoBuffer(duration_seconds=120)  # 2 minutos de buffer
        self.error_count = 0
        self.last_error = None
        self.fps = 0
        self.frame_count = 0
        self.recording = False
        self.video_writer = None
        
    def connect(self) -> bool:
        """Conectar a la cámara"""
        try:
            logger.info(f"Conectando a cámara {self.config.name} en {self.config.ip}")
            
            # Opciones para mejorar la conexión RTSP
            self.cap = cv2.VideoCapture(self.config.rtsp_url)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir buffer para menor latencia
            
            # Verificar conexión
            if not self.cap.isOpened():
                raise Exception("No se pudo abrir el stream RTSP")
            
            # Leer un frame de prueba
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise Exception("No se pudo leer frame de la cámara")
            
            logger.info(f"Cámara {self.config.name} conectada exitosamente")
            self.error_count = 0
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a {self.config.name}: {e}")
            self.last_error = str(e)
            self.error_count += 1
            if self.cap:
                self.cap.release()
            return False
    
    def start(self):
        """Iniciar captura en thread separado"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        """Detener captura"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        if self.video_writer:
            self.video_writer.release()
    
    def _capture_loop(self):
        """Loop de captura en thread separado"""
        import time
        max_retries = 3
        retry_delay = 5  # segundos entre reintentos
        
        # Intentar conectar con límite de reintentos
        for attempt in range(max_retries):
            if self.connect():
                break
            if attempt < max_retries - 1:
                logger.warning(f"Intento {attempt + 1}/{max_retries} fallido para {self.config.name}, reintentando en {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"No se pudo conectar a {self.config.name} después de {max_retries} intentos. Deteniendo stream.")
                self.is_running = False
                return
        
        fps_counter = 0
        fps_timer = datetime.now()
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.current_frame = frame
                    self.buffer.add_frame(frame.copy())
                    self.frame_count += 1
                    fps_counter += 1
                    consecutive_errors = 0  # Reset error counter on success
                    
                    # Calcular FPS
                    if (datetime.now() - fps_timer).total_seconds() >= 1.0:
                        self.fps = fps_counter
                        fps_counter = 0
                        fps_timer = datetime.now()
                    
                    # Grabar si está activo
                    if self.recording and self.video_writer:
                        self.video_writer.write(frame)
                else:
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"Demasiados errores consecutivos ({consecutive_errors}) para {self.config.name}. Deteniendo stream.")
                        self.is_running = False
                        break
                    
                    # Reconectar si se pierde la conexión
                    logger.warning(f"Frame perdido de {self.config.name} (error {consecutive_errors}/{max_consecutive_errors})")
                    self.cap.release()
                    time.sleep(1)  # Breve pausa antes de reconectar
                    
                    if not self.connect():
                        time.sleep(retry_delay)  # Esperar antes de reintentar
                        
            except Exception as e:
                logger.error(f"Error en loop de captura {self.config.name}: {e}")
                self.error_count += 1
                consecutive_errors += 1
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"Demasiados errores para {self.config.name}. Deteniendo stream.")
                    self.is_running = False
                    break
                    
                time.sleep(1)  # Pausa antes de continuar
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Obtener el frame actual"""
        return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_context_video(self, event_time: datetime, before_seconds: int = 30, after_seconds: int = 30):
        """Obtener video de contexto alrededor de un evento"""
        start_time = event_time - timedelta(seconds=before_seconds)
        end_time = event_time + timedelta(seconds=after_seconds)
        return self.buffer.get_frames_range(start_time, end_time)
    
    def start_recording(self, output_path: str):
        """Iniciar grabación"""
        if self.current_frame is not None:
            h, w = self.current_frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(output_path, fourcc, 20.0, (w, h))
            self.recording = True
            logger.info(f"Grabación iniciada: {output_path}")
    
    def stop_recording(self):
        """Detener grabación"""
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        self.recording = False
        logger.info("Grabación detenida")

class CameraManager:
    """Gestor central de todas las cámaras"""
    def __init__(self, config_path: str = "cameras/camera_config.json"):
        self.config_path = Path(config_path)
        self.cameras: Dict[str, CameraStream] = {}
        self.configs: Dict[str, CameraConfig] = {}
        self.use_db = DB_AVAILABLE and camera_config_db is not None
        
        if self.use_db:
            logger.info("Usando base de datos SQLite para configuraciones de cámaras")
        else:
            logger.warning("Base de datos no disponible, usando archivo JSON")
            
        self.load_configs()
        
    def load_configs(self):
        """Cargar configuraciones de cámaras desde base de datos o archivo"""
        if self.use_db:
            # Cargar desde base de datos
            try:
                configs_data = camera_config_db.get_all_camera_configs()
                for cam_id, cam_data in configs_data.items():
                    # Convertir de dict a CameraConfig
                    config_params = {
                        'id': cam_data['id'],
                        'name': cam_data['name'],
                        'ip': cam_data['ip'],
                        'username': cam_data['username'],
                        'password': cam_data['password'],
                        'rtsp_port': cam_data.get('rtsp_port', 554),
                        'channel': cam_data.get('channel', 1),
                        'stream': cam_data.get('stream', 'main'),
                        'zone_id': cam_data.get('zone_id'),
                        'enabled': cam_data.get('enabled', True)
                    }
                    self.configs[cam_id] = CameraConfig(**config_params)
                logger.info(f"Cargadas {len(self.configs)} cámaras desde base de datos")
            except Exception as e:
                logger.error(f"Error cargando configuraciones desde DB: {e}")
                # Fallback a JSON
                self._load_from_json()
        else:
            # Cargar desde JSON
            self._load_from_json()
            
    def _load_from_json(self):
        """Cargar configuraciones desde archivo JSON (fallback)"""
        self.config_path.parent.mkdir(exist_ok=True)
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    configs_data = json.load(f)
                    for cam_id, cam_data in configs_data.items():
                        self.configs[cam_id] = CameraConfig(**cam_data)
                logger.info(f"Cargadas {len(self.configs)} cámaras desde JSON")
            except Exception as e:
                logger.error(f"Error cargando configuraciones desde JSON: {e}")
        
    def save_configs(self):
        """Guardar configuraciones actuales"""
        if self.use_db:
            # Guardar en base de datos
            try:
                for cam_id, config in self.configs.items():
                    config_dict = {
                        'id': config.id,
                        'name': config.name,
                        'ip': config.ip,
                        'username': config.username,
                        'password': config.password,
                        'rtsp_port': config.rtsp_port,
                        'channel': config.channel,
                        'stream': config.stream,
                        'zone_id': config.zone_id,
                        'enabled': config.enabled
                    }
                    camera_config_db.save_camera_config(config_dict)
                logger.info("Configuraciones guardadas en base de datos")
            except Exception as e:
                logger.error(f"Error guardando en DB: {e}")
                # Fallback a JSON
                self._save_to_json()
        else:
            # Guardar en JSON
            self._save_to_json()
            
    def _save_to_json(self):
        """Guardar configuraciones en archivo JSON (fallback)"""
        configs_data = {}
        for cam_id, config in self.configs.items():
            configs_data[cam_id] = {
                'id': config.id,
                'name': config.name,
                'ip': config.ip,
                'username': config.username,
                'password': config.password,
                'rtsp_port': config.rtsp_port,
                'channel': config.channel,
                'stream': config.stream,
                'zone_id': config.zone_id,
                'enabled': config.enabled
            }
        
        with open(self.config_path, 'w') as f:
            json.dump(configs_data, f, indent=2)
        logger.info("Configuraciones guardadas en JSON")
    
    def add_camera(self, config: CameraConfig):
        """Agregar nueva cámara"""
        self.configs[config.id] = config
        self.save_configs()
        
        if config.enabled:
            self.start_camera(config.id)
    
    def remove_camera(self, camera_id: str):
        """Eliminar cámara"""
        if camera_id in self.cameras:
            self.stop_camera(camera_id)
        
        if camera_id in self.configs:
            del self.configs[camera_id]
            
            # Eliminar de base de datos
            if self.use_db:
                try:
                    camera_config_db.delete_camera_config(camera_id)
                    logger.info(f"Cámara {camera_id} eliminada de DB")
                except Exception as e:
                    logger.error(f"Error eliminando de DB: {e}")
            
            # También actualizar el archivo JSON para mantener sincronización
            self.save_configs()
    
    def start_camera(self, camera_id: str):
        """Iniciar stream de una cámara"""
        if camera_id in self.configs and camera_id not in self.cameras:
            config = self.configs[camera_id]
            stream = CameraStream(config)
            stream.start()
            self.cameras[camera_id] = stream
            logger.info(f"Cámara {config.name} iniciada")
    
    def stop_camera(self, camera_id: str):
        """Detener stream de una cámara"""
        if camera_id in self.cameras:
            self.cameras[camera_id].stop()
            del self.cameras[camera_id]
            logger.info(f"Cámara {camera_id} detenida")
    
    def start_all(self):
        """Iniciar todas las cámaras habilitadas"""
        for cam_id, config in self.configs.items():
            if config.enabled:
                self.start_camera(cam_id)
    
    def stop_all(self):
        """Detener todas las cámaras"""
        for cam_id in list(self.cameras.keys()):
            self.stop_camera(cam_id)
    
    def get_camera_by_zone(self, zone_id: str) -> Optional[CameraStream]:
        """Obtener cámara asociada a una zona"""
        for config in self.configs.values():
            if config.zone_id == zone_id and config.id in self.cameras:
                return self.cameras[config.id]
        return None
    
    def get_camera_status(self) -> Dict[str, Any]:
        """Obtener estado de todas las cámaras"""
        status = {}
        for cam_id, config in self.configs.items():
            if cam_id in self.cameras:
                stream = self.cameras[cam_id]
                status[cam_id] = {
                    'name': config.name,
                    'enabled': config.enabled,
                    'connected': stream.current_frame is not None,
                    'fps': stream.fps,
                    'frames': stream.frame_count,
                    'recording': stream.recording,
                    'errors': stream.error_count,
                    'last_error': stream.last_error
                }
            else:
                status[cam_id] = {
                    'name': config.name,
                    'enabled': config.enabled,
                    'connected': False,
                    'status': 'stopped'
                }
        return status

# Configuración de ejemplo
EXAMPLE_CONFIG = {
    "cam_001": {
        "id": "cam_001",
        "name": "Entrada Principal",
        "ip": "192.168.1.100",
        "username": "admin",
        "password": "password",
        "rtsp_port": 554,
        "channel": 1,
        "stream": "main",
        "zone_id": "door_1",
        "enabled": True
    }
}

if __name__ == "__main__":
    # Test del sistema
    manager = CameraManager()
    
    # Agregar cámara de ejemplo
    if not manager.configs:
        config = CameraConfig(**EXAMPLE_CONFIG["cam_001"])
        manager.add_camera(config)
    
    # Iniciar todas las cámaras
    manager.start_all()
    
    # Mantener corriendo
    try:
        while True:
            status = manager.get_camera_status()
            print(f"Estado: {json.dumps(status, indent=2)}")
            asyncio.sleep(5)
    except KeyboardInterrupt:
        manager.stop_all()
