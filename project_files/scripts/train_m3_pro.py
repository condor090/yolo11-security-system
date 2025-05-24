#!/usr/bin/env python3
"""
Script de entrenamiento optimizado para Apple M3 Pro
Específico para dataset pequeño de detección de rejas (60 imágenes)
"""

import os
import torch
import logging
from pathlib import Path
from ultralytics import YOLO

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_m3_pro_training():
    """Configuración específica para M3 Pro"""
    
    # Verificar disponibilidad de MPS (Metal Performance Shaders)
    if torch.backends.mps.is_available():
        device = "mps"
        logger.info("✅ Usando GPU M3 Pro con Metal Performance Shaders")
    else:
        device = "cpu"
        logger.warning("⚠️ GPU no disponible, usando CPU")
    
    # Configurar variables de entorno para M3 Pro
    os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'  # Usar toda la GPU
    
    return device

def train_gate_detection_m3():
    """Entrenar modelo específico para rejas en M3 Pro"""
    
    logger.info("🚀 Iniciando entrenamiento optimizado para M3 Pro")
    
    # Configurar dispositivo
    device = setup_m3_pro_training()
    
    # Usar modelo más ligero para dataset pequeño
    model = YOLO('yolo11s.pt')  # YOLOv11 Small - perfecto para 60 imágenes
    logger.info("📦 Modelo YOLO11s cargado (optimizado para datasets pequeños)")
    
    # Configuración de entrenamiento optimizada
    train_args = {
        'data': '/security_project/configs/gate_detection_m3.yaml',
        'epochs': 150,
        'batch': 12,                    # Óptimo para 18GB RAM
        'imgsz': 640,
        'device': device,
        'project': 'runs/gate_detection',
        'name': 'gates_m3_pro',
        'save': True,
        'save_period': 10,              # Guardar cada 10 épocas
        'cache': True,                  # Cache en RAM
        'workers': 6,                   # 6 de 11 cores
        'patience': 30,                 # Early stopping más agresivo
        'resume': False,
        'amp': True,                    # Mixed precision
        'fraction': 1.0,                # Usar todo el dataset
        'profile': False,
        'freeze': None,
        'multi_scale': False,           # Desactivar para mayor estabilidad
        'overlap_mask': True,
        'mask_ratio': 4,
        'dropout': 0.0,
        'val': True,
        'split': 'val',
        'save_json': True,
        'plots': True,
        'lr0': 0.01,                    # Learning rate
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'box': 7.5,                     # Box loss gain
        'cls': 0.5,                     # Class loss gain
        'conf': None,
        'iou': 0.6,
        'max_det': 100,                 # Máximo detecciones por imagen
        'half': False,                  # No usar half precision con MPS
        'dnn': False,
        'augment': True,
        'agnostic_nms': False,
        'classes': None,
        'retina_masks': False,
        'close_mosaic': 10,             # Cerrar mosaic en últimas 10 épocas
        
        # Data augmentation optimizado para rejas
        'hsv_h': 0.01,
        'hsv_s': 0.5,
        'hsv_v': 0.3,
        'degrees': 5.0,
        'translate': 0.05,
        'scale': 0.3,
        'fliplr': 0.0,                  # No flip horizontal
        'flipud': 0.0,                  # No flip vertical
        'mosaic': 0.8,
        'mixup': 0.0,
        'copy_paste': 0.0
    }
    
    logger.info("⚙️ Configuración de entrenamiento:")
    logger.info(f"   📊 Batch size: {train_args['batch']}")
    logger.info(f"   🔄 Épocas: {train_args['epochs']}")
    logger.info(f"   📱 Dispositivo: {device}")
    logger.info(f"   🖥️ Workers: {train_args['workers']}")
    logger.info(f"   💾 Cache activado: {train_args['cache']}")
    
    try:
        # Entrenar modelo
        logger.info("🎯 Iniciando entrenamiento...")
        results = model.train(**train_args)
        
        logger.info("✅ ¡Entrenamiento completado!")
        logger.info(f"📁 Resultados guardados en: {results.save_dir}")
        
        # Validar modelo final
        logger.info("🧪 Validando modelo entrenado...")
        metrics = model.val()
        
        logger.info("📈 Métricas finales:")
        if hasattr(metrics, 'box'):
            logger.info(f"   📦 mAP50: {metrics.box.map50:.4f}")
            logger.info(f"   📦 mAP50-95: {metrics.box.map:.4f}")
        
        # Exportar modelo optimizado
        logger.info("📤 Exportando modelo final...")
        
        # Guardar modelo en formato optimizado para M3
        best_model_path = Path(results.save_dir) / 'weights' / 'best.pt'
        if best_model_path.exists():
            final_model_path = '/security_project/models/gate_detector_m3.pt'
            import shutil
            shutil.copy2(best_model_path, final_model_path)
            logger.info(f"✅ Modelo final guardado: {final_model_path}")
        
        # Exportar a otros formatos para producción
        try:
            model.export(format='onnx', imgsz=640)
            logger.info("✅ Modelo exportado a ONNX")
        except Exception as e:
            logger.warning(f"⚠️ Error exportando ONNX: {e}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error durante entrenamiento: {e}")
        raise
    
    finally:
        # Limpiar memoria
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        logger.info("🧹 Memoria GPU limpiada")

def estimate_training_time():
    """Estimar tiempo de entrenamiento para M3 Pro"""
    logger.info("⏱️ Estimación de tiempo para M3 Pro:")
    logger.info("   📊 Dataset: 60 imágenes")
    logger.info("   🔄 Épocas: 150")
    logger.info("   📱 Modelo: YOLO11s")
    logger.info("   ⏰ Tiempo estimado: 30-60 minutos")
    logger.info("   💾 Memoria GPU: ~2-4 GB")
    logger.info("   🔋 Uso de CPU: Moderado")

if __name__ == "__main__":
    print("🍎 YOLO11 - Entrenamiento Optimizado para Apple M3 Pro")
    print("=" * 60)
    
    estimate_training_time()
    
    # Verificar estructura de datos
    data_path = Path('/security_project/data')
    if not data_path.exists():
        print("❌ Error: Directorio de datos no encontrado")
        print("   Ejecuta primero: ./deploy.sh setup")
        exit(1)
    
    # Crear directorio de configuración si no existe
    config_dir = Path('/security_project/configs')
    config_dir.mkdir(exist_ok=True)
    
    # Copiar configuración optimizada
    import shutil
    source_config = '/security_project/project_files/configs/gate_detection_m3.yaml'
    target_config = '/security_project/configs/gate_detection_m3.yaml'
    if Path(source_config).exists():
        shutil.copy2(source_config, target_config)
        print(f"✅ Configuración copiada: {target_config}")
    
    # Ejecutar entrenamiento
    results = train_gate_detection_m3()
    
    print("\n🎉 ¡Entrenamiento completado en M3 Pro!")
    print("📁 Revisa los resultados en: runs/gate_detection/gates_m3_pro/")
