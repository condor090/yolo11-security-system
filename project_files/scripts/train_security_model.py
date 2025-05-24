#!/usr/bin/env python3
"""
Script de entrenamiento para el modelo de seguridad YOLO11
Entrena detección de rejas, personas autorizadas y vehículos
"""

import os
import yaml
import logging
from pathlib import Path
from datetime import datetime
import argparse

from ultralytics import YOLO
import torch

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_security_model(
    data_config: str,
    model_size: str = 'yolo11m.pt',
    epochs: int = 300,
    batch_size: int = 16,
    image_size: int = 640,
    device: str = 'auto',
    project_name: str = 'security_training',
    resume: bool = False
):
    """
    Entrenar modelo YOLO11 para sistema de seguridad
    
    Args:
        data_config: Ruta al archivo de configuración del dataset
        model_size: Tamaño del modelo base
        epochs: Número de épocas de entrenamiento
        batch_size: Tamaño del batch
        image_size: Tamaño de imagen para entrenamiento
        device: Dispositivo de cómputo ('auto', 'cpu', '0', '1', etc.)
        project_name: Nombre del proyecto para organizar runs
        resume: Reanudar entrenamiento desde el último checkpoint
    """
    
    # Verificar configuración
    if not Path(data_config).exists():
        raise FileNotFoundError(f"Configuración no encontrada: {data_config}")
    
    # Cargar configuración del dataset
    with open(data_config, 'r') as f:
        config = yaml.safe_load(f)
    
    logger.info(f"Configuración cargada: {config['nc']} clases")
    logger.info(f"Clases: {list(config['names'].values())}")
    
    # Verificar que existen las rutas del dataset
    train_path = Path(config['train'])
    val_path = Path(config['val'])
    
    if not train_path.parent.exists():
        logger.warning(f"Directorio de entrenamiento no existe: {train_path.parent}")
        train_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not val_path.parent.exists():
        logger.warning(f"Directorio de validación no existe: {val_path.parent}")
        val_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Inicializar modelo
    logger.info(f"Cargando modelo base: {model_size}")
    model = YOLO(model_size)
    
    # Configurar parámetros de entrenamiento
    train_args = {
        'data': data_config,
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': image_size,
        'device': device,
        'project': f'/security_project/runs/{project_name}',
        'name': f'security_model_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'save': True,
        'save_period': 10,  # Guardar checkpoint cada 10 épocas
        'cache': True,
        'workers': 8,
        'patience': 50,
        'resume': resume,
        'amp': True,  # Automatic Mixed Precision
        'fraction': 1.0,
        'profile': False,
        'freeze': None,
        'multi_scale': True,
        'overlap_mask': True,
        'mask_ratio': 4,
        'dropout': 0.0,
        'val': True,
        'split': 'val',
        'save_json': True,
        'save_hybrid': False,
        'conf': None,
        'iou': 0.7,
        'max_det': 300,
        'half': False,
        'dnn': False,
        'plots': True,
        'source': None,
        'vid_stride': 1,
        'stream_buffer': False,
        'visualize': False,
        'augment': False,
        'agnostic_nms': False,
        'classes': None,
        'retina_masks': False,
        'embed': None
    }
    
    # Configuración específica desde el config file
    if 'train_config' in config:
        train_cfg = config['train_config']
        train_args.update({
            'lr0': train_cfg.get('learning_rate', 0.01),
            'momentum': train_cfg.get('momentum', 0.937),
            'weight_decay': train_cfg.get('weight_decay', 0.0005),
            'warmup_epochs': train_cfg.get('warmup_epochs', 3),
            'warmup_momentum': train_cfg.get('warmup_momentum', 0.8),
            'warmup_bias_lr': train_cfg.get('warmup_bias_lr', 0.1)
        })
    
    # Configuración de augmentation
    if 'augmentation' in config:
        aug_cfg = config['augmentation']
        train_args.update({
            'hsv_h': aug_cfg.get('hsv_h', 0.015),
            'hsv_s': aug_cfg.get('hsv_s', 0.7),
            'hsv_v': aug_cfg.get('hsv_v', 0.4),
            'degrees': aug_cfg.get('degrees', 0.0),
            'translate': aug_cfg.get('translate', 0.1),
            'scale': aug_cfg.get('scale', 0.5),
            'fliplr': aug_cfg.get('fliplr', 0.5),
            'flipud': aug_cfg.get('flipud', 0.0),
            'mosaic': aug_cfg.get('mosaic', 1.0),
            'mixup': aug_cfg.get('mixup', 0.0),
            'copy_paste': aug_cfg.get('copy_paste', 0.0)
        })
    
    logger.info("Iniciando entrenamiento...")
    logger.info(f"Parámetros principales:")
    logger.info(f"  - Épocas: {epochs}")
    logger.info(f"  - Batch size: {batch_size}")
    logger.info(f"  - Tamaño imagen: {image_size}")
    logger.info(f"  - Dispositivo: {device}")
    
    # Entrenar modelo
    try:
        results = model.train(**train_args)
        
        logger.info("Entrenamiento completado exitosamente!")
        logger.info(f"Mejor modelo guardado en: {results.save_dir}")
        
        # Copiar mejor modelo a directorio principal
        best_model_path = Path(results.save_dir) / 'weights' / 'best.pt'
        if best_model_path.exists():
            import shutil
            final_model_path = '/security_project/models/security_model_best.pt'
            shutil.copy2(best_model_path, final_model_path)
            logger.info(f"Modelo copiado a: {final_model_path}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error durante el entrenamiento: {e}")
        raise

