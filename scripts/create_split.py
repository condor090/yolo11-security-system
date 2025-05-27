#!/usr/bin/env python3
"""
Script para dividir el dataset en train/val (80/20)
Mantiene el balance de clases en ambos conjuntos
"""

import os
import shutil
import random
from pathlib import Path

def create_train_val_split(train_ratio=0.8):
    # Directorios
    base_dir = Path("/Users/Shared/yolo11_project/data")
    train_labels = base_dir / "train" / "labels"
    train_images = base_dir / "train" / "images"
    val_labels = base_dir / "val" / "labels"
    val_images = base_dir / "val" / "images"
    
    # Crear directorios val
    val_labels.mkdir(parents=True, exist_ok=True)
    val_images.mkdir(parents=True, exist_ok=True)
    
    # Copiar classes.txt a val
    shutil.copy2(train_labels / "classes.txt", val_labels / "classes.txt")
    
    # Obtener todas las etiquetas por clase
    gate_open_files = []
    gate_closed_files = []
    
    for label_file in train_labels.glob("*.txt"):
        if label_file.name == "classes.txt":
            continue
            
        with open(label_file, 'r') as f:
            first_line = f.readline()
            if first_line.startswith('0'):
                gate_open_files.append(label_file.name)
            elif first_line.startswith('1'):
                gate_closed_files.append(label_file.name)
    
    # Mezclar aleatoriamente
    random.seed(42)  # Para reproducibilidad
    random.shuffle(gate_open_files)
    random.shuffle(gate_closed_files)
    
    # Calcular split
    n_train_open = int(len(gate_open_files) * train_ratio)
    n_train_closed = int(len(gate_closed_files) * train_ratio)
    
    # Archivos para validación
    val_files = gate_open_files[n_train_open:] + gate_closed_files[n_train_closed:]
    
    # Mover archivos a validación
    moved = 0
    for txt_file in val_files:
        # Mover etiqueta
        shutil.move(train_labels / txt_file, val_labels / txt_file)
        
        # Mover imagen correspondiente
        base_name = Path(txt_file).stem
        for ext in ['.jpg', '.png', '.jpeg']:
            img_file = train_images / f"{base_name}{ext}"
            if img_file.exists():
                shutil.move(img_file, val_images / img_file.name)
                moved += 1
                break
    
    # Estadísticas finales
    train_open = n_train_open
    train_closed = n_train_closed
    val_open = len(gate_open_files) - n_train_open
    val_closed = len(gate_closed_files) - n_train_closed
    
    print("✅ División Train/Val completada:")
    print(f"\n📁 TRAIN ({int(train_ratio*100)}%):")
    print(f"   🚪 Puertas abiertas: {train_open}")
    print(f"   🔒 Puertas cerradas: {train_closed}")
    print(f"   📊 Total: {train_open + train_closed}")
    print(f"\n📁 VAL ({int((1-train_ratio)*100)}%):")
    print(f"   🚪 Puertas abiertas: {val_open}")
    print(f"   🔒 Puertas cerradas: {val_closed}")
    print(f"   📊 Total: {val_open + val_closed}")

if __name__ == "__main__":
    create_train_val_split()
