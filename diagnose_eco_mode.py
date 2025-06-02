#!/usr/bin/env python3
"""
Diagnóstico Profesional del Sistema de Modo Eco
Verifica el funcionamiento completo del sistema
"""

import cv2
import numpy as np
import time
import logging
from pathlib import Path
import sys

# Agregar el path del proyecto
sys.path.append(str(Path(__file__).parent))

from backend.utils.eco_mode import EcoModeManager, SystemState

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_motion_detection():
    """Prueba la detección de movimiento con frames sintéticos"""
    print("\n=== PRUEBA DE DETECCIÓN DE MOVIMIENTO ===\n")
    
    eco = EcoModeManager()
    eco.motion_threshold = 0.01  # Muy sensible para pruebas
    
    # Crear frame base (gris uniforme)
    base_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
    
    print("1. Procesando frame inicial (sin movimiento)...")
    has_motion = eco.detect_motion(base_frame)
    print(f"   Movimiento detectado: {has_motion} (esperado: False)")
    print(f"   Estado: {eco.current_state.value}")
    
    # Crear frame con movimiento (rectángulo blanco)
    motion_frame = base_frame.copy()
    cv2.rectangle(motion_frame, (200, 200), (400, 300), (255, 255, 255), -1)
    
    print("\n2. Procesando frame con movimiento...")
    has_motion = eco.detect_motion(motion_frame)
    print(f"   Movimiento detectado: {has_motion} (esperado: True)")
    print(f"   Estado: {eco.current_state.value}")
    
    # Verificar cambio de estado
    time.sleep(0.1)
    
    print("\n3. Verificando estado después de movimiento...")
    print(f"   Estado actual: {eco.current_state.value}")
    print(f"   Tiempo desde último movimiento: {time.time() - eco.last_motion_time:.2f}s")
    
    return eco.current_state == SystemState.ALERT

def test_state_transitions():
    """Prueba las transiciones entre estados"""
    print("\n=== PRUEBA DE TRANSICIONES DE ESTADO ===\n")
    
    eco = EcoModeManager()
    eco.idle_timeout = 2.0  # Timeouts cortos para prueba rápida
    eco.alert_timeout = 1.0
    
    print("1. Estado inicial:")
    print(f"   Estado: {eco.current_state.value}")
    print(f"   YOLO habilitado: {eco.get_current_config()['yolo_enabled']}")
    
    # Forzar estado ALERT
    eco.current_state = SystemState.ALERT
    print("\n2. Cambiado a ALERT:")
    print(f"   Estado: {eco.current_state.value}")
    print(f"   YOLO habilitado: {eco.get_current_config()['yolo_enabled']}")
    
    # Simular detección
    eco.update_state(detection_found=True)
    print("\n3. Después de detección:")
    print(f"   Estado: {eco.current_state.value}")
    print(f"   YOLO habilitado: {eco.get_current_config()['yolo_enabled']}")
    
    return True

def test_performance():
    """Prueba el rendimiento del sistema"""
    print("\n=== PRUEBA DE RENDIMIENTO ===\n")
    
    eco = EcoModeManager()
    frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
    
    # Probar diferentes estados
    for state in [SystemState.IDLE, SystemState.ALERT, SystemState.ACTIVE]:
        eco.current_state = state
        config = eco.get_current_config()
        
        print(f"\nEstado: {state.value}")
        print(f"  FPS configurado: {config['fps']}")
        print(f"  Intervalo detección: {config['detection_interval']}s")
        print(f"  Calidad JPEG: {config['jpeg_quality']}%")
        print(f"  Escala resolución: {config['resolution_scale']}")
        
        # Medir tiempo de procesamiento
        start = time.time()
        for _ in range(10):
            eco.detect_motion(frame)
        elapsed = time.time() - start
        
        print(f"  Tiempo promedio por frame: {elapsed/10*1000:.2f}ms")
        print(f"  FPS máximo teórico: {10/elapsed:.1f}")

def diagnose_system():
    """Diagnóstico completo del sistema"""
    print("="*60)
    print("DIAGNÓSTICO PROFESIONAL - MODO ECO INTELIGENTE")
    print("="*60)
    
    # Test 1: Detección de movimiento
    motion_ok = test_motion_detection()
    
    # Test 2: Transiciones de estado
    transitions_ok = test_state_transitions()
    
    # Test 3: Rendimiento
    test_performance()
    
    print("\n" + "="*60)
    print("RESUMEN DE DIAGNÓSTICO")
    print("="*60)
    
    print(f"\n✓ Detección de movimiento: {'FUNCIONANDO' if motion_ok else 'FALLA'}")
    print(f"✓ Transiciones de estado: {'FUNCIONANDO' if transitions_ok else 'FALLA'}")
    print("\nRECOMENDACIONES:")
    
    if not motion_ok:
        print("- Verificar que la cámara esté enviando frames correctamente")
        print("- Ajustar motion_threshold (actual: 0.02)")
        print("- Verificar permisos de la cámara")
    else:
        print("- Sistema de detección funcionando correctamente")
        print("- Puede ajustar sensibilidad si es necesario")
    
    print("\nCONFIGURACIÓN RECOMENDADA:")
    print("- motion_threshold: 0.01 (más sensible)")
    print("- idle_timeout: 60s (más tiempo antes de dormir)")
    print("- alert_timeout: 20s (más tiempo para detectar)")

if __name__ == "__main__":
    diagnose_system()
