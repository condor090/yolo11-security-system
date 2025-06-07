"""
Sistema de almacenamiento de configuración de cámaras en base de datos SQLite
Reemplaza el almacenamiento en JSON por una solución más robusta
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class CameraConfigDB:
    def __init__(self, db_path: str = "/Users/Shared/yolo11_project/database/yomjai_cameras.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self._get_connection() as conn:
            # Tabla principal de configuración de cámaras
            conn.execute('''
                CREATE TABLE IF NOT EXISTS camera_configs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    rtsp_port INTEGER DEFAULT 554,
                    channel INTEGER DEFAULT 1,
                    stream TEXT DEFAULT 'main',
                    zone_id TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Índices para búsquedas rápidas
            conn.execute('CREATE INDEX IF NOT EXISTS idx_camera_ip ON camera_configs(ip)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_camera_zone ON camera_configs(zone_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_camera_enabled ON camera_configs(enabled)')
            
            # Tabla de historial de cambios
            conn.execute('''
                CREATE TABLE IF NOT EXISTS camera_config_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    camera_id TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    old_values TEXT,
                    new_values TEXT,
                    changed_by TEXT,
                    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (camera_id) REFERENCES camera_configs(id)
                )
            ''')
            
    @contextmanager
    def _get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    def save_camera_config(self, config: Dict) -> bool:
        """
        Guarda o actualiza la configuración de una cámara
        """
        try:
            with self._get_connection() as conn:
                # Verificar si existe
                existing = conn.execute(
                    'SELECT * FROM camera_configs WHERE id = ?',
                    (config['id'],)
                ).fetchone()
                
                if existing:
                    # Actualizar
                    old_values = dict(existing)
                    
                    conn.execute('''
                        UPDATE camera_configs
                        SET name = ?, ip = ?, username = ?, password = ?,
                            rtsp_port = ?, channel = ?, stream = ?,
                            zone_id = ?, enabled = ?, updated_at = CURRENT_TIMESTAMP,
                            metadata = ?
                        WHERE id = ?
                    ''', (
                        config.get('name'),
                        config.get('ip'),
                        config.get('username'),
                        config.get('password'),
                        config.get('rtsp_port', 554),
                        config.get('channel', 1),
                        config.get('stream', 'main'),
                        config.get('zone_id'),
                        config.get('enabled', True),
                        json.dumps(config.get('metadata', {})),
                        config['id']
                    ))
                    
                    # Registrar cambio en historial
                    self._log_change(
                        conn,
                        config['id'],
                        'update',
                        old_values,
                        config
                    )
                    
                    logger.info(f"Cámara {config['id']} actualizada en DB")
                else:
                    # Insertar nueva
                    conn.execute('''
                        INSERT INTO camera_configs
                        (id, name, ip, username, password, rtsp_port,
                         channel, stream, zone_id, enabled, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        config['id'],
                        config.get('name'),
                        config.get('ip'),
                        config.get('username'),
                        config.get('password'),
                        config.get('rtsp_port', 554),
                        config.get('channel', 1),
                        config.get('stream', 'main'),
                        config.get('zone_id'),
                        config.get('enabled', True),
                        json.dumps(config.get('metadata', {}))
                    ))
                    
                    # Registrar cambio en historial
                    self._log_change(
                        conn,
                        config['id'],
                        'create',
                        None,
                        config
                    )
                    
                    logger.info(f"Cámara {config['id']} creada en DB")
                    
                return True
                
        except Exception as e:
            logger.error(f"Error guardando configuración de cámara: {e}")
            return False
            
    def get_camera_config(self, camera_id: str) -> Optional[Dict]:
        """Obtiene la configuración de una cámara específica"""
        with self._get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM camera_configs WHERE id = ?',
                (camera_id,)
            ).fetchone()
            
            if row:
                config = dict(row)
                if config.get('metadata'):
                    config['metadata'] = json.loads(config['metadata'])
                return config
            return None
            
    def get_all_camera_configs(self) -> Dict[str, Dict]:
        """Obtiene todas las configuraciones de cámaras"""
        configs = {}
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM camera_configs ORDER BY created_at'
            )
            
            for row in cursor:
                config = dict(row)
                if config.get('metadata'):
                    config['metadata'] = json.loads(config['metadata'])
                configs[config['id']] = config
                
        return configs
        
    def delete_camera_config(self, camera_id: str) -> bool:
        """Elimina la configuración de una cámara"""
        try:
            with self._get_connection() as conn:
                # Obtener configuración actual para el historial
                existing = conn.execute(
                    'SELECT * FROM camera_configs WHERE id = ?',
                    (camera_id,)
                ).fetchone()
                
                if existing:
                    # Primero registrar eliminación en el historial
                    self._log_change(
                        conn,
                        camera_id,
                        'delete',
                        dict(existing),
                        None
                    )
                    
                    # Luego eliminar todos los registros del historial para evitar FK constraint
                    conn.execute(
                        'DELETE FROM camera_config_history WHERE camera_id = ?',
                        (camera_id,)
                    )
                    
                    # Finalmente eliminar la configuración
                    conn.execute(
                        'DELETE FROM camera_configs WHERE id = ?',
                        (camera_id,)
                    )
                    
                    logger.info(f"Cámara {camera_id} eliminada de DB")
                    return True
                    
        except Exception as e:
            logger.error(f"Error eliminando cámara: {e}")
            
        return False
        
    def _log_change(self, conn, camera_id: str, change_type: str, 
                    old_values: Optional[Dict], new_values: Optional[Dict]):
        """Registra un cambio en el historial"""
        conn.execute('''
            INSERT INTO camera_config_history
            (camera_id, change_type, old_values, new_values)
            VALUES (?, ?, ?, ?)
        ''', (
            camera_id,
            change_type,
            json.dumps(old_values) if old_values else None,
            json.dumps(new_values) if new_values else None
        ))
        
    def get_camera_history(self, camera_id: str, limit: int = 50) -> List[Dict]:
        """Obtiene el historial de cambios de una cámara"""
        history = []
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM camera_config_history
                WHERE camera_id = ?
                ORDER BY changed_at DESC
                LIMIT ?
            ''', (camera_id, limit))
            
            for row in cursor:
                entry = dict(row)
                if entry.get('old_values'):
                    entry['old_values'] = json.loads(entry['old_values'])
                if entry.get('new_values'):
                    entry['new_values'] = json.loads(entry['new_values'])
                history.append(entry)
                
        return history
        
    def migrate_from_json(self, json_path: str):
        """Migra configuraciones desde archivo JSON a la base de datos"""
        try:
            with open(json_path, 'r') as f:
                configs = json.load(f)
                
            migrated = 0
            for cam_id, config in configs.items():
                if 'id' not in config:
                    config['id'] = cam_id
                    
                if self.save_camera_config(config):
                    migrated += 1
                    
            logger.info(f"Migradas {migrated} configuraciones de cámaras desde JSON")
            return migrated
            
        except Exception as e:
            logger.error(f"Error migrando desde JSON: {e}")
            return 0
            
    def export_to_json(self, json_path: str):
        """Exporta las configuraciones a un archivo JSON (backup)"""
        try:
            configs = self.get_all_camera_configs()
            
            # Limpiar campos internos
            for config in configs.values():
                config.pop('created_at', None)
                config.pop('updated_at', None)
                
            with open(json_path, 'w') as f:
                json.dump(configs, f, indent=2)
                
            logger.info(f"Exportadas {len(configs)} configuraciones a JSON")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a JSON: {e}")
            return False

# Instancia global para uso fácil
camera_config_db = CameraConfigDB()
