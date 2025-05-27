#!/usr/bin/env python3
"""
Backend API con FastAPI para Sistema de Seguridad YOLO11
Arquitectura profesional con WebSockets y tiempo real
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO
import base64
from PIL import Image
import io
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar nuestros módulos
import sys
sys.path.append(str(Path(__file__).parent.parent))
from alerts.alert_manager_v2_simple import AlertManager, DoorTimer

# Manager de conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Cliente conectado. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Cliente desconectado. Total: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: dict):
        """Enviar mensaje a todos los clientes conectados"""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error enviando mensaje: {e}")
                dead_connections.append(connection)
        
        # Limpiar conexiones muertas
        for conn in dead_connections:
            self.active_connections.remove(conn)

# Instancias globales
manager = ConnectionManager()
model: Optional[YOLO] = None
alert_manager: Optional[AlertManager] = None
monitoring_active = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global model, alert_manager
    
    # Startup
    logger.info("Iniciando backend...")
    
    # Cargar modelo YOLO
    model_path = Path(__file__).parent.parent / 'runs' / 'gates' / 'gate_detector_v1' / 'weights' / 'best.pt'
    if model_path.exists():
        model = YOLO(str(model_path))
        logger.info("Modelo YOLO cargado exitosamente")
    else:
        logger.error(f"Modelo no encontrado en {model_path}")
    
    # Cargar AlertManager
    config_path = Path(__file__).parent.parent / 'alerts' / 'alert_config_v2.json'
    alert_manager = AlertManager(str(config_path))
    logger.info("AlertManager inicializado")
    
    # Iniciar monitor de temporizadores
    asyncio.create_task(timer_monitor())
    
    yield
    
    # Shutdown
    logger.info("Cerrando backend...")

# Crear aplicación FastAPI
app = FastAPI(
    title="YOLO11 Security System API",
    version="3.0.0",
    description="API profesional para sistema de seguridad con detección de puertas",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "YOLO11 Security System API",
        "version": "3.0.0",
        "status": "operational",
        "model_loaded": model is not None,
        "alert_manager_loaded": alert_manager is not None
    }

@app.get("/api/health")
async def health_check():
    """Verificar salud del sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "model": "active" if model else "inactive",
            "alerts": "active" if alert_manager else "inactive",
            "websocket": len(manager.active_connections)
        }
    }

@app.post("/api/detect")
async def detect_image(file: UploadFile = File(...)):
    """Detectar puertas en imagen subida"""
    if not model:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    
    try:
        # Leer imagen
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detectar con YOLO
        results = model.predict(image, conf=0.5, iou=0.5, verbose=False)
        
        # Procesar detecciones
        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            for i, box in enumerate(results[0].boxes):
                detection = {
                    'id': f"det_{i}",
                    'class_name': model.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': {
                        'x1': int(box.xyxy[0][0]),
                        'y1': int(box.xyxy[0][1]),
                        'x2': int(box.xyxy[0][2]),
                        'y2': int(box.xyxy[0][3])
                    },
                    'door_id': f"door_{i}"
                }
                detections.append(detection)
        
        # Procesar con AlertManager
        if alert_manager and detections:
            await alert_manager.process_detection(detections, camera_id="upload")
        
        # Obtener imagen anotada
        annotated = results[0].plot()
        _, buffer = cv2.imencode('.jpg', annotated)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Broadcast a clientes WebSocket
        await manager.broadcast({
            'type': 'detection',
            'data': {
                'detections': detections,
                'image': f"data:image/jpeg;base64,{img_base64}",
                'timestamp': datetime.now().isoformat()
            }
        })
        
        return {
            'success': True,
            'detections': detections,
            'image': f"data:image/jpeg;base64,{img_base64}",
            'timers': alert_manager.get_active_timers() if alert_manager else []
        }
        
    except Exception as e:
        logger.error(f"Error en detección: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/timers")
async def get_timers():
    """Obtener temporizadores activos"""
    if not alert_manager:
        return {"timers": []}
    
    return {
        "timers": alert_manager.get_active_timers(),
        "alarm_active": alert_manager.alarm_active if hasattr(alert_manager, 'alarm_active') else False
    }

@app.post("/api/timers/acknowledge/{door_id}")
async def acknowledge_timer(door_id: str):
    """Reconocer alarma de una puerta"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="AlertManager no disponible")
    
    alert_manager.acknowledge_alarm(door_id)
    
    # Broadcast actualización
    await manager.broadcast({
        'type': 'timer_acknowledged',
        'data': {'door_id': door_id}
    })
    
    return {"success": True, "message": f"Alarma {door_id} reconocida"}

@app.post("/api/alarms/stop-all")
async def stop_all_alarms():
    """Detener todas las alarmas"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="AlertManager no disponible")
    
    alert_manager.stop_all_alarms()
    
    # Broadcast
    await manager.broadcast({
        'type': 'alarms_stopped',
        'data': {'timestamp': datetime.now().isoformat()}
    })
    
    return {"success": True, "message": "Todas las alarmas detenidas"}

@app.get("/api/config")
async def get_config():
    """Obtener configuración actual"""
    if not alert_manager:
        return {"config": {}}
    
    return {"config": alert_manager.config}

@app.put("/api/config")
async def update_config(config: dict):
    """Actualizar configuración"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="AlertManager no disponible")
    
    try:
        # Actualizar configuración
        alert_manager.config.update(config)
        alert_manager.save_config()
        
        # Broadcast
        await manager.broadcast({
            'type': 'config_updated',
            'data': config
        })
        
        return {"success": True, "message": "Configuración actualizada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/statistics")
async def get_statistics():
    """Obtener estadísticas del sistema"""
    if not alert_manager:
        return {"statistics": {}}
    
    stats = alert_manager.get_alert_statistics(hours=24)
    stats['websocket_clients'] = len(manager.active_connections)
    
    return {"statistics": stats}

# ==================== WEBSOCKET ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para comunicación en tiempo real"""
    await manager.connect(websocket)
    
    try:
        # Enviar estado inicial
        await websocket.send_json({
            'type': 'connection',
            'data': {
                'status': 'connected',
                'timestamp': datetime.now().isoformat()
            }
        })
        
        while True:
            # Recibir mensajes del cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Procesar comandos
            if message.get('type') == 'ping':
                await websocket.send_json({
                    'type': 'pong',
                    'data': {'timestamp': datetime.now().isoformat()}
                })
            
            elif message.get('type') == 'start_monitoring':
                global monitoring_active
                monitoring_active = True
                await websocket.send_json({
                    'type': 'monitoring_started',
                    'data': {'status': 'active'}
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        manager.disconnect(websocket)

# ==================== TAREAS ASÍNCRONAS ====================

async def timer_monitor():
    """Monitor de temporizadores que envía actualizaciones por WebSocket"""
    while True:
        try:
            if alert_manager and len(manager.active_connections) > 0:
                timers = alert_manager.get_active_timers()
                
                # Broadcast estado de temporizadores
                await manager.broadcast({
                    'type': 'timer_update',
                    'data': {
                        'timers': timers,
                        'alarm_active': getattr(alert_manager, 'alarm_active', False),
                        'timestamp': datetime.now().isoformat()
                    }
                })
            
            await asyncio.sleep(0.5)  # Actualizar cada 500ms
            
        except Exception as e:
            logger.error(f"Error en timer_monitor: {e}")
            await asyncio.sleep(1)

# ==================== ARRANQUE ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8888,
        reload=True,
        log_level="info"
    )
