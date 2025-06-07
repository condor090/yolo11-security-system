"""
Sistema de Eventos para YOMJAI
Almacena eventos del sistema en SQLite
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import asyncio
from contextlib import contextmanager

class EventLogger:
    def __init__(self, db_path: str = "/Users/Shared/yolo11_project/database/yomjai_events.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    description TEXT,
                    zone_id TEXT,
                    severity TEXT DEFAULT 'info',
                    metadata TEXT
                )
            ''')
            
            # Índices para búsquedas rápidas
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp DESC)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_zone_id ON events(zone_id)')
            
    @contextmanager
    def _get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    def log_event(
        self,
        event_type: str,
        event_name: str,
        description: str = None,
        zone_id: str = None,
        severity: str = "info",
        metadata: Dict = None,
        image_path: str = None,
        thumbnail_base64: str = None
    ) -> int:
        """
        Registra un nuevo evento en la base de datos
        
        Args:
            event_type: Tipo de evento (door_open, alarm, system, detection)
            event_name: Nombre corto del evento
            description: Descripción detallada (opcional)
            zone_id: ID de la zona afectada (opcional)
            severity: Severidad (info, warning, error, critical)
            metadata: Datos adicionales en formato dict (opcional)
            image_path: Ruta a la imagen del evento (opcional)
            thumbnail_base64: Thumbnail en base64 para vista rápida (opcional)
            
        Returns:
            ID del evento creado
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO events (event_type, event_name, description, zone_id, 
                                  severity, metadata, image_path, thumbnail_base64)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_type,
                event_name,
                description,
                zone_id,
                severity,
                json.dumps(metadata) if metadata else None,
                image_path,
                thumbnail_base64
            ))
            return cursor.lastrowid
            
    def get_recent_events(self, limit: int = 20, offset: int = 0, search: str = None) -> List[Dict]:
        """
        Obtiene los eventos más recientes con opción de búsqueda
        
        Args:
            limit: Número máximo de eventos a retornar
            offset: Número de eventos a saltar (para paginación)
            search: Término de búsqueda (opcional)
            
        Returns:
            Lista de eventos con formato para el frontend
        """
        with self._get_connection() as conn:
            if search:
                # Búsqueda con LIKE en nombre y descripción
                cursor = conn.execute('''
                    SELECT id, timestamp, event_type, event_name, description, 
                           zone_id, severity, metadata, image_path, thumbnail_base64
                    FROM events
                    WHERE event_name LIKE ? OR description LIKE ? OR zone_id LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                ''', (f'%{search}%', f'%{search}%', f'%{search}%', limit, offset))
            else:
                cursor = conn.execute('''
                    SELECT id, timestamp, event_type, event_name, description, 
                           zone_id, severity, metadata, image_path, thumbnail_base64
                    FROM events
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            
            events = []
            for row in cursor:
                # Formatear hora para el frontend
                timestamp = datetime.fromisoformat(row['timestamp'])
                
                # Mapear severity a type para el frontend
                type_map = {
                    'info': 'info',
                    'warning': 'warning',
                    'error': 'error',
                    'critical': 'error',
                    'success': 'success'
                }
                
                events.append({
                    'id': row['id'],
                    'time': timestamp.strftime('%H:%M'),
                    'date': timestamp.strftime('%Y-%m-%d'),
                    'datetime': timestamp.isoformat(),
                    'event': row['event_name'],
                    'description': row['description'],
                    'type': type_map.get(row['severity'], 'info'),
                    'event_type': row['event_type'],
                    'zone_id': row['zone_id'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None,
                    'image_path': row['image_path'],
                    'thumbnail': row['thumbnail_base64'],
                    'has_image': bool(row['image_path'] or row['thumbnail_base64'])
                })
                
            return events
            
    def get_events_by_type(self, event_type: str, limit: int = 50) -> List[Dict]:
        """Obtiene eventos filtrados por tipo"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM events
                WHERE event_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (event_type, limit))
            
            return [dict(row) for row in cursor]
            
    def get_events_by_zone(self, zone_id: str, limit: int = 50) -> List[Dict]:
        """Obtiene eventos de una zona específica"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM events
                WHERE zone_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (zone_id, limit))
            
            return [dict(row) for row in cursor]
            
    def get_event_stats(self) -> Dict:
        """Obtiene estadísticas de eventos"""
        with self._get_connection() as conn:
            # Total de eventos
            total = conn.execute('SELECT COUNT(*) as count FROM events').fetchone()['count']
            
            # Eventos por tipo
            by_type = conn.execute('''
                SELECT event_type, COUNT(*) as count
                FROM events
                GROUP BY event_type
            ''').fetchall()
            
            # Eventos por severidad
            by_severity = conn.execute('''
                SELECT severity, COUNT(*) as count
                FROM events
                GROUP BY severity
            ''').fetchall()
            
            # Eventos de las últimas 24 horas
            last_24h = conn.execute('''
                SELECT COUNT(*) as count
                FROM events
                WHERE timestamp > datetime('now', '-1 day')
            ''').fetchone()['count']
            
            return {
                'total': total,
                'by_type': {row['event_type']: row['count'] for row in by_type},
                'by_severity': {row['severity']: row['count'] for row in by_severity},
                'last_24h': last_24h
            }
            
    def get_events_by_hour(self, hour: int) -> List[Dict]:
        """
        Obtiene eventos de una hora específica del día actual
        
        Args:
            hour: Hora del día (0-23)
            
        Returns:
            Lista de eventos de esa hora
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM events
                WHERE strftime('%H', timestamp) = ? 
                AND date(timestamp) = date('now')
                ORDER BY timestamp DESC
            ''', (str(hour).zfill(2),))
            
            return [dict(row) for row in cursor]
    
    def get_hourly_stats(self, days: int = 1) -> Dict[int, int]:
        """
        Obtiene estadísticas de eventos por hora
        
        Args:
            days: Número de días hacia atrás para analizar
            
        Returns:
            Diccionario con hora (0-23) como clave y cantidad de eventos como valor
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                FROM events
                WHERE timestamp > datetime('now', '-{} days')
                GROUP BY hour
                ORDER BY hour
            '''.format(days))
            
            # Inicializar todas las horas con 0
            hourly_stats = {i: 0 for i in range(24)}
            
            # Actualizar con los datos reales
            for row in cursor:
                hour = int(row['hour'])
                hourly_stats[hour] = row['count']
                
            return hourly_stats
            
    def clear_old_events(self, days: int = 30):
        """Elimina eventos más antiguos que X días"""
        with self._get_connection() as conn:
            conn.execute('''
                DELETE FROM events
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
# Eventos predefinidos para fácil uso
class EventTypes:
    DOOR_OPEN = "door_open"
    DOOR_CLOSE = "door_close"
    ALARM_TRIGGERED = "alarm"
    ALARM_ACKNOWLEDGED = "alarm_ack"
    SYSTEM = "system"
    DETECTION = "detection"
    CAMERA = "camera"
    ERROR = "error"

# Instancia global
event_logger = EventLogger()
