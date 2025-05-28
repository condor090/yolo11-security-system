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
import socket
import ipaddress
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar nuestros módulos
import sys
sys.path.append(str(Path(__file__).parent.parent))
from alerts.alert_manager_v2_simple import AlertManager, DoorTimer
from backend.camera_manager import CameraManager, CameraConfig

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
camera_manager: Optional[CameraManager] = None
monitoring_active = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global model, alert_manager, camera_manager
    
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
    
    # Cargar CameraManager
    camera_manager = CameraManager()
    camera_manager.start_all()
    logger.info("CameraManager inicializado")
    
    # Iniciar monitor de temporizadores
    asyncio.create_task(timer_monitor())
    
    yield
    
    # Shutdown
    logger.info("Cerrando backend...")
    if camera_manager:
        camera_manager.stop_all()

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

# ==================== CAMERA ENDPOINTS ====================

@app.get("/api/cameras")
async def get_cameras():
    """Obtener lista de cámaras configuradas"""
    if not camera_manager:
        return {"cameras": {}}
    
    return {"cameras": camera_manager.get_camera_status()}

@app.post("/api/cameras")
async def add_camera(config: dict):
    """Agregar nueva cámara"""
    if not camera_manager:
        raise HTTPException(status_code=503, detail="CameraManager no disponible")
    
    try:
        cam_config = CameraConfig(**config)
        camera_manager.add_camera(cam_config)
        return {"success": True, "message": f"Cámara {cam_config.name} agregada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/cameras/{camera_id}")
async def get_camera(camera_id: str):
    """Obtener información de una cámara específica"""
    if not camera_manager or camera_id not in camera_manager.configs:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    config = camera_manager.configs[camera_id]
    return {
        "id": config.id,
        "name": config.name,
        "ip": config.ip,
        "username": config.username,
        "password": config.password,  # En producción, considerar no enviar esto
        "rtsp_port": config.rtsp_port,
        "channel": config.channel,
        "stream": config.stream,
        "zone_id": config.zone_id,
        "enabled": config.enabled
    }

@app.put("/api/cameras/{camera_id}")
async def update_camera(camera_id: str, config: dict):
    """Actualizar cámara existente"""
    if not camera_manager:
        raise HTTPException(status_code=503, detail="CameraManager no disponible")
    
    try:
        # Obtener configuración actual
        if camera_id not in camera_manager.configs:
            raise HTTPException(status_code=404, detail="Cámara no encontrada")
        
        current_config = camera_manager.configs[camera_id]
        
        # Si no se envía contraseña, mantener la actual
        if 'password' not in config or config['password'] == '':
            config['password'] = current_config.password
        
        # Determinar si necesitamos reconectar (solo si cambian parámetros de conexión)
        needs_reconnect = (
            config.get('ip') != current_config.ip or
            config.get('username') != current_config.username or
            config.get('password') != current_config.password or
            config.get('rtsp_port') != current_config.rtsp_port or
            config.get('channel') != current_config.channel or
            config.get('stream') != current_config.stream
        )
        
        # Actualizar la configuración
        new_config = CameraConfig(**config)
        camera_manager.configs[camera_id] = new_config
        camera_manager.save_configs()
        
        # Solo reconectar si es necesario
        if needs_reconnect and camera_id in camera_manager.cameras:
            camera_manager.stop_camera(camera_id)
            if new_config.enabled:
                camera_manager.start_camera(camera_id)
        elif new_config.enabled and camera_id not in camera_manager.cameras:
            # Si está habilitada pero no está corriendo, iniciarla
            camera_manager.start_camera(camera_id)
        elif not new_config.enabled and camera_id in camera_manager.cameras:
            # Si está deshabilitada pero está corriendo, detenerla
            camera_manager.stop_camera(camera_id)
        
        return {"success": True, "message": f"Cámara {camera_id} actualizada"}
    except Exception as e:
        logger.error(f"Error actualizando cámara: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/cameras/{camera_id}")
async def remove_camera(camera_id: str):
    """Eliminar cámara"""
    if not camera_manager:
        raise HTTPException(status_code=503, detail="CameraManager no disponible")
    
    camera_manager.remove_camera(camera_id)
    return {"success": True, "message": f"Cámara {camera_id} eliminada"}

@app.post("/api/cameras/{camera_id}/test")
async def test_camera_connection(camera_id: str):
    """Probar conexión con una cámara"""
    if not camera_manager or camera_id not in camera_manager.configs:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    config = camera_manager.configs[camera_id]
    
    # Crear una instancia temporal para probar
    from backend.camera_manager import CameraStream
    test_stream = CameraStream(config)
    
    # Intentar conectar
    success = test_stream.connect()
    
    # Limpiar
    if test_stream.cap:
        test_stream.cap.release()
    
    return {
        "success": success,
        "message": "Conexión exitosa" if success else "No se pudo conectar",
        "rtsp_url": config.rtsp_url
    }

