#!/usr/bin/env python3
"""
Script de entrenamiento YOLO optimizado para M3 Pro
Detecta puertas abiertas y cerradas
"""

from ultralytics import YOLO
import torch
import yaml
from datetime import datetime
import os

def train_gate_detector():
    print("🚀 Iniciando entrenamiento de detector de puertas")
    print(f"🖥️  Device: {'MPS' if torch.backends.mps.is_available() else 'CPU'}")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuración del dataset
    data_config = {
        'path': '/Users/Shared/yolo11_project/data',
        'train': 'train/images',
        'val': 'val/images',
        'names': {
            0: 'gate_open',
            1: 'gate_closed'
        },
        'nc': 2  # número de clases
    }
    
    # Guardar configuración
    config_path = '/Users/Shared/yolo11_project/configs/gates_data.yaml'
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(data_config, f)
    
    # Inicializar modelo
    model = YOLO('yolo11n.pt')  # Modelo nano para empezar
    
    # Parámetros optimizados para M3 Pro
    training_args = {
        'data': config_path,
        'epochs': 100,          # Suficiente para converger
        'imgsz': 640,          # Tamaño estándar
        'batch': 16,           # Optimizado para M3 Pro
        'patience': 20,        # Early stopping
        'save': True,
        'save_period': 10,     # Guardar cada 10 épocas
        'cache': True,         # Cachear imágenes en RAM
        'device': 'mps',       # Metal Performance Shaders
        'workers': 8,          # Workers para M3 Pro
        'project': 'runs/gates',
        'name': 'gate_detector_v1',
        'exist_ok': True,
        'pretrained': True,
        'optimizer': 'AdamW',
        'verbose': True,
        'seed': 42,
        
        # Hiperparámetros
        'lr0': 0.01,           # Learning rate inicial
        'lrf': 0.01,           # LR final
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3.0,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'box': 7.5,            # Box loss gain
        'cls': 0.5,            # Cls loss gain
        'dfl': 1.5,            # DFL loss gain
        'hsv_h': 0.015,        # Augmentación HSV
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 0.0,        # Sin rotación (puertas siempre verticales)
        'translate': 0.1,
        'scale': 0.5,
        'shear': 0.0,
        'perspective': 0.0,
        'flipud': 0.0,         # Sin flip vertical
        'fliplr': 0.5,         # Flip horizontal permitido
        'mosaic': 1.0,
        'mixup': 0.0,
        'copy_paste': 0.0,
        'auto_augment': 'randaugment',
        'erasing': 0.4,
        'crop_fraction': 1.0,
        
        # Validación
        'val': True,
        'plots': True,
        'overlap_mask': True,
        'mask_ratio': 4,
        'dropout': 0.0,
        
        # Guardar
        'save_json': False,
        'save_hybrid': False,
        'half': False,         # No usar FP16 en MPS
        'dnn': False,
        'plots': True,
        'show': False,
        'save_txt': False,
        'save_conf': False,
        'save_crop': False,
        'hide_labels': False,
        'hide_conf': False,
        'line_width': 3,
    }
    
    print("\n📊 Configuración del entrenamiento:")
    print(f"   - Épocas: {training_args['epochs']}")
    print(f"   - Batch size: {training_args['batch']}")
    print(f"   - Tamaño imagen: {training_args['imgsz']}")
    print(f"   - Device: {training_args['device']}")
    
    # Entrenar
    print("\n🏃 Iniciando entrenamiento...")
    results = model.train(**training_args)
    
    print("\n✅ Entrenamiento completado!")
    print(f"📁 Modelo guardado en: runs/gates/gate_detector_v1/")
    
    # Evaluar modelo final
    print("\n📈 Evaluando modelo en conjunto de validación...")
    metrics = model.val()
    
    print(f"\n📊 Métricas finales:")
    print(f"   - mAP50: {metrics.box.map50:.3f}")
    print(f"   - mAP50-95: {metrics.box.map:.3f}")
    
    return model

if __name__ == "__main__":
    train_gate_detector()
