#!/usr/bin/env python3
"""
Script para agregar nuevas clases a un modelo YOLO existente
Usa transfer learning para entrenar más rápido
"""

from ultralytics import YOLO
import yaml

def add_new_class_to_model(
    base_model_path="models/gate_detector.pt",
    new_data_yaml="configs/data_with_new_classes.yaml",
    output_name="enhanced_model"
):
    # Cargar modelo existente
    model = YOLO(base_model_path)
    
    # Configuración optimizada para transfer learning
    training_args = {
        'data': new_data_yaml,
        'epochs': 50,        # Menos épocas que entrenamiento inicial
        'imgsz': 640,
        'batch': 16,
        'patience': 20,
        'save': True,
        'name': output_name,
        'exist_ok': True,
        'freeze': 10,        # Congela primeras 10 capas
        'lr0': 0.001,        # Learning rate más bajo
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3.0,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'device': 'mps'      # Para M3 Pro
    }
    
    # Entrenar con nuevas clases
    results = model.train(**training_args)
    
    print(f"✅ Modelo actualizado guardado en: runs/detect/{output_name}/")
    return results

# Ejemplo de uso
if __name__ == "__main__":
    # Para agregar vehículos en el futuro
    add_new_class_to_model(
        base_model_path="models/gate_detector_v1.pt",
        new_data_yaml="configs/data_with_vehicles.yaml",
        output_name="gate_and_vehicles_v2"
    )
