#!/usr/bin/env python3
"""
Script para reinicio completo del sistema
"""

import os
import json
import shutil
from pathlib import Path

print("🔄 REINICIO COMPLETO DEL SISTEMA")
print("================================")

# Directorio base
base_dir = Path(__file__).parent

# 1. Detener todos los procesos
print("\n1️⃣ Deteniendo procesos...")
os.system("pkill -f 'python.*main.py' 2>/dev/null || true")
os.system("pkill -f 'npm' 2>/dev/null || true")
os.system("pkill -f 'node.*react' 2>/dev/null || true")
print("   ✅ Procesos detenidos")

# 2. Limpiar archivos de estado
print("\n2️⃣ Limpiando archivos de estado...")
files_to_clean = [
    "alerts/alert_state.json",
    "alerts/alert_state_v2.json", 
    "alerts/door_timers.json",
    "alerts/active_timers.json",
    "backend/camera_state.json",
    "backend/*.log",
    "backend_test.log",
    "*.log"
]

for pattern in files_to_clean:
    for file_path in base_dir.glob(pattern):
        if file_path.exists():
            print(f"   🗑️  Eliminando: {file_path.name}")
            file_path.unlink()

# 3. Resetear configuración de cámaras
print("\n3️⃣ Reseteando configuración de cámaras...")
camera_config = base_dir / "cameras/camera_config.json"
if camera_config.exists():
    # Mantener la configuración pero limpiar estados
    with open(camera_config, 'r') as f:
        config = json.load(f)
    
    # Asegurar que las cámaras estén habilitadas
    for cam_id, cam_data in config.items():
        cam_data['enabled'] = True
    
    with open(camera_config, 'w') as f:
        json.dump(config, f, indent=2)
    print("   ✅ Configuración de cámaras reseteada")

# 4. Crear estado limpio para AlertManager
print("\n4️⃣ Creando estado limpio...")
clean_state = {
    "alert_history": [],
    "cooldown_tracker": {},
    "monitored_doors": {},
    "door_timers": {},
    "statistics": {}
}

alerts_dir = base_dir / "alerts"
alerts_dir.mkdir(exist_ok=True)

for state_file in ["alert_state.json", "alert_state_v2.json"]:
    file_path = alerts_dir / state_file
    with open(file_path, 'w') as f:
        json.dump(clean_state, f, indent=2)
    print(f"   ✅ Creado: {state_file}")

# 5. Limpiar logs antiguos
print("\n5️⃣ Limpiando logs...")
log_patterns = ["*.log", "logs/*.log", "backend/*.log"]
for pattern in log_patterns:
    for log_file in base_dir.glob(pattern):
        if log_file.exists():
            log_file.unlink()
            print(f"   🗑️  Eliminado: {log_file.name}")

# 6. Verificar puertos
print("\n6️⃣ Verificando puertos...")
os.system("lsof -ti:8889 | xargs kill -9 2>/dev/null || true")
os.system("lsof -ti:3000 | xargs kill -9 2>/dev/null || true")
print("   ✅ Puertos 8889 y 3000 liberados")

print("\n✅ SISTEMA COMPLETAMENTE REINICIADO")
print("\n📝 Próximos pasos:")
print("   1. cd backend && python3 main.py")
print("   2. cd frontend && npm start")
print("\n🎯 El sistema iniciará en estado completamente limpio")