def validate_model(model_path: str, data_config: str):
    """Validar modelo entrenado"""
    logger.info(f"Validando modelo: {model_path}")
    
    model = YOLO(model_path)
    results = model.val(data=data_config, split='val')
    
    logger.info("Resultados de validación:")
    logger.info(f"mAP50: {results.box.map50:.4f}")
    logger.info(f"mAP50-95: {results.box.map:.4f}")
    
    return results

def export_model(model_path: str, formats: list = ['onnx', 'torchscript']):
    """Exportar modelo a diferentes formatos"""
    logger.info(f"Exportando modelo: {model_path}")
    
    model = YOLO(model_path)
    
    for fmt in formats:
        try:
            model.export(format=fmt, imgsz=640)
            logger.info(f"Modelo exportado a formato: {fmt}")
        except Exception as e:
            logger.error(f"Error exportando a {fmt}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Entrenar modelo YOLO11 de seguridad')
    parser.add_argument('--data', type=str, 
                       default='/security_project/configs/security_dataset.yaml',
                       help='Ruta al archivo de configuración del dataset')
    parser.add_argument('--model', type=str, default='yolo11m.pt',
                       help='Modelo base (yolo11n.pt, yolo11s.pt, yolo11m.pt, yolo11l.pt, yolo11x.pt)')
    parser.add_argument('--epochs', type=int, default=300,
                       help='Número de épocas')
    parser.add_argument('--batch', type=int, default=16,
                       help='Tamaño del batch')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='Tamaño de imagen')
    parser.add_argument('--device', type=str, default='auto',
                       help='Dispositivo de cómputo')
    parser.add_argument('--project', type=str, default='security_training',
                       help='Nombre del proyecto')
    parser.add_argument('--resume', action='store_true',
                       help='Reanudar entrenamiento')
    parser.add_argument('--validate', action='store_true',
                       help='Solo validar modelo existente')
    parser.add_argument('--export', action='store_true',
                       help='Exportar modelo a otros formatos')
    
    args = parser.parse_args()
    
    # Crear directorios necesarios
    os.makedirs('/security_project/runs', exist_ok=True)
    os.makedirs('/security_project/models', exist_ok=True)
    
    if args.validate:
        model_path = '/security_project/models/security_model_best.pt'
        if Path(model_path).exists():
            validate_model(model_path, args.data)
        else:
            logger.error(f"Modelo no encontrado: {model_path}")
    
    elif args.export:
        model_path = '/security_project/models/security_model_best.pt'
        if Path(model_path).exists():
            export_model(model_path)
        else:
            logger.error(f"Modelo no encontrado: {model_path}")
    
    else:
        # Entrenar modelo
        results = train_security_model(
            data_config=args.data,
            model_size=args.model,
            epochs=args.epochs,
            batch_size=args.batch,
            image_size=args.imgsz,
            device=args.device,
            project_name=args.project,
            resume=args.resume
        )
        
        logger.info("Proceso de entrenamiento finalizado")

if __name__ == "__main__":
    main()
