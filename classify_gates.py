#!/usr/bin/env python3
"""
Clasificador Inteligente de Puertas Abiertas/Cerradas
Analiza 32,487 fotos y las organiza automáticamente
"""

import os
import cv2
import numpy as np
from datetime import datetime
import json
from tqdm import tqdm
import shutil
from collections import defaultdict
import random

# Configuración
SOURCE_DIR = '/Users/Shared/yolo11_project/data/telegram_photos'
OUTPUT_DIR = '/Users/Shared/yolo11_project/data/classified'
ANALYSIS_RESULTS = '/Users/Shared/yolo11_project/data/analysis_results.json'

class GateClassifier:
    """Clasificador de puertas basado en características visuales"""
    
    def __init__(self):
        self.stats = {
            'total_processed': 0,
            'gates_open': 0,
            'gates_closed': 0,
            'uncertain': 0,
            'errors': 0,
            'by_hour': defaultdict(lambda: {'open': 0, 'closed': 0, 'uncertain': 0})
        }
        
        # Crear directorios
        os.makedirs(f"{OUTPUT_DIR}/gates_open", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/gates_closed", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/uncertain", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/selected_1000_open", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/selected_1000_closed", exist_ok=True)
    
    def analyze_gate_state(self, image_path):
        """
        Analiza si la puerta está abierta o cerrada
        Retorna: 'open', 'closed', o 'uncertain'
        """
        try:
            # Leer imagen
            img = cv2.imread(image_path)
            if img is None:
                return 'error'
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Región de interés (centro de la imagen donde suele estar la puerta)
            h, w = gray.shape
            roi = gray[int(h*0.3):int(h*0.8), int(w*0.2):int(w*0.8)]
            
            # Detectar líneas verticales (barras de la reja)
            edges = cv2.Canny(roi, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                   minLineLength=30, maxLineGap=10)
            
            if lines is None:
                return 'uncertain'
            
            # Analizar patrones
            vertical_lines = 0
            horizontal_lines = 0
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                
                if 80 <= angle <= 100:  # Líneas verticales
                    vertical_lines += 1
                elif angle <= 10 or angle >= 170:  # Líneas horizontales
                    horizontal_lines += 1
            
            # Analizar brillo en el centro (puertas abiertas suelen mostrar el fondo)
            center_roi = roi[int(roi.shape[0]*0.4):int(roi.shape[0]*0.6),
                            int(roi.shape[1]*0.4):int(roi.shape[1]*0.6)]
            avg_brightness = np.mean(center_roi)
            
            # Detección de movimiento/personas
            # Las puertas abiertas suelen tener más variación
            variance = np.var(roi)
            
            # Lógica de clasificación
            # Puerta cerrada: muchas líneas verticales, poco brillo central, poca variación
            # Puerta abierta: menos líneas verticales, más brillo, más variación
            
            score_open = 0
            score_closed = 0
            
            # Líneas verticales (más = cerrada)
            if vertical_lines > 5:
                score_closed += 2
            else:
                score_open += 1
            
            # Brillo central (más = abierta)
            if avg_brightness > 100:
                score_open += 2
            else:
                score_closed += 1
            
            # Variación (más = abierta, puede haber personas/vehículos)
            if variance > 1000:
                score_open += 1
            
            # Decisión
            if score_open > score_closed:
                return 'open'
            elif score_closed > score_open:
                return 'closed'
            else:
                return 'uncertain'
                
        except Exception as e:
            print(f"Error analizando {image_path}: {e}")
            return 'error'
    
    def extract_timestamp(self, filename):
        """Extrae la hora del nombre del archivo"""
        try:
            # Formato: puerta_YYYYMMDD_HHMMSS_ID.jpg
            parts = filename.split('_')
            if len(parts) >= 3:
                time_str = parts[2]
                hour = int(time_str[:2])
                return hour
        except:
            pass
        return -1
    
    def process_all_images(self):
        """Procesa todas las imágenes del directorio"""
        
        # Obtener lista de imágenes
        images = [f for f in os.listdir(SOURCE_DIR) 
                 if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"📸 Total de imágenes a procesar: {len(images)}")
        
        # Clasificar por tipo
        classified = {
            'open': [],
            'closed': [],
            'uncertain': []
        }
        
        # Procesar con barra de progreso
        with tqdm(total=len(images), desc="Clasificando imágenes") as pbar:
            for image_file in images:
                image_path = os.path.join(SOURCE_DIR, image_file)
                
                # Clasificar
                state = self.analyze_gate_state(image_path)
                
                # Actualizar estadísticas
                self.stats['total_processed'] += 1
                
                if state == 'open':
                    self.stats['gates_open'] += 1
                    classified['open'].append(image_path)
                elif state == 'closed':
                    self.stats['gates_closed'] += 1
                    classified['closed'].append(image_path)
                elif state == 'uncertain':
                    self.stats['uncertain'] += 1
                    classified['uncertain'].append(image_path)
                else:  # error
                    self.stats['errors'] += 1
                
                # Estadísticas por hora
                hour = self.extract_timestamp(image_file)
                if hour >= 0 and state in ['open', 'closed', 'uncertain']:
                    self.stats['by_hour'][hour][state] += 1
                
                pbar.update(1)
                
                # Mostrar progreso cada 1000 imágenes
                if self.stats['total_processed'] % 1000 == 0:
                    pbar.set_postfix({
                        'Abiertas': self.stats['gates_open'],
                        'Cerradas': self.stats['gates_closed'],
                        'Inciertas': self.stats['uncertain']
                    })
        
        return classified
    
    def select_best_1000(self, classified):
        """Selecciona las mejores 1000 de cada tipo"""
        
        print("\n🎯 Seleccionando las mejores 1000 de cada tipo...")
        
        # Para puertas abiertas
        if len(classified['open']) >= 1000:
            # Estrategia: distribuir por hora del día
            open_by_hour = defaultdict(list)
            
            for img_path in classified['open']:
                filename = os.path.basename(img_path)
                hour = self.extract_timestamp(filename)
                if hour >= 0:
                    open_by_hour[hour].append(img_path)
                else:
                    open_by_hour[12].append(img_path)  # Default mediodía
            
            # Seleccionar proporcionalmente de cada hora
            selected_open = []
            photos_per_hour = 1000 // 24  # ~41 por hora
            
            for hour in range(24):
                hour_photos = open_by_hour[hour]
                if hour_photos:
                    n_select = min(len(hour_photos), photos_per_hour)
                    selected_open.extend(random.sample(hour_photos, n_select))
            
            # Completar si faltan
            if len(selected_open) < 1000:
                remaining = list(set(classified['open']) - set(selected_open))
                need = 1000 - len(selected_open)
                selected_open.extend(random.sample(remaining, min(need, len(remaining))))
            
            # Limitar a 1000
            selected_open = selected_open[:1000]
            
            # Copiar archivos
            print(f"📁 Copiando {len(selected_open)} puertas abiertas seleccionadas...")
            for i, src in enumerate(tqdm(selected_open, desc="Copiando abiertas")):
                dst = os.path.join(OUTPUT_DIR, 'selected_1000_open', 
                                 f"open_{i:04d}_{os.path.basename(src)}")
                shutil.copy2(src, dst)
        else:
            print(f"⚠️  Solo hay {len(classified['open'])} puertas abiertas (necesita 1000)")
        
        # Para puertas cerradas
        if len(classified['closed']) >= 1000:
            # Misma estrategia
            closed_by_hour = defaultdict(list)
            
            for img_path in classified['closed']:
                filename = os.path.basename(img_path)
                hour = self.extract_timestamp(filename)
                if hour >= 0:
                    closed_by_hour[hour].append(img_path)
                else:
                    closed_by_hour[12].append(img_path)
            
            selected_closed = []
            photos_per_hour = 1000 // 24
            
            for hour in range(24):
                hour_photos = closed_by_hour[hour]
                if hour_photos:
                    n_select = min(len(hour_photos), photos_per_hour)
                    selected_closed.extend(random.sample(hour_photos, n_select))
            
            # Completar si faltan
            if len(selected_closed) < 1000:
                remaining = list(set(classified['closed']) - set(selected_closed))
                need = 1000 - len(selected_closed)
                selected_closed.extend(random.sample(remaining, min(need, len(remaining))))
            
            # Limitar a 1000
            selected_closed = selected_closed[:1000]
            
            # Copiar archivos
            print(f"📁 Copiando {len(selected_closed)} puertas cerradas seleccionadas...")
            for i, src in enumerate(tqdm(selected_closed, desc="Copiando cerradas")):
                dst = os.path.join(OUTPUT_DIR, 'selected_1000_closed', 
                                 f"closed_{i:04d}_{os.path.basename(src)}")
                shutil.copy2(src, dst)
        else:
            print(f"⚠️  Solo hay {len(classified['closed'])} puertas cerradas (necesita 1000)")
        
        return len(selected_open) if 'selected_open' in locals() else 0, \
               len(selected_closed) if 'selected_closed' in locals() else 0
    
    def save_results(self):
        """Guarda los resultados del análisis"""
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'statistics': dict(self.stats),
            'hourly_distribution': dict(self.stats['by_hour']),
            'directories': {
                'source': SOURCE_DIR,
                'output': OUTPUT_DIR,
                'selected_open': f"{OUTPUT_DIR}/selected_1000_open",
                'selected_closed': f"{OUTPUT_DIR}/selected_1000_closed"
            }
        }
        
        with open(ANALYSIS_RESULTS, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Resultados guardados en: {ANALYSIS_RESULTS}")
    
    def print_summary(self):
        """Imprime resumen del análisis"""
        
        print("\n" + "="*60)
        print("📊 RESUMEN DEL ANÁLISIS")
        print("="*60)
        print(f"Total procesadas: {self.stats['total_processed']:,}")
        print(f"Puertas ABIERTAS: {self.stats['gates_open']:,} ({self.stats['gates_open']/self.stats['total_processed']*100:.1f}%)")
        print(f"Puertas CERRADAS: {self.stats['gates_closed']:,} ({self.stats['gates_closed']/self.stats['total_processed']*100:.1f}%)")
        print(f"Inciertas: {self.stats['uncertain']:,} ({self.stats['uncertain']/self.stats['total_processed']*100:.1f}%)")
        print(f"Errores: {self.stats['errors']:,}")
        print("="*60)
        
        # Distribución por hora
        print("\n📈 Distribución por hora del día:")
        for hour in sorted(self.stats['by_hour'].keys()):
            hour_stats = self.stats['by_hour'][hour]
            total_hour = sum(hour_stats.values())
            if total_hour > 0:
                bar = "█" * (total_hour // 100)
                print(f"{hour:02d}:00 - {bar} ({total_hour}) "
                      f"[A:{hour_stats['open']} C:{hour_stats['closed']}]")

def main():
    """Función principal"""
    print("🤖 Clasificador Inteligente de Puertas")
    print("="*60)
    
    classifier = GateClassifier()
    
    # Procesar todas las imágenes
    classified = classifier.process_all_images()
    
    # Seleccionar las mejores 1000 de cada tipo
    n_open, n_closed = classifier.select_best_1000(classified)
    
    # Guardar resultados
    classifier.save_results()
    
    # Mostrar resumen
    classifier.print_summary()
    
    print(f"\n✅ Proceso completado!")
    print(f"📁 Imágenes seleccionadas en: {OUTPUT_DIR}/selected_1000_open y selected_1000_closed")
    
    if n_open < 1000 or n_closed < 1000:
        print("\n⚠️  ATENCIÓN: No hay suficientes imágenes para completar 1000 de cada tipo")
        print("Considere ajustar las imágenes 'inciertas' manualmente")

if __name__ == '__main__':
    main()
