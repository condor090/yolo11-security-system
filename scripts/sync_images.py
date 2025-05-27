#!/usr/bin/env python3
"""
Script para sincronizar imágenes con etiquetas
Solo copia las imágenes que tienen archivo .txt correspondiente
"""

import os
import shutil
from pathlib import Path

def sync_images_with_labels():
    # Directorios
    source_images = Path("/Users/Shared/yolo11_project/data/telegram_photos")
    labels_dir = Path("/Users/Shared/yolo11_project/data/train/labels")
    train_images = Path("/Users/Shared/yolo11_project/data/train/images")
    
    # Crear directorio de imágenes si no existe
    train_images.mkdir(parents=True, exist_ok=True)
    
    # Obtener lista de etiquetas (sin classes.txt)
    label_files = [f for f in labels_dir.glob("*.txt") if f.name != "classes.txt"]
    
    print(f"📊 Encontradas {len(label_files)} etiquetas")
    
    # Estadísticas
    copied = 0
    gate_open = 0
    gate_closed = 0
    
    # Sincronizar imágenes
    for label_file in label_files:
        # Nombre base sin extensión
        base_name = label_file.stem
        
        # Buscar imagen correspondiente (jpg o png)
        for ext in ['.jpg', '.png', '.jpeg']:
            image_path = source_images / f"{base_name}{ext}"
            if image_path.exists():
                # Copiar imagen
                dest_path = train_images / image_path.name
                shutil.copy2(image_path, dest_path)
                copied += 1
                
                # Contar clases
                with open(label_file, 'r') as f:
                    first_line = f.readline()
                    if first_line.startswith('0'):
                        gate_open += 1
                    elif first_line.startswith('1'):
                        gate_closed += 1
                
                break
    
    print(f"\n✅ Sincronización completada:")
    print(f"📁 Imágenes copiadas: {copied}")
    print(f"🚪 Puertas abiertas: {gate_open}")
    print(f"🔒 Puertas cerradas: {gate_closed}")
    print(f"📊 Balance: {gate_open/gate_closed:.2f}:1")
    
    return copied

if __name__ == "__main__":
    sync_images_with_labels()