@app.post("/api/cameras/scan")
async def scan_network_for_cameras():
    """Escanear la red en busca de cámaras IP"""
    import socket
    import ipaddress
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import requests
    
    def get_local_network():
        """Obtener el rango de red local"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            # Asumiendo una red /24
            network = ipaddress.ip_network(f"{local_ip}/24", strict=False)
            return network
        except:
            # Red por defecto
            return ipaddress.ip_network("192.168.1.0/24")
    
    def check_rtsp_port(ip_str, port=554, timeout=0.5):
        """Verificar si el puerto RTSP está abierto"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip_str, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def check_hikvision_http(ip_str, timeout=1):
        """Verificar si es una cámara Hikvision por HTTP"""
        ports = [80, 8080]
        
        for port in ports:
            try:
                url = f"http://{ip_str}:{port}"
                response = requests.get(url, timeout=timeout, verify=False)
                
                # Buscar indicadores de Hikvision
                if any(indicator in response.text.lower() for indicator in ['hikvision', 'hik', 'dvr', 'nvr']):
                    return True, port
            except:
                pass
        
        return False, None
    
    logger.info("Iniciando escaneo de red para cámaras")
    
    try:
        network = get_local_network()
        found_cameras = []
        
        # Usar ThreadPoolExecutor para escaneo paralelo
        with ThreadPoolExecutor(max_workers=50) as executor:
            # Crear futures para cada IP
            future_to_ip = {}
            for ip in network.hosts():
                future = executor.submit(check_rtsp_port, str(ip))
                future_to_ip[future] = str(ip)
            
            # Procesar resultados conforme se completan
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    has_rtsp = future.result()
                    if has_rtsp:
                        # Verificar si es Hikvision
                        is_hik, http_port = check_hikvision_http(ip)
                        
                        camera_info = {
                            "ip": ip,
                            "rtsp_port": 554,
                            "rtsp_open": True,
                            "http_port": http_port,
                            "confirmed_hikvision": is_hik,
                            "name": f"Cámara {ip}"
                        }
                        
                        found_cameras.append(camera_info)
                        logger.info(f"Cámara encontrada en {ip}")
                        
                except Exception as e:
                    logger.error(f"Error verificando {ip}: {e}")
        
        logger.info(f"Escaneo completado. {len(found_cameras)} cámaras encontradas")
        
        return {
            "success": True,
            "cameras": found_cameras,
            "network_scanned": str(network),
            "total_found": len(found_cameras)
        }
        
    except Exception as e:
        logger.error(f"Error en escaneo de red: {e}")
        raise HTTPException(status_code=500, detail=str(e))
async def test_camera_connection(camera_id: str):
    """Probar conexión con una cámara"""
    if not camera_manager or camera_id not in camera_manager.configs:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    config = camera_manager.configs[camera_id]
    
    # Crear una instancia temporal para probar
    from backend.camera_manager import CameraStream
    test_stream = CameraStream(config)
    
    # Intentar conectar
    success = test_stream.connect()
    
    # Limpiar
    if test_stream.cap:
        test_stream.cap.release()
    
    return {
        "success": success,
        "message": "Conexión exitosa" if success else "No se pudo conectar",
        "rtsp_url": config.rtsp_url
    }

@app.get("/api/cameras/{camera_id}/stream")
async def get_camera_stream(camera_id: str):
    """Obtener frame actual de una cámara"""
    if not camera_manager or camera_id not in camera_manager.cameras:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    camera = camera_manager.cameras[camera_id]
    frame = camera.get_frame()
    
    if frame is None:
        raise HTTPException(status_code=503, detail="No hay frame disponible")
    
    # Convertir frame a JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "camera_id": camera_id,
        "image": f"data:image/jpeg;base64,{img_base64}",
        "fps": camera.fps,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/cameras/{camera_id}/context")
async def get_camera_context(
    camera_id: str,
    event_time: str,
    before_seconds: int = 30,
    after_seconds: int = 30
):
    """Obtener video de contexto de un evento"""
    if not camera_manager or camera_id not in camera_manager.cameras:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    try:
        event_dt = datetime.fromisoformat(event_time)
        camera = camera_manager.cameras[camera_id]
        frames = camera.get_context_video(event_dt, before_seconds, after_seconds)
        
        # Convertir frames a base64 para enviar
        context_data = []
        for frame, timestamp in frames:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            context_data.append({
                "timestamp": timestamp.isoformat(),
                "image": f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
            })
        
        return {
            "camera_id": camera_id,
            "event_time": event_time,
            "frames": context_data,
            "total_frames": len(context_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/cameras/{camera_id}/record")
async def start_recording(camera_id: str):
    """Iniciar grabación de una cámara"""
    if not camera_manager or camera_id not in camera_manager.cameras:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    camera = camera_manager.cameras[camera_id]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"recordings/{camera_id}_{timestamp}.mp4"
    
    # Crear directorio si no existe
    Path("recordings").mkdir(exist_ok=True)
    
    camera.start_recording(output_path)
    
    return {"success": True, "recording_path": output_path}

@app.post("/api/cameras/{camera_id}/stop-recording")
async def stop_recording(camera_id: str):
    """Detener grabación de una cámara"""
    if not camera_manager or camera_id not in camera_manager.cameras:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    camera = camera_manager.cameras[camera_id]
    camera.stop_recording()
    
    return {"success": True}

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
                
                # Agregar información de cámaras a los timers
                for timer in timers:
                    if camera_manager and timer.get('door_id'):
                        # Buscar cámara asociada a la zona
                        camera = camera_manager.get_camera_by_zone(timer['door_id'])
                        if camera:
                            timer['has_camera'] = True
                            timer['camera_id'] = camera.config.id
                            timer['camera_name'] = camera.config.name
                            timer['camera_connected'] = camera.current_frame is not None
                        else:
                            timer['has_camera'] = False
                
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
        port=8889,
        reload=True,
        log_level="info"
    )
