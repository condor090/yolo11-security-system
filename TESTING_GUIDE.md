# 🎯 GUÍA DE PRUEBAS - SISTEMA YOLO11 SECURITY

## 🚀 INICIO RÁPIDO

### 1. Verificar Estado del Sistema
```bash
cd /Users/Shared/yolo11_project
python3 test_system.py
```

### 2. Iniciar Backend (Terminal 1)
```bash
cd /Users/Shared/yolo11_project
python3 backend/main.py
```

### 3. Iniciar Frontend (Terminal 2)
```bash
cd /Users/Shared/yolo11_project/frontend
npm start
```

### 4. Abrir Dashboard
- Navegador: http://localhost:3000
- Backend API: http://localhost:8888
- WebSocket: ws://localhost:8888/ws

## 🧪 PRUEBAS DISPONIBLES

### Test 1: Verificación Básica
```bash
python3 test_system.py
```
Verifica:
- ✅ Backend activo
- ✅ Cámaras configuradas
- ✅ Frontend activo
- ✅ Configuraciones

### Test 2: Simulador de Eventos
```bash
python3 simulate_events.py
```
Simula:
- 🚪 Puertas abiertas/cerradas
- ⏱️ Diferentes duraciones
- 🚨 Activación de alarmas

### Test 3: Cámaras
```bash
python3 test_camera_integration.py
```
Verifica:
- 📹 Configuración de cámaras
- 🔗 URLs RTSP generadas
- 📊 Estado del sistema

## 📱 USO DEL DASHBOARD

### Tab: Dashboard
- KPIs en tiempo real
- Gráficos de actividad
- Eventos recientes
- Estado general

### Tab: Monitor
- **Temporizadores activos** con cuenta regresiva
- **Botón "Ver Video Contextual"** en cada timer
- **Botón "Vista Directa"** para ver todas las cámaras
- Estados: Normal → Alerta → Alarma

### Tab: Análisis
- Subir imagen para análisis
- Detectar puertas abiertas/cerradas
- Ajustar umbral de confianza
- Descargar resultados

### Tab: Configuración
- Delays por zona
- Notificaciones
- Ajustes del sistema

## 🎬 FLUJO DE PRUEBA COMPLETO

1. **Iniciar Sistema**
   - Backend → Frontend → Dashboard

2. **Simular Eventos**
   ```bash
   python3 simulate_events.py
   ```

3. **Observar en Dashboard**
   - Tab Monitor: Ver temporizadores aparecer
   - Cuenta regresiva en tiempo real
   - Alarmas activarse después del delay

4. **Probar Video Contextual**
   - Click en "Ver Video Contextual"
   - Ver timeline ±30 segundos
   - Controles de reproducción

5. **Vista Directa**
   - Click en "Vista Directa"
   - Ver grid de cámaras
   - Estados en tiempo real

## 🔧 CONFIGURACIÓN DE CÁMARAS REALES

1. Editar `cameras/camera_config.json`:
```json
{
  "cam_001": {
    "ip": "192.168.1.100",  // IP real
    "username": "admin",     // Usuario real
    "password": "password",  // Password real
    ...
  }
}
```

2. Probar conexión RTSP:
```bash
ffmpeg -i rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101 -f null -
```

3. Reiniciar backend para aplicar cambios

## 📊 MONITOREO

### Logs Backend
- Conexiones WebSocket
- Detecciones procesadas
- Estados de cámaras
- Temporizadores activos

### Logs Frontend
- Consola del navegador (F12)
- Mensajes WebSocket
- Estados de componentes

## 🐛 SOLUCIÓN DE PROBLEMAS

### Puerto 8888 ocupado
```bash
lsof -i :8888
kill -9 [PID]
```

### Frontend no inicia
```bash
cd frontend
npm install
npm start
```

### Cámaras no conectan
- Verificar IPs y credenciales
- Probar con VLC: Media → Open Network Stream
- Verificar firewall/red

## 🎯 CASOS DE USO

1. **Operador de Seguridad**
   - Monitor en pantalla grande
   - Reaccionar a alarmas
   - Ver video contextual

2. **Supervisor**
   - Dashboard con métricas
   - Análisis de patrones
   - Configuración de delays

3. **Testing**
   - Simular eventos
   - Verificar respuestas
   - Ajustar parámetros

---

**¡Sistema listo para pruebas!** 🚀
