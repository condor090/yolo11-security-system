#!/usr/bin/env python3
"""
YOLO11 Security System - Sistema de Seguridad con Detección Inteligente
Detección de rejas, personas autorizadas y vehículos

Autor: Security Vision Project
Fecha: 2025
"""

import cv2
import numpy as np
import time
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/security_project/logs/security_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    import torch
except ImportError as e:
    logger.error(f"Error importando dependencias: {e}")
    raise

class SecurityDetector:
    """
    Detector de seguridad basado en YOLO11
    Detecta rejas abiertas/cerradas, personas autorizadas y vehículos
    """
    
    def __init__(self, model_path: str, config_path: str):
        """
        Inicializar el detector de seguridad
        
        Args:
            model_path: Ruta al modelo YOLO11 entrenado
            config_path: Ruta al archivo de configuración
        """
        self.model_path = Path(model_path)
        self.config_path = Path(config_path)
        
        # Cargar configuración
        self.config = self._load_config()
        
        # Inicializar modelo
        self.model = self._load_model()
        
        # Configurar clases
        self.class_names = self.config['names']
        self.num_classes = self.config['nc']
        
        # Contadores y estadísticas
        self.detection_stats = {
            'total_detections': 0,
            'gate_status_changes': 0,
            'unauthorized_alerts': 0,
            'vehicle_detections': 0
        }
        
        # Estado actual del sistema
        self.current_state = {
            'gate_status': 'unknown',
            'persons_detected': [],
            'vehicles_detected': [],
            'last_update': None,
            'alerts': []
        }
        
        logger.info("Sistema de seguridad inicializado correctamente")
    
    def _load_config(self) -> dict:
        """Cargar configuración desde archivo YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuración cargada desde {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            raise
    
    def _load_model(self) -> YOLO:
        """Cargar modelo YOLO11"""
        try:
            if self.model_path.exists():
                model = YOLO(str(self.model_path))
                logger.info(f"Modelo personalizado cargado: {self.model_path}")
            else:
                # Usar modelo base si no existe el personalizado
                model = YOLO('yolo11m.pt')
                logger.warning("Usando modelo base YOLO11m - Entrenar modelo personalizado")
            
            # Verificar GPU
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Dispositivo de cómputo: {device}")
            
            return model
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise
    
    def detect_frame(self, frame: np.ndarray, confidence: float = 0.6) -> dict:
        """
        Procesar un frame y detectar objetos de seguridad
        
        Args:
            frame: Frame de video/imagen
            confidence: Umbral de confianza para detecciones
            
        Returns:
            dict: Resultados de detección procesados
        """
        try:
            # Ejecutar detección
            results = self.model(frame, conf=confidence, iou=0.5)
            
            # Procesar resultados
            detections = self._process_detections(results[0])
            
            # Analizar estado del sistema
            self._analyze_security_state(detections)
            
            # Actualizar estadísticas
            self._update_stats(detections)
            
            return {
                'detections': detections,
                'system_state': self.current_state.copy(),
                'stats': self.detection_stats.copy(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en detección: {e}")
            return {'error': str(e)}
    
    def _process_detections(self, results) -> List[dict]:
        """Procesar resultados de YOLO en formato estructurado"""
        detections = []
        
        if results.boxes is not None:
            boxes = results.boxes.cpu().numpy()
            
            for i, box in enumerate(boxes):
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                coords = box.xyxy[0].tolist()
                
                detection = {
                    'class_id': cls,
                    'class_name': self.class_names.get(cls, f'class_{cls}'),
                    'confidence': conf,
                    'bbox': {
                        'x1': int(coords[0]),
                        'y1': int(coords[1]),
                        'x2': int(coords[2]),
                        'y2': int(coords[3])
                    },
                    'center': {
                        'x': int((coords[0] + coords[2]) / 2),
                        'y': int((coords[1] + coords[3]) / 2)
                    }
                }
                detections.append(detection)
        
        return detections
    
    def _analyze_security_state(self, detections: List[dict]):
        """Analizar estado de seguridad basado en detecciones"""
        current_time = datetime.now()
        
        # Analizar estado de la reja
        gate_detections = [d for d in detections if 'gate' in d['class_name']]
        if gate_detections:
            # Tomar la detección con mayor confianza
            best_gate = max(gate_detections, key=lambda x: x['confidence'])
            new_status = best_gate['class_name']
            
            if self.current_state['gate_status'] != new_status:
                self.current_state['gate_status'] = new_status
                self.detection_stats['gate_status_changes'] += 1
                logger.info(f"Cambio de estado de reja: {new_status}")
        
        # Analizar personas
        person_detections = [d for d in detections if 'person' in d['class_name']]
        self.current_state['persons_detected'] = person_detections
        
        # Verificar personas no autorizadas
        unauthorized = [d for d in person_detections if d['class_name'] == 'unauthorized_person']
        if unauthorized:
            self.detection_stats['unauthorized_alerts'] += len(unauthorized)
            alert = {
                'type': 'unauthorized_person',
                'count': len(unauthorized),
                'timestamp': current_time.isoformat(),
                'locations': [d['center'] for d in unauthorized]
            }
            self.current_state['alerts'].append(alert)
            logger.warning(f"ALERTA: {len(unauthorized)} persona(s) no autorizada(s) detectada(s)")
        
        # Analizar vehículos
        vehicle_classes = ['truck', 'car', 'motorcycle']
        vehicle_detections = [d for d in detections if d['class_name'] in vehicle_classes]
        self.current_state['vehicles_detected'] = vehicle_detections
        
        if vehicle_detections:
            self.detection_stats['vehicle_detections'] += len(vehicle_detections)
        
        # Limpiar alertas antiguas (mantener solo las últimas 10)
        self.current_state['alerts'] = self.current_state['alerts'][-10:]
        self.current_state['last_update'] = current_time.isoformat()
    
    def _update_stats(self, detections: List[dict]):
        """Actualizar estadísticas del sistema"""
        self.detection_stats['total_detections'] += len(detections)
    
    def draw_detections(self, frame: np.ndarray, detection_results: dict) -> np.ndarray:
        """
        Dibujar detecciones en el frame
        
        Args:
            frame: Frame original
            detection_results: Resultados de detección
            
        Returns:
            np.ndarray: Frame con detecciones dibujadas
        """
        if 'detections' not in detection_results:
            return frame
        
        frame_copy = frame.copy()
        detections = detection_results['detections']
        
        # Colores por clase
        colors = {
            'gate_open': (0, 255, 0),      # Verde
            'gate_closed': (0, 0, 255),    # Rojo
            'authorized_person': (255, 255, 0),  # Cian
            'unauthorized_person': (0, 0, 255),  # Rojo
            'truck': (255, 0, 255),        # Magenta
            'car': (0, 255, 255),          # Amarillo
            'motorcycle': (128, 0, 128)    # Púrpura
        }
        
        for detection in detections:
            bbox = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # Color de la clase
            color = colors.get(class_name, (255, 255, 255))
            
            # Dibujar bounding box
            cv2.rectangle(frame_copy, 
                         (bbox['x1'], bbox['y1']), 
                         (bbox['x2'], bbox['y2']), 
                         color, 2)
            
            # Etiqueta
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Fondo de la etiqueta
            cv2.rectangle(frame_copy,
                         (bbox['x1'], bbox['y1'] - label_size[1] - 10),
                         (bbox['x1'] + label_size[0], bbox['y1']),
                         color, -1)
            
            # Texto de la etiqueta
            cv2.putText(frame_copy, label,
                       (bbox['x1'], bbox['y1'] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                       (0, 0, 0), 2)
        
        # Información del sistema en la esquina
        self._draw_system_info(frame_copy, detection_results)
        
        return frame_copy
    
    def _draw_system_info(self, frame: np.ndarray, detection_results: dict):
        """Dibujar información del sistema en el frame"""
        system_state = detection_results.get('system_state', {})
        
        # Preparar información
        info_lines = [
            f"Estado Reja: {system_state.get('gate_status', 'unknown')}",
            f"Personas: {len(system_state.get('persons_detected', []))}",
            f"Vehículos: {len(system_state.get('vehicles_detected', []))}",
            f"Alertas: {len(system_state.get('alerts', []))}"
        ]
        
        # Fondo semi-transparente
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Texto
        for i, line in enumerate(info_lines):
            cv2.putText(frame, line, (20, 35 + i * 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def save_state(self, filepath: str):
        """Guardar estado actual del sistema"""
        state_data = {
            'current_state': self.current_state,
            'detection_stats': self.detection_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Estado guardado en {filepath}")
        except Exception as e:
            logger.error(f"Error guardando estado: {e}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='YOLO11 Security System')
    parser.add_argument('--model', type=str, 
                       default='/security_project/models/security_model.pt',
                       help='Ruta al modelo entrenado')
    parser.add_argument('--config', type=str,
                       default='/security_project/configs/security_dataset.yaml',
                       help='Ruta al archivo de configuración')
    parser.add_argument('--source', type=str, default='0',
                       help='Fuente de video (webcam=0, archivo=ruta, rtsp=url)')
    parser.add_argument('--save-video', action='store_true',
                       help='Guardar video con detecciones')
    parser.add_argument('--confidence', type=float, default=0.6,
                       help='Umbral de confianza')
    
    args = parser.parse_args()
    
    # Inicializar detector
    detector = SecurityDetector(args.model, args.config)
    
    # Configurar fuente de video
    if args.source.isdigit():
        cap = cv2.VideoCapture(int(args.source))
    else:
        cap = cv2.VideoCapture(args.source)
    
    if not cap.isOpened():
        logger.error("Error abriendo fuente de video")
        return
    
    # Configurar grabación si se solicita
    if args.save_video:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        output_path = f"/security_project/runs/security_output_{int(time.time())}.mp4"
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        logger.info(f"Guardando video en: {output_path}")
    
    logger.info("Iniciando sistema de seguridad. Presiona 'q' para salir.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Procesar frame
            results = detector.detect_frame(frame, confidence=args.confidence)
            
            # Dibujar detecciones
            frame_with_detections = detector.draw_detections(frame, results)
            
            # Mostrar frame
            cv2.imshow('YOLO11 Security System', frame_with_detections)
            
            # Guardar frame si se solicita
            if args.save_video:
                out.write(frame_with_detections)
            
            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        logger.info("Interrumpido por usuario")
    
    finally:
        # Limpiar recursos
        cap.release()
        if args.save_video:
            out.release()
        cv2.destroyAllWindows()
        
        # Guardar estado final
        detector.save_state('/security_project/logs/final_state.json')
        logger.info("Sistema de seguridad finalizado")

if __name__ == "__main__":
    main()
