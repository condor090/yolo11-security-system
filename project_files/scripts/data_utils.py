#!/usr/bin/env python3
"""
Utilidades para el preprocesamiento de datos del sistema de seguridad
Incluye funciones para conversión de formatos, augmentation y análisis de datasets
"""

import cv2
import numpy as np
import os
import json
import yaml
from pathlib import Path
import argparse
import logging
from typing import List, Tuple, Dict
from tqdm import tqdm
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetProcessor:
    """Procesador de datasets para el sistema de seguridad"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Cargar configuración"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def convert_coco_to_yolo(self, coco_json_path: str, images_dir: str, output_dir: str):
        """
        Convertir anotaciones COCO a formato YOLO
        
        Args:
            coco_json_path: Ruta al archivo JSON de COCO
            images_dir: Directorio con imágenes
            output_dir: Directorio de salida para labels YOLO
        """
        logger.info(f"Convirtiendo COCO a YOLO: {coco_json_path}")
        
        with open(coco_json_path, 'r') as f:
            coco_data = json.load(f)
        
        # Mapear categorías COCO a nuestras clases
        category_mapping = self._create_category_mapping(coco_data['categories'])
        
        # Crear directorio de salida
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Procesar imágenes y anotaciones
        image_info = {img['id']: img for img in coco_data['images']}
        
        for annotation in tqdm(coco_data['annotations'], desc="Procesando anotaciones"):
            image_id = annotation['image_id']
            image_info_item = image_info[image_id]
            
            # Obtener dimensiones de la imagen
            img_width = image_info_item['width']
            img_height = image_info_item['height']
            img_filename = image_info_item['file_name']
            
            # Convertir bbox de COCO a YOLO
            bbox = annotation['bbox']  # [x, y, width, height]
            yolo_bbox = self._coco_to_yolo_bbox(bbox, img_width, img_height)
            
            # Mapear categoría
            category_id = annotation['category_id']
            yolo_class = category_mapping.get(category_id, 0)
            
            # Crear archivo de anotación YOLO
            label_filename = Path(img_filename).stem + '.txt'
            label_path = output_path / label_filename
            
            # Escribir anotación
            with open(label_path, 'a') as f:
                f.write(f"{yolo_class} {' '.join(map(str, yolo_bbox))}\n")
        
        logger.info(f"Conversión completada. Labels guardados en: {output_dir}")
    
    def _coco_to_yolo_bbox(self, coco_bbox: List, img_width: int, img_height: int) -> List[float]:
        """Convertir bbox de COCO a formato YOLO"""
        x, y, width, height = coco_bbox
        
        # Calcular centro y normalizar
        center_x = (x + width / 2) / img_width
        center_y = (y + height / 2) / img_height
        norm_width = width / img_width
        norm_height = height / img_height
        
        return [center_x, center_y, norm_width, norm_height]
    
    def _create_category_mapping(self, coco_categories: List[Dict]) -> Dict[int, int]:
        """Crear mapeo de categorías COCO a clases YOLO"""
        # Mapeo personalizado - ajustar según necesidades
        mapping = {}
        class_names = list(self.config['names'].values())
        
        for category in coco_categories:
            coco_name = category['name'].lower()
            coco_id = category['id']
            
            # Mapear a nuestras clases
            if 'gate' in coco_name or 'door' in coco_name:
                if 'open' in coco_name:
                    mapping[coco_id] = 0  # gate_open
                else:
                    mapping[coco_id] = 1  # gate_closed
            elif 'person' in coco_name:
                mapping[coco_id] = 2  # authorized_person (por defecto)
            elif 'truck' in coco_name:
                mapping[coco_id] = 4  # truck
            elif 'car' in coco_name:
                mapping[coco_id] = 5  # car
            elif 'motorcycle' in coco_name or 'bike' in coco_name:
                mapping[coco_id] = 6  # motorcycle
        
        return mapping
    
    def split_dataset(self, images_dir: str, labels_dir: str, 
                     train_ratio: float = 0.8, val_ratio: float = 0.15):
        """
        Dividir dataset en train/val/test
        
        Args:
            images_dir: Directorio con imágenes
            labels_dir: Directorio con labels
            train_ratio: Proporción para entrenamiento
            val_ratio: Proporción para validación
        """
        logger.info("Dividiendo dataset...")
        
        images_path = Path(images_dir)
        labels_path = Path(labels_dir)
        
        # Obtener lista de archivos
        image_files = list(images_path.glob('*.jpg')) + list(images_path.glob('*.png'))
        
        # Verificar que existen labels correspondientes
        valid_files = []
        for img_file in image_files:
            label_file = labels_path / (img_file.stem + '.txt')
            if label_file.exists():
                valid_files.append(img_file.stem)
        
        logger.info(f"Archivos válidos encontrados: {len(valid_files)}")
        
        # Mezclar archivos
        np.random.shuffle(valid_files)
        
        # Calcular splits
        total_files = len(valid_files)
        train_count = int(total_files * train_ratio)
        val_count = int(total_files * val_ratio)
        
        train_files = valid_files[:train_count]
        val_files = valid_files[train_count:train_count + val_count]
        test_files = valid_files[train_count + val_count:]
        
        logger.info(f"Train: {len(train_files)}, Val: {len(val_files)}, Test: {len(test_files)}")
        
        # Crear directorios de destino
        splits = {
            'train': train_files,
            'val': val_files,
            'test': test_files
        }
        
        for split_name, file_list in splits.items():
            if not file_list:
                continue
                
            # Crear directorios
            split_images_dir = Path(f'data/{split_name}/images')
            split_labels_dir = Path(f'data/{split_name}/labels')
            split_images_dir.mkdir(parents=True, exist_ok=True)
            split_labels_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivos
            for filename in tqdm(file_list, desc=f"Copiando {split_name}"):
                # Buscar imagen con diferentes extensiones
                img_src = None
                for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    potential_img = images_path / (filename + ext)
                    if potential_img.exists():
                        img_src = potential_img
                        break
                
                if img_src:
                    img_dst = split_images_dir / img_src.name
                    shutil.copy2(img_src, img_dst)
                
                # Copiar label
                label_src = labels_path / (filename + '.txt')
                if label_src.exists():
                    label_dst = split_labels_dir / label_src.name
                    shutil.copy2(label_src, label_dst)
        
        logger.info("División del dataset completada")
    
    def analyze_dataset(self, dataset_dir: str) -> Dict:
        """Analizar estadísticas del dataset"""
        logger.info(f"Analizando dataset: {dataset_dir}")
        
        dataset_path = Path(dataset_dir)
        stats = {
            'total_images': 0,
            'total_annotations': 0,
            'class_distribution': {},
            'image_sizes': [],
            'bbox_sizes': []
        }
        
        # Inicializar contadores de clases
        for class_id, class_name in self.config['names'].items():
            stats['class_distribution'][class_name] = 0
        
        # Procesar cada split
        for split in ['train', 'val', 'test']:
            images_dir = dataset_path / split / 'images'
            labels_dir = dataset_path / split / 'labels'
            
            if not images_dir.exists():
                continue
            
            logger.info(f"Analizando split: {split}")
            
            for image_file in tqdm(list(images_dir.glob('*'))):
                if image_file.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.bmp']:
                    continue
                
                stats['total_images'] += 1
                
                # Obtener dimensiones de imagen
                img = cv2.imread(str(image_file))
                if img is not None:
                    h, w = img.shape[:2]
                    stats['image_sizes'].append((w, h))
                
                # Procesar labels
                label_file = labels_dir / (image_file.stem + '.txt')
                if label_file.exists():
                    with open(label_file, 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                class_id = int(parts[0])
                                class_name = self.config['names'].get(class_id, f'class_{class_id}')
                                stats['class_distribution'][class_name] += 1
                                stats['total_annotations'] += 1
                                
                                # Tamaño de bbox
                                width, height = float(parts[3]), float(parts[4])
                                stats['bbox_sizes'].append((width, height))
        
        # Calcular estadísticas adicionales
        if stats['image_sizes']:
            widths, heights = zip(*stats['image_sizes'])
            stats['avg_image_size'] = (np.mean(widths), np.mean(heights))
        
        if stats['bbox_sizes']:
            bbox_widths, bbox_heights = zip(*stats['bbox_sizes'])
            stats['avg_bbox_size'] = (np.mean(bbox_widths), np.mean(bbox_heights))
        
        return stats
    
    def visualize_annotations(self, images_dir: str, labels_dir: str, 
                            output_dir: str, num_samples: int = 10):
        """Visualizar muestras del dataset con anotaciones"""
        logger.info("Creando visualizaciones del dataset...")
        
        images_path = Path(images_dir)
        labels_path = Path(labels_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Colores para cada clase
        colors = [
            (0, 255, 0),    # gate_open - Verde
            (0, 0, 255),    # gate_closed - Rojo
            (255, 255, 0),  # authorized_person - Cian
            (0, 0, 255),    # unauthorized_person - Rojo
            (255, 0, 255),  # truck - Magenta
            (0, 255, 255),  # car - Amarillo
            (128, 0, 128)   # motorcycle - Púrpura
        ]
        
        # Seleccionar muestras aleatorias
        image_files = list(images_path.glob('*.jpg')) + list(images_path.glob('*.png'))
        samples = np.random.choice(image_files, min(num_samples, len(image_files)), replace=False)
        
        for i, image_file in enumerate(samples):
            img = cv2.imread(str(image_file))
            if img is None:
                continue
            
            h, w = img.shape[:2]
            
            # Cargar anotaciones
            label_file = labels_path / (image_file.stem + '.txt')
            if label_file.exists():
                with open(label_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            center_x, center_y, width, height = map(float, parts[1:5])
                            
                            # Convertir a coordenadas de píxeles
                            x1 = int((center_x - width/2) * w)
                            y1 = int((center_y - height/2) * h)
                            x2 = int((center_x + width/2) * w)
                            y2 = int((center_y + height/2) * h)
                            
                            # Dibujar bbox
                            color = colors[class_id % len(colors)]
                            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                            
                            # Etiqueta
                            class_name = self.config['names'].get(class_id, f'class_{class_id}')
                            cv2.putText(img, class_name, (x1, y1-10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Guardar imagen visualizada
            output_file = output_path / f'sample_{i:03d}_{image_file.name}'
            cv2.imwrite(str(output_file), img)
        
        logger.info(f"Visualizaciones guardadas en: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Utilidades de procesamiento de datos')
    parser.add_argument('--config', type=str, 
                       default='configs/security_dataset.yaml',
                       help='Archivo de configuración')
    parser.add_argument('--action', type=str, required=True,
                       choices=['convert_coco', 'split_dataset', 'analyze', 'visualize'],
                       help='Acción a realizar')
    parser.add_argument('--input-dir', type=str, help='Directorio de entrada')
    parser.add_argument('--output-dir', type=str, help='Directorio de salida')
    parser.add_argument('--coco-json', type=str, help='Archivo JSON de COCO')
    parser.add_argument('--images-dir', type=str, help='Directorio de imágenes')
    parser.add_argument('--labels-dir', type=str, help='Directorio de labels')
    
    args = parser.parse_args()
    
    processor = DatasetProcessor(args.config)
    
    if args.action == 'convert_coco':
        if not all([args.coco_json, args.images_dir, args.output_dir]):
            parser.error("convert_coco requiere --coco-json, --images-dir, --output-dir")
        processor.convert_coco_to_yolo(args.coco_json, args.images_dir, args.output_dir)
    
    elif args.action == 'split_dataset':
        if not all([args.images_dir, args.labels_dir]):
            parser.error("split_dataset requiere --images-dir, --labels-dir")
        processor.split_dataset(args.images_dir, args.labels_dir)
    
    elif args.action == 'analyze':
        if not args.input_dir:
            parser.error("analyze requiere --input-dir")
        stats = processor.analyze_dataset(args.input_dir)
        
        print("\n=== ESTADÍSTICAS DEL DATASET ===")
        print(f"Total de imágenes: {stats['total_images']}")
        print(f"Total de anotaciones: {stats['total_annotations']}")
        print(f"Promedio de anotaciones por imagen: {stats['total_annotations']/stats['total_images']:.2f}")
        
        if 'avg_image_size' in stats:
            print(f"Tamaño promedio de imagen: {stats['avg_image_size'][0]:.0f}x{stats['avg_image_size'][1]:.0f}")
        
        print("\nDistribución de clases:")
        for class_name, count in stats['class_distribution'].items():
            percentage = (count / stats['total_annotations']) * 100 if stats['total_annotations'] > 0 else 0
            print(f"  {class_name}: {count} ({percentage:.1f}%)")
    
    elif args.action == 'visualize':
        if not all([args.images_dir, args.labels_dir, args.output_dir]):
            parser.error("visualize requiere --images-dir, --labels-dir, --output-dir")
        processor.visualize_annotations(args.images_dir, args.labels_dir, args.output_dir)

if __name__ == "__main__":
    main()
