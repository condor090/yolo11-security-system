#!/usr/bin/env python3
"""
Script de diagnóstico para el sistema de audio
Verifica el cálculo correcto de fases
"""

import sys
sys.path.append('/Users/Shared/yolo11_project')

from backend.utils.audio_service import audio_service

# Simular diferentes tiempos transcurridos con un timer de 15 segundos
test_cases = [
    (5, 15),    # 33% - debería ser fase 1 (friendly)
    (8, 15),    # 53% - debería ser fase 2 (moderate)
    (14, 15),   # 93% - debería ser fase 3 (critical)
    (20, 15),   # 133% - debería ser fase 3 (critical)
    (128, 15),  # 853% - definitivamente fase 3 (critical)
]

print("=== DIAGNÓSTICO DE FASES DE AUDIO ===\n")

for elapsed, total in test_cases:
    # Obtener la configuración de fase
    phase_config = audio_service._get_percentage_phase(elapsed, total)
    percentage = (elapsed / total) * 100
    
    print(f"Tiempo transcurrido: {elapsed}s de {total}s ({percentage:.1f}%)")
    print(f"Fase calculada: {phase_config['name']} (fase {phase_config['phase_number']})")
    print(f"Intervalo de sonido: {phase_config['interval']}s")
    print("-" * 50)

# Verificar la configuración actual
print("\n=== CONFIGURACIÓN ACTUAL DE FASES ===")
config = audio_service.config.get("default_phases", {})
for phase_key, phase_data in config.items():
    print(f"{phase_key}: {phase_data['percentage']}% - intervalo {phase_data['interval_seconds']}s")
