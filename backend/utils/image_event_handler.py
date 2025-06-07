"""
Utilidades para manejo de imágenes en eventos
"""
import cv2
import base64
import numpy as np
from typing import Optional, Tuple
import io
from PIL import Image
from datetime import datetime
import os

class ImageEventHandler:
    def __init__(self, save_dir: str = "/Users/Shared/yolo11_project/event_images"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def capture_frame_thumbnail(self, frame: np.ndarray, max_size: Tuple[int, int] = (320, 240)) -> str:
        """
        Captura un frame y lo convierte a thumbnail base64
        
        Args:
            frame: Frame de OpenCV (numpy array)
            max_size: Tamaño máximo del thumbnail (ancho, alto)
            
        Returns:
            String base64 del thumbnail
        """
        if frame is None:
            return None
            
        try:
            # Convertir a PIL Image
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Crear thumbnail manteniendo aspecto
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convertir a base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=70)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_base64
        except Exception as e:
            print(f"Error creando thumbnail: {e}")
            return None
    
    def save_event_image(self, frame: np.ndarray, event_id: int, event_type: str) -> Optional[str]:
        """
        Guarda la imagen completa del evento
        
        Args:
            frame: Frame de OpenCV
            event_id: ID del evento
            event_type: Tipo de evento
            
        Returns:
            Ruta del archivo guardado o None si falla
        """
        if frame is None:
            return None
            
        try:
            # Crear nombre de archivo único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{event_type}_{event_id}_{timestamp}.jpg"
            filepath = os.path.join(self.save_dir, filename)
            
            # Guardar imagen
            cv2.imwrite(filepath, frame)
            
            return filepath
        except Exception as e:
            print(f"Error guardando imagen: {e}")
            return None
    
    def draw_event_overlay(self, frame: np.ndarray, event_info: dict) -> np.ndarray:
        """
        Dibuja información del evento sobre el frame
        
        Args:
            frame: Frame original
            event_info: Información del evento (tipo, zona, timestamp, etc)
            
        Returns:
            Frame con overlay
        """
        if frame is None:
            return frame
            
        overlay = frame.copy()
        height, width = frame.shape[:2]
        
        # Fondo semi-transparente para el texto
        cv2.rectangle(overlay, (0, 0), (width, 80), (0, 0, 0), -1)
        
        # Información del evento
        timestamp = event_info.get('timestamp', datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        event_type = event_info.get('event_type', 'Unknown')
        zone = event_info.get('zone_id', 'Unknown')
        
        # Texto del evento
        cv2.putText(overlay, f"EVENTO: {event_type.upper()}", 
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(overlay, f"Zona: {zone} | {timestamp}", 
                    (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Aplicar overlay con transparencia
        return cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
    
    def create_event_collage(self, frames: list, max_frames: int = 4) -> Optional[np.ndarray]:
        """
        Crea un collage de múltiples frames del evento
        
        Args:
            frames: Lista de frames
            max_frames: Número máximo de frames en el collage
            
        Returns:
            Imagen del collage o None
        """
        if not frames:
            return None
            
        # Limitar número de frames
        frames = frames[:max_frames]
        
        # Redimensionar todos los frames al mismo tamaño
        target_size = (320, 240)
        resized_frames = []
        for frame in frames:
            if frame is not None:
                resized = cv2.resize(frame, target_size)
                resized_frames.append(resized)
        
        if not resized_frames:
            return None
            
        # Crear grid 2x2
        if len(resized_frames) == 1:
            return resized_frames[0]
        elif len(resized_frames) == 2:
            return np.hstack(resized_frames)
        elif len(resized_frames) == 3:
            # Agregar frame negro para completar el grid
            black_frame = np.zeros_like(resized_frames[0])
            resized_frames.append(black_frame)
        
        # Crear grid 2x2
        top_row = np.hstack(resized_frames[:2])
        bottom_row = np.hstack(resized_frames[2:4])
        collage = np.vstack([top_row, bottom_row])
        
        return collage

# Instancia global
image_handler = ImageEventHandler()
