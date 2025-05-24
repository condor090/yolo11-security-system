#!/usr/bin/env python3
"""
Script de Augmentación de Datos para YOLO11
Multiplica tu dataset automáticamente
"""

import cv2
import numpy as np
import os
from pathlib import Path
import albumentations as A

# Configurar transformaciones
transform = A.Compose([
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
    A.RandomGamma(gamma_limit=(80, 120), p=0.5),
    A.RandomRain(p=0.3),  # Simular lluvia
    A.RandomFog(p=0.3),   # Simular neblina
    A.RandomShadow(p=0.3), # Agregar sombras
    A.GaussNoise(p=0.2),   # Ruido
    A.Blur(blur_limit=3, p=0.1),
    A.CLAHE(p=0.3),  # Mejorar contraste
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

def augment_dataset(input_dir, output_dir, augmentation_factor=3):
    """
    Aumenta el dataset por el factor especificado
    
    Args:
        input_dir: Directorio con imágenes originales
        output_dir: Directorio de salida
        augmentation_factor: Cuántas versiones crear por imagen
    """
    os.makedirs(output_dir, exist_ok=True)
    
    image_files = list(Path(input_dir).glob('*.jpg'))
    print(f"📸 Encontradas {len(image_files)} imágenes originales")
    
    total_generated = 0
    
    for img_path in image_files:
        # Leer imagen
        image = cv2.imread(str(img_path))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Leer anotaciones YOLO si existen
        label_path = img_path.with_suffix('.txt')
        bboxes = []
        class_labels = []
        
        if label_path.exists():
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_labels.append(int(parts[0]))
                        bboxes.append([float(x) for x in parts[1:]])
        
        # Guardar original
        base_name = img_path.stem
        cv2.imwrite(f"{output_dir}/{base_name}_original.jpg", image)
        
        # Generar augmentaciones
        for i in range(augmentation_factor):
            # Aplicar transformaciones
            transformed = transform(
                image=image_rgb,
                bboxes=bboxes,
                class_labels=class_labels
            )
            
            # Guardar imagen aumentada
            aug_image = cv2.cvtColor(transformed['image'], cv2.COLOR_RGB2BGR)
            aug_filename = f"{output_dir}/{base_name}_aug_{i+1}.jpg"
            cv2.imwrite(aug_filename, aug_image)
            
            # Guardar anotaciones si existen
            if transformed['bboxes']:
                label_filename = f"{output_dir}/{base_name}_aug_{i+1}.txt"
                with open(label_filename, 'w') as f:
                    for bbox, cls in zip(transformed['bboxes'], transformed['class_labels']):
                        f.write(f"{cls} {' '.join(map(str, bbox))}\n")
            
            total_generated += 1
    
    print(f"✅ Generadas {total_generated} imágenes aumentadas")
    print(f"📊 Dataset total: {len(image_files) + total_generated} imágenes")

if __name__ == "__main__":
    # Ejemplo de uso
    augment_dataset(
        input_dir="data/train/images",
        output_dir="data/train_augmented/images",
        augmentation_factor=3
    )
