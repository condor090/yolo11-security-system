#!/usr/bin/env python3
"""
Backend API con FastAPI para Sistema de Seguridad YOLO11
Arquitectura profesional con WebSockets y tiempo real
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
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

# Importar servicio de audio
try:
    from backend.utils.audio_service import audio_service
    AUDIO_SERVICE_AVAILABLE = True
    logger.info("🔊 Servicio de audio importado")
except ImportError:
    AUDIO_SERVICE_AVAILABLE = False
    audio_service = None
    logger.warning("⚠️ Servicio de audio no disponible")

# Importar nuestros módulos
import sys
sys.path.append(str(Path(__file__).parent.parent))
from alerts.alert_manager_v2_simple import AlertManager, DoorTimer
from backend.camera_manager import CameraManager, CameraConfig
from backend.utils.detection_manager import DetectionManager
from backend.utils.eco_mode import EcoModeManager, SystemState
from backend.utils.telegram_service import telegram_service
try:
    from backend.optimized_config import DETECTION_CONFIG, RESOURCE_CONFIG
except ImportError:
    DETECTION_CONFIG = {"interval": 0.5, "max_fps": 30, "jpeg_quality": 70}
    RESOURCE_CONFIG = {"max_workers": 4}

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
detection_manager: Optional[DetectionManager] = None
eco_manager: Optional[EcoModeManager] = None
monitoring_active = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global model, alert_manager, camera_manager, detection_manager, eco_manager
    
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
    
    # Configurar Telegram si está en la configuración
    if alert_manager and 'telegram' in alert_manager.config:
        tg_config = alert_manager.config['telegram']
        telegram_service.configure(
            bot_token=tg_config.get('bot_token', ''),
            chat_id=tg_config.get('chat_id', ''),
            enabled=tg_config.get('enabled', False)
        )
        logger.info(f"Telegram configurado: {telegram_service.enabled}")
    
    # Cargar CameraManager
    camera_manager = CameraManager()
    camera_manager.start_all()
    logger.info("CameraManager inicializado")
    
    # Inicializar DetectionManager
    detection_manager = DetectionManager(
        state_timeout=5.0,  # 5 segundos sin detección = objeto ausente
        min_confidence=0.75  # Confianza mínima
    )
    logger.info("DetectionManager inicializado")
    
    # Inicializar EcoModeManager
    eco_manager = EcoModeManager()
    logger.info("Modo Eco inicializado en estado IDLE")
    
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
            
            # NO enviar alerta inmediata a Telegram - solo cuando expire el timer
            # for detection in detections:
            #     if detection['class_name'] == 'gate_open' and telegram_service.enabled:
            #         zone_name = alert_manager.config['zones'].get(detection['door_id'], {}).get('name', detection['door_id'])
            #         await telegram_service.send_alert(
            #             zone_id=detection['door_id'],
            #             zone_name=zone_name,
            #             detection_type='puerta_abierta',
            #             image=annotated if 'annotated' in locals() else None
            #         )
        
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
    
    # También resetear el detection manager
    if detection_manager:
        detection_manager.reset_all()
    
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
        
        # Configurar Telegram si está presente
        if 'telegram' in config:
            tg_config = config['telegram']
            telegram_service.configure(
                bot_token=tg_config.get('bot_token', ''),
                chat_id=tg_config.get('chat_id', ''),
                enabled=tg_config.get('enabled', False)
            )
            logger.info(f"Telegram configurado: {telegram_service.enabled}")
        
        # Broadcast
        await manager.broadcast({
            'type': 'config_updated',
            'data': config
        })
        
        return {"success": True, "message": "Configuración actualizada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/telegram/test")
async def test_telegram(config: dict):
    """Enviar mensaje de prueba a Telegram"""
    try:
        # Configurar temporalmente para la prueba
        telegram_service.configure(
            bot_token=config.get('bot_token', ''),
            chat_id=config.get('chat_id', ''),
            enabled=True
        )
        
        # Enviar mensaje de prueba
        success = await telegram_service.send_test_message()
        
        if success:
            return {"success": True, "message": "Mensaje de prueba enviado correctamente"}
        else:
            raise HTTPException(status_code=400, detail="No se pudo enviar el mensaje de prueba")
            
    except Exception as e:
        logger.error(f"Error probando Telegram: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/process-detection")
async def process_detection(data: dict):
    """Procesar detecciones enviadas manualmente"""
    if not alert_manager:
        raise HTTPException(status_code=503, detail="AlertManager no disponible")
    
    try:
        detections = data.get('detections', [])
        camera_id = data.get('camera_id', 'manual')
        
        # Procesar con AlertManager
        await alert_manager.process_detection(detections, camera_id=camera_id)
        
        # Obtener timers actualizados
        timers = alert_manager.get_active_timers()
        
        # Broadcast actualización
        await manager.broadcast({
            'type': 'timer_update',
            'data': {
                'timers': timers,
                'alarm_active': alert_manager.alarm_active,
                'timestamp': datetime.now().isoformat()
            }
        })
        
        return {
            "success": True,
            "timers": timers,
            "alarm_active": alert_manager.alarm_active
        }
        
    except Exception as e:
        logger.error(f"Error procesando detección: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/statistics")
async def get_statistics():
    """Obtener estadísticas del sistema"""
    if not alert_manager:
        return {"statistics": {}}
    
    stats = alert_manager.get_alert_statistics(hours=24)
    stats['websocket_clients'] = len(manager.active_connections)
    
    # Agregar estado de zonas
    if detection_manager:
        stats['zone_states'] = detection_manager.get_zone_states()
    
    return {"statistics": stats}

@app.get("/api/zones")
async def get_zones():
    """Obtener estado de todas las zonas"""
    if not detection_manager:
        return {"zones": {}}
    
    return {"zones": detection_manager.get_zone_states()}

@app.get("/api/eco-mode")
async def get_eco_mode():
    """Obtener estado del Modo Eco"""
    if not eco_manager:
        return {"eco_mode": {"enabled": False}}
    
    return {
        "eco_mode": {
            "enabled": True,
            "status": eco_manager.get_status(),
            "current_state": eco_manager.current_state.value,
            "settings": {
                "idle_timeout": eco_manager.idle_timeout,
                "alert_timeout": eco_manager.alert_timeout,
                "motion_threshold": eco_manager.motion_threshold
            }
        }
    }

@app.put("/api/eco-mode")
async def update_eco_mode(settings: dict):
    """Actualizar configuración del Modo Eco"""
    if not eco_manager:
        raise HTTPException(status_code=503, detail="Modo Eco no disponible")
    
    try:
        # Actualizar timeouts
        if 'idle_timeout' in settings:
            eco_manager.idle_timeout = float(settings['idle_timeout'])
        
        if 'alert_timeout' in settings:
            eco_manager.alert_timeout = float(settings['alert_timeout'])
        
        if 'motion_threshold' in settings:
            eco_manager.motion_threshold = float(settings['motion_threshold'])
        
        # Forzar estado si se especifica
        if 'force_state' in settings:
            state_map = {
                'idle': SystemState.IDLE,
                'alert': SystemState.ALERT,
                'active': SystemState.ACTIVE
            }
            if settings['force_state'] in state_map:
                eco_manager.current_state = state_map[settings['force_state']]
        
        # Broadcast actualización
        await manager.broadcast({
            'type': 'eco_mode_updated',
            'data': eco_manager.get_status()
        })
        
        return {"success": True, "message": "Modo Eco actualizado"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== AUDIO ENDPOINTS ====================

@app.get("/api/audio/status")
async def get_audio_status():
    """Obtener estado del servicio de audio"""
    if not AUDIO_SERVICE_AVAILABLE or not audio_service:
        return {
            "enabled": False,
            "available": False,
            "message": "Servicio de audio no disponible"
        }
    
    return {
        "enabled": audio_service.config.get("enabled", False),
        "available": audio_service.audio_enabled,
        "active_alarms": audio_service.get_all_active_alarms(),
        "volume_mode": "night" if audio_service._get_current_volume() < 0.7 else "day",
        "current_volume": audio_service._get_current_volume()
    }

@app.get("/api/audio/config")
async def get_audio_config():
    """Obtener configuración del servicio de audio"""
    if not AUDIO_SERVICE_AVAILABLE or not audio_service:
        return {"config": {}}
    
    return {"config": audio_service.config}

@app.put("/api/audio/config")
async def update_audio_config(config: dict):
    """Actualizar configuración del servicio de audio"""
    if not AUDIO_SERVICE_AVAILABLE or not audio_service:
        raise HTTPException(status_code=503, detail="Servicio de audio no disponible")
    
    try:
        # Actualizar configuración completa
        audio_service.config = config
        
        # Guardar configuración
        audio_service._save_config()
        
        # Broadcast actualización
        await manager.broadcast({
            'type': 'audio_config_updated',
            'data': audio_service.config
        })
        
        return {"success": True, "message": "Configuración de audio actualizada"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/audio/alarms")
async def get_active_audio_alarms():
    """Obtener todas las alarmas sonoras activas"""
    if not AUDIO_SERVICE_AVAILABLE or not audio_service:
        return {"alarms": {}}
    
    return {"alarms": audio_service.get_all_active_alarms()}

@app.post("/api/audio/test/{phase}")
async def test_audio_phase(phase: str):
    """Probar sonido de una fase específica"""
    if not AUDIO_SERVICE_AVAILABLE or not audio_service:
        raise HTTPException(status_code=503, detail="Servicio de audio no disponible")
    
    try:
        from backend.utils.audio_service import AlertPhase
        
        # Mapear string a enum
        phase_map = {
            "friendly": AlertPhase.FRIENDLY,
            "moderate": AlertPhase.MODERATE,
            "critical": AlertPhase.CRITICAL
        }
        
        if phase not in phase_map:
            raise ValueError(f"Fase inválida: {phase}")
        
        # Reproducir sonido de prueba
        await audio_service._play_phase_sound(phase_map[phase])
        
        return {
            "success": True,
            "message": f"Sonido de fase {phase} reproducido",
            "phase": phase
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/audio/alarm/stop/{zone_id}")
async def stop_audio_alarm(zone_id: str):
    """Detener alarma sonora de una zona específica"""
    if not AUDIO_SERVICE_AVAILABLE or not audio_service:
        raise HTTPException(status_code=503, detail="Servicio de audio no disponible")
    
    await audio_service.stop_alarm(zone_id)
    
    return {"success": True, "message": f"Alarma sonora detenida para zona {zone_id}"}

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

@app.post("/api/cameras/{camera_id}/reconnect")
async def reconnect_camera(camera_id: str):
    """Forzar reconexión de una cámara"""
    if not camera_manager:
        raise HTTPException(status_code=503, detail="CameraManager no disponible")
    
    if camera_id not in camera_manager.configs:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    try:
        logger.info(f"Forzando reconexión de cámara {camera_id}")
        
        # Detener la cámara si está corriendo
        if camera_id in camera_manager.cameras:
            camera_manager.stop_camera(camera_id)
            await asyncio.sleep(0.5)  # Breve pausa para asegurar limpieza
        
        # Reiniciar si está habilitada
        if camera_manager.configs[camera_id].enabled:
            camera_manager.start_camera(camera_id)
            
            # Esperar un momento para verificar conexión
            await asyncio.sleep(2)
            
            # Verificar estado
            status = camera_manager.get_camera_status()
            camera_status = status.get(camera_id, {})
            
            if camera_status.get('connected'):
                return {
                    "success": True,
                    "message": f"Cámara {camera_id} reconectada exitosamente",
                    "status": camera_status
                }
            else:
                return {
                    "success": False,
                    "message": f"Reconexión iniciada pero cámara aún no conectada",
                    "status": camera_status
                }
        else:
            return {
                "success": False,
                "message": "La cámara está deshabilitada"
            }
            
    except Exception as e:
        logger.error(f"Error reconectando cámara: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/api/cameras/{camera_id}/stream.mjpeg")
async def get_camera_mjpeg_stream(camera_id: str):
    """Stream MJPEG de una cámara (fallback para WebSocket)"""
    if not camera_manager or camera_id not in camera_manager.cameras:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    
    camera = camera_manager.cameras[camera_id]
    
    async def generate():
        """Generador de frames MJPEG"""
        while True:
            frame = camera.get_frame()
            if frame is not None:
                # Codificar frame como JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                
                # Formato MJPEG
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + 
                       buffer.tobytes() + 
                       b'\r\n')
            
            await asyncio.sleep(0.033)  # ~30 FPS
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

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

@app.websocket("/ws/camera/{camera_id}")
async def camera_stream_websocket(websocket: WebSocket, camera_id: str):
    """WebSocket endpoint para streaming de cámara con detecciones YOLO y Modo Eco"""
    await websocket.accept()
    
    if not camera_manager or camera_id not in camera_manager.cameras:
        await websocket.send_json({
            "error": "Cámara no encontrada"
        })
        await websocket.close()
        return
    
    camera = camera_manager.cameras[camera_id]
    logger.info(f"Cliente conectado al stream de {camera_id}")
    
    # Configuración de detección base
    enable_detection = True
    last_detection_time = 0
    
    try:
        while True:
            # Obtener frame de la cámara
            frame = camera.get_frame()
            
            if frame is not None:
                # Procesar frame con Modo Eco
                eco_config = None
                if eco_manager:
                    try:
                        # Obtener configuración actual del Modo Eco
                        eco_config = eco_manager.get_current_config()
                        detection_interval = eco_manager.get_detection_interval()
                        frame_delay = eco_manager.get_frame_delay()
                        jpeg_quality = eco_config.get('jpeg_quality', 60)
                        
                        # Si estamos en IDLE, verificar movimiento en cada frame
                        if eco_manager.current_state == SystemState.IDLE:
                            # La detección de movimiento se hace internamente en detect_motion
                            # y cambia el estado automáticamente si detecta algo
                            eco_manager.detect_motion(frame)
                        
                        # Procesar frame según configuración del estado actual
                        frame, _ = eco_manager.process_frame(frame)
                        
                    except Exception as e:
                        logger.error(f"Error en Modo Eco: {e}")
                        # Fallback a configuración por defecto
                        detection_interval = 2.0
                        frame_delay = 0.066  # ~15 FPS
                        jpeg_quality = 60
                else:
                    # Fallback si no hay eco manager
                    detection_interval = DETECTION_CONFIG.get('interval', 2.0)
                    frame_delay = 1.0 / DETECTION_CONFIG.get('max_fps', 15)
                    jpeg_quality = DETECTION_CONFIG.get('jpeg_quality', 60)
                
                current_time = asyncio.get_event_loop().time()
                detections = []
                
                # Ejecutar detección YOLO según Modo Eco
                should_detect = eco_manager and eco_manager.should_run_detection()
                
                if enable_detection and model and should_detect and (current_time - last_detection_time) > detection_interval:
                    try:
                        # Ejecutar predicción con umbral de confianza configurable
                        confidence_threshold = getattr(alert_manager, 'config', {}).get('confidence_threshold', 0.75)
                        results = model.predict(frame, conf=confidence_threshold, iou=0.5, verbose=False)
                        
                        # Procesar detecciones
                        if len(results) > 0 and results[0].boxes is not None:
                            for i, box in enumerate(results[0].boxes):
                                # Asignar door_id basado en la zona de la cámara
                                zone_id = camera.config.zone_id or f"cam_{camera_id}"
                                door_id = f"{zone_id}_door_{i}"
                                
                                detection = {
                                    'class_name': model.names[int(box.cls)],
                                    'confidence': float(box.conf),
                                    'bbox': {
                                        'x1': int(box.xyxy[0][0]),
                                        'y1': int(box.xyxy[0][1]),
                                        'x2': int(box.xyxy[0][2]),
                                        'y2': int(box.xyxy[0][3])
                                    },
                                    'door_id': door_id
                                }
                                detections.append(detection)
                        
                        # Procesar con DetectionManager para deduplicar
                        if detection_manager and alert_manager:
                            actions = detection_manager.process_frame_detections(detections, camera_id)
                            
                            # Ejecutar acciones necesarias
                            for action in actions:
                                if action['action'] == 'create_alert':
                                    # Crear nueva alerta
                                    await alert_manager.process_detection(
                                        [action['detection']], 
                                        camera_id=camera_id
                                    )
                                    logger.info(f"Alerta creada para {action['zone_id']}")
                                    
                                    # NO enviar alerta inmediata - solo cuando expire el timer
                                    # if telegram_service.enabled:
                                    #     zone_name = alert_manager.config['zones'].get(action['zone_id'], {}).get('name', action['zone_id'])
                                    #     await telegram_service.send_alert(
                                    #         zone_id=action['zone_id'],
                                    #         zone_name=zone_name,
                                    #         detection_type='puerta_abierta',
                                    #         image=frame
                                    #     )
                                        
                                elif action['action'] == 'cancel_alert':
                                    # Cancelar alerta existente
                                    zone_id = action['zone_id']
                                    # Buscar TODOS los timers activos
                                    active_timers = alert_manager.get_active_timers()
                                    timers_to_cancel = []
                                    
                                    # Buscar timers que coincidan con la zona/cámara
                                    for timer in active_timers:
                                        timer_door_id = timer.get('door_id', '')
                                        timer_camera_id = timer.get('camera_id', '')
                                        
                                        # Cancelar si:
                                        # 1. El door_id coincide exactamente
                                        # 2. Es de la misma cámara
                                        # 3. El door_id contiene el zone_id
                                        if (timer_door_id == zone_id or 
                                            timer_camera_id == camera_id or
                                            zone_id in timer_door_id or
                                            timer_door_id in zone_id):
                                            timers_to_cancel.append(timer_door_id)
                                    
                                    # Cancelar todos los timers encontrados
                                    for door_id in timers_to_cancel:
                                        alert_manager.acknowledge_alarm(door_id)
                                        logger.info(f"Alerta cancelada para {door_id}")
                                    
                                    # Si no se encontraron timers específicos, limpiar todos de esta cámara
                                    if not timers_to_cancel:
                                        logger.warning(f"No se encontraron timers para {zone_id}, limpiando todos de cámara {camera_id}")
                                        for timer in active_timers:
                                            if timer.get('camera_id') == camera_id:
                                                alert_manager.acknowledge_alarm(timer['door_id'])
                                                logger.info(f"Alerta cancelada para {timer['door_id']} (limpieza por cámara)")
                                    
                                    # Enviar notificación a Telegram de puerta cerrada (sin imagen)
                                    if telegram_service.enabled and (timers_to_cancel or not active_timers):
                                        zone_name = alert_manager.config['zones'].get(zone_id, {}).get('name', zone_id)
                                        await telegram_service.send_alert(
                                            zone_id=zone_id,
                                            zone_name=zone_name,
                                            detection_type='puerta_cerrada'
                                            # NO incluir imagen en cierre
                                        )
                        
                        # Actualizar estado del Modo Eco
                        if eco_manager:
                            door_open_detected = any(d['class_name'] == 'gate_open' for d in detections)
                            eco_manager.update_state(detection_found=door_open_detected)
                        
                        last_detection_time = current_time
                        
                    except Exception as e:
                        logger.error(f"Error en detección YOLO: {e}")
                
                # Dibujar detecciones en el frame
                if detections:
                    for det in detections:
                        bbox = det['bbox']
                        color = (0, 255, 0) if det['class_name'] == 'gate_closed' else (0, 0, 255)
                        
                        # Dibujar bounding box
                        cv2.rectangle(frame, 
                                    (bbox['x1'], bbox['y1']), 
                                    (bbox['x2'], bbox['y2']), 
                                    color, 2)
                        
                        # Dibujar etiqueta
                        label = f"{det['class_name']} {det['confidence']:.2f}"
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                        
                        # Fondo para el texto
                        cv2.rectangle(frame,
                                    (bbox['x1'], bbox['y1'] - label_size[1] - 4),
                                    (bbox['x1'] + label_size[0], bbox['y1']),
                                    color, -1)
                        
                        # Texto
                        cv2.putText(frame, label,
                                  (bbox['x1'], bbox['y1'] - 2),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Comprimir frame a JPEG con calidad según Modo Eco
                encode_param = [cv2.IMWRITE_JPEG_QUALITY, int(jpeg_quality)]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                # Crear mensaje con metadata
                metadata = {
                    "type": "frame",
                    "timestamp": datetime.now().isoformat(),
                    "detections": detections,
                    "frame_size": len(buffer),
                    "zones": detection_manager.get_zone_states() if detection_manager else {},
                    "eco_mode": eco_manager.get_status() if eco_manager else None
                }
                
                # Protocolo: enviar metadata + frame en un solo mensaje binario
                # Formato: [metadata_length(4 bytes)][metadata_json][frame_jpeg]
                metadata_json = json.dumps(metadata).encode('utf-8')
                metadata_length = len(metadata_json).to_bytes(4, byteorder='big')
                
                # Combinar todo en un solo mensaje
                full_message = metadata_length + metadata_json + buffer.tobytes()
                
                # Enviar mensaje completo
                await websocket.send_bytes(full_message)
                
                # Control de FPS según Modo Eco
                await asyncio.sleep(frame_delay)
            else:
                # Si no hay frame, esperar un poco
                await asyncio.sleep(0.1)
                
    except WebSocketDisconnect:
        logger.info(f"Cliente desconectado del stream de {camera_id}")
    except Exception as e:
        logger.error(f"Error en stream de {camera_id}: {e}")
        try:
            await websocket.close()
        except:
            pass

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
