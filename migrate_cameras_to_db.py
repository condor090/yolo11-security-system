#!/usr/bin/env python3
"""
Script para migrar las configuraciones de cámaras desde JSON a SQLite
"""
import sys
sys.path.append('/Users/Shared/yolo11_project')

from backend.utils.camera_config_db import CameraConfigDB
from pathlib import Path
import json
import shutil
from datetime import datetime

def migrate_cameras_to_db():
    """Migra las configuraciones de cámaras a base de datos"""
    print("🎥 Migración de Configuraciones de Cámaras a Base de Datos")
    print("=" * 60)
    
    # Inicializar base de datos
    camera_db = CameraConfigDB()
    
    # Rutas
    json_path = "/Users/Shared/yolo11_project/cameras/camera_config.json"
    
    if not Path(json_path).exists():
        print("❌ No se encontró archivo camera_config.json")
        return
    
    # Leer configuraciones actuales
    print(f"\n📄 Leyendo configuraciones desde: {json_path}")
    with open(json_path, 'r') as f:
        configs = json.load(f)
    
    print(f"   Encontradas {len(configs)} cámaras")
    
    # Mostrar configuraciones actuales
    print("\n📸 Configuraciones a migrar:")
    for cam_id, config in configs.items():
        print(f"   - {cam_id}: {config.get('name', 'Sin nombre')} ({config.get('ip', 'Sin IP')})")
    
    # Crear backup
    backup_path = json_path.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    shutil.copy(json_path, backup_path)
    print(f"\n💾 Backup creado: {backup_path}")
    
    # Migrar
    print("\n🔄 Migrando a base de datos...")
    migrated = camera_db.migrate_from_json(json_path)
    print(f"   ✅ Migradas {migrated} configuraciones")
    
    # Verificar migración
    print("\n🔍 Verificando migración:")
    db_configs = camera_db.get_all_camera_configs()
    for cam_id, config in db_configs.items():
        print(f"   ✓ {cam_id}: {config['name']} - OK")
    
    # Mostrar historial
    print("\n📜 Historial de cambios:")
    for cam_id in db_configs:
        history = camera_db.get_camera_history(cam_id, limit=1)
        if history:
            print(f"   - {cam_id}: {history[0]['change_type']} at {history[0]['changed_at']}")
    
    print("\n✅ Migración completada exitosamente")
    print("\n💡 Nota: El sistema ahora usará la base de datos SQLite")
    print("   Las configuraciones son persistentes y con historial de cambios")

if __name__ == "__main__":
    migrate_cameras_to_db()
