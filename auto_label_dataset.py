#!/usr/bin/env python3
"""
Auto-etiquetador para las 2000 imágenes seleccionadas
Genera archivos YOLO .txt automáticamente
"""

import os
import cv2
from pathlib import Path
import shutil
from tqdm import tqdm

# Configuración
SELECTED_OPEN = '/Users/Shared/yolo11_project/data/classified/selected_1000_open'
SELECTED_CLOSED = '/Users/Shared/yolo11_project/data/classified/selected_1000_closed'
OUTPUT_DIR = '/Users/Shared/yolo11_project/data/dataset_profesional'

# Mapeo de clases
CLASSES = {
    'gate_open': 0,
    'gate_closed': 1
}

def create_dataset_structure():
    """Crea la estructura del dataset profesional"""
    
    # Crear directorios
    for split in ['train', 'val', 'test']:
        os.makedirs(f"{OUTPUT_DIR}/{split}/images", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/{split}/labels", exist_ok=True)
    
    print("📁 Estructura del dataset creada")

def auto_label_image(image_path, class_id):
    """
    Genera etiqueta YOLO automática para la imagen
    Asume que la reja está en el centro de la imagen
    """
    
    # Leer imagen para obtener dimensiones
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    h, w = img.shape[:2]
    
    # Definir bounding box para la reja (región central)
    # Ajustado para cubrir típicamente donde está la reja
    x_center = 0.5  # Centro horizontal
    y_center = 0.5  # Centro vertical  
    bbox_width = 0.7  # 70% del ancho
    bbox_height = 0.6  # 60% de la altura
    
    # Formato YOLO: class x_center y_center width height
    label = f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}"
    
    return label

def process_images():
    """Procesa y etiqueta todas las imágenes"""
    
    # Contadores
    stats = {
        'train_open': 0, 'train_closed': 0,
        'val_open': 0, 'val_closed': 0,
        'test_open': 0, 'test_closed': 0
    }
    
    # Procesar puertas abiertas
    print("\n🚪 Procesando puertas ABIERTAS...")
    open_images = list(Path(SELECTED_OPEN).glob('*.jpg'))
    
    if open_images:
        # División 80/15/5
        n_train = int(len(open_images) * 0.8)
        n_val = int(len(open_images) * 0.15)
        
        train_open = open_images[:n_train]
        val_open = open_images[n_train:n_train+n_val]
        test_open = open_images[n_train+n_val:]
        
        # Procesar cada conjunto
        for images, split in [(train_open, 'train'), (val_open, 'val'), (test_open, 'test')]:
            for img_path in tqdm(images, desc=f"Etiquetando {split} (abiertas)"):
                # Generar nombre único
                new_name = f"gate_open_{split}_{len(os.listdir(f'{OUTPUT_DIR}/{split}/images')):05d}.jpg"
                
                # Copiar imagen
                dst_img = f"{OUTPUT_DIR}/{split}/images/{new_name}"
                shutil.copy2(str(img_path), dst_img)
                
                # Generar etiqueta
                label = auto_label_image(str(img_path), CLASSES['gate_open'])
                if label:
                    label_path = f"{OUTPUT_DIR}/{split}/labels/{new_name.replace('.jpg', '.txt')}"
                    with open(label_path, 'w') as f:
                        f.write(label)
                    
                    stats[f'{split}_open'] += 1
    
    # Procesar puertas cerradas
    print("\n🚪 Procesando puertas CERRADAS...")
    closed_images = list(Path(SELECTED_CLOSED).glob('*.jpg'))
    
    if closed_images:
        # División 80/15/5
        n_train = int(len(closed_images) * 0.8)
        n_val = int(len(closed_images) * 0.15)
        
        train_closed = closed_images[:n_train]
        val_closed = closed_images[n_train:n_train+n_val]
        test_closed = closed_images[n_train+n_val:]
        
        # Procesar cada conjunto
        for images, split in [(train_closed, 'train'), (val_closed, 'val'), (test_closed, 'test')]:
            for img_path in tqdm(images, desc=f"Etiquetando {split} (cerradas)"):
                # Generar nombre único
                new_name = f"gate_closed_{split}_{len(os.listdir(f'{OUTPUT_DIR}/{split}/images')):05d}.jpg"
                
                # Copiar imagen
                dst_img = f"{OUTPUT_DIR}/{split}/images/{new_name}"
                shutil.copy2(str(img_path), dst_img)
                
                # Generar etiqueta
                label = auto_label_image(str(img_path), CLASSES['gate_closed'])
                if label:
                    label_path = f"{OUTPUT_DIR}/{split}/labels/{new_name.replace('.jpg', '.txt')}"
                    with open(label_path, 'w') as f:
                        f.write(label)
                    
                    stats[f'{split}_closed'] += 1
    
    return stats

def create_yaml_config():
    """Crea archivo de configuración YAML para el entrenamiento"""
    
    yaml_content = f"""# Dataset Profesional YOLO11 Security System
# 2000 imágenes: 1000 puertas abiertas + 1000 puertas cerradas

path: {OUTPUT_DIR}  # Ruta del dataset
train: train/images
val: val/images
test: test/images

# Clases
nc: 2  # Número de clases
names:
  0: gate_open
  1: gate_closed

# Configuración de entrenamiento optimizada
train_config:
  epochs: 200
  batch_size: 16
  imgsz: 640
  patience: 50
  device: mps  # Para M3 Pro
  workers: 8
  cache: true
  
# Métricas objetivo
target_metrics:
  map50: 0.95
  map50_95: 0.90
  precision: 0.95
  recall: 0.93
"""
    
    with open(f"{OUTPUT_DIR}/dataset.yaml", 'w') as f:
        f.write(yaml_content)
    
    print(f"📝 Archivo de configuración creado: {OUTPUT_DIR}/dataset.yaml")

def print_summary(stats):
    """Imprime resumen del dataset"""
    
    print("\n" + "="*60)
    print("📊 DATASET PROFESIONAL CREADO")
    print("="*60)
    
    total_train = stats['train_open'] + stats['train_closed']
    total_val = stats['val_open'] + stats['val_closed']
    total_test = stats['test_open'] + stats['test_closed']
    total = total_train + total_val + total_test
    
    print(f"\n🏋️ TRAINING SET: {total_train} imágenes")
    print(f"   - Puertas abiertas: {stats['train_open']}")
    print(f"   - Puertas cerradas: {stats['train_closed']}")
    
    print(f"\n🎯 VALIDATION SET: {total_val} imágenes")
    print(f"   - Puertas abiertas: {stats['val_open']}")
    print(f"   - Puertas cerradas: {stats['val_closed']}")
    
    print(f"\n🧪 TEST SET: {total_test} imágenes")
    print(f"   - Puertas abiertas: {stats['test_open']}")
    print(f"   - Puertas cerradas: {stats['test_closed']}")
    
    print(f"\n📈 TOTAL: {total} imágenes etiquetadas")
    print("="*60)

def main():
    """Función principal"""
    
    print("🤖 Auto-Etiquetador YOLO para Dataset Profesional")
    print("="*60)
    
    # Crear estructura
    create_dataset_structure()
    
    # Procesar imágenes
    stats = process_images()
    
    # Crear configuración YAML
    create_yaml_config()
    
    # Mostrar resumen
    print_summary(stats)
    
    print(f"\n✅ Dataset profesional listo en: {OUTPUT_DIR}")
    print("\n🚀 Próximo paso: Entrenar el modelo con:")
    print(f"   python train_m3_pro.py --data {OUTPUT_DIR}/dataset.yaml")

if __name__ == '__main__':
    main()
