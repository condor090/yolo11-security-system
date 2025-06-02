# 🎥 GUÍA PASO A PASO: Agregar Cámara Hikvision Real

## 📋 ANTES DE EMPEZAR

### Necesitará esta información de su cámara:
- **IP de la cámara** (ejemplo: 192.168.1.108)
- **Usuario** (generalmente: admin)
- **Contraseña** (la que configuró al instalar)
- **Modelo** (opcional, para referencia)

### Cómo obtener la IP de su cámara:
1. **Opción 1 - SADP Tool** (Recomendado):
   - Descargar de Hikvision.com
   - Ejecutar y escanear red
   - Mostrará todas las cámaras Hikvision

2. **Opción 2 - Router**:
   - Acceder a su router
   - Ver dispositivos conectados
   - Buscar "Hikvision" o "HIK"

3. **Opción 3 - Software de la cámara**:
   - iVMS-4200 o Hik-Connect
   - Ver propiedades del dispositivo

## 🚀 PASOS PARA AGREGAR LA CÁMARA

### Paso 1: Abrir el Dashboard
```bash
# Asegurarse que el sistema está corriendo
# Abrir navegador en:
http://localhost:3000
```

### Paso 2: Ir a Configuración de Cámaras
1. Click en tab **"Configuración"** (último tab)
2. Seleccionar sub-tab **"Cámaras"**
3. Click en botón **"+ Agregar Cámara"**

### Paso 3: Completar el Formulario

📝 **Ejemplo con valores reales:**

| Campo | Valor a Ingresar | Notas |
|-------|------------------|-------|
| **ID** | cam_001 | Se genera automático |
| **Nombre** | Entrada Principal | Nombre descriptivo |
| **IP** | 192.168.1.108 | IP de SU cámara |
| **Puerto** | 554 | Dejar por defecto |
| **Usuario** | admin | Usuario de la cámara |
| **Contraseña** | Su_Password_123 | Contraseña real |
| **Canal** | 1 | Primera cámara = 1 |
| **Stream** | Principal (main) | Para alta calidad |
| **Zona** | door_1 | O seleccionar apropiada |
| ✅ **Habilitada** | Marcado | Para activar |

### Paso 4: Probar Conexión (Recomendado)
1. Antes de guardar, click en **"🔌 Probar Conexión"**
2. Esperar resultado:
   - ✅ **"Conexión exitosa"** → Continuar al paso 5
   - ❌ **"No se pudo conectar"** → Verificar datos

### Paso 5: Guardar Cámara
1. Click en **"Guardar Cámara"**
2. La cámara aparecerá en la lista
3. Verificar estado:
   - 🟢 **Online** = Funcionando
   - 🔴 **Offline** = Revisar conexión

## 🔍 VERIFICAR FUNCIONAMIENTO

### 1. En la Lista de Cámaras
Debería ver algo así:
```
┌─────────────────────────────────────┐
│ 🎥 Entrada Principal                │
│ IP: 192.168.1.108 • 🟢 Online      │
│ Usuario: admin                      │
│ Zona: door_1                        │
│ FPS: 25 • Frames: 1,234            │
└─────────────────────────────────────┘
```

### 2. En el Monitor (Tab Monitor)
- Al detectar puerta abierta
- Aparecerá botón **"Ver Video Contextual"**
- Mostrará video de esa cámara

### 3. Probar URL RTSP Externa
La URL generada es:
```
rtsp://admin:Su_Password_123@192.168.1.108:554/Streaming/Channels/101
```

Puede probarla en:
- **VLC**: Media → Abrir ubicación de red
- **ffplay**: `ffplay rtsp://...`

## 🛠️ SOLUCIÓN DE PROBLEMAS

### ❌ "No se pudo conectar"

1. **Verificar IP**:
   ```bash
   ping 192.168.1.108
   ```
   Debe responder

2. **Verificar puerto 554**:
   ```bash
   telnet 192.168.1.108 554
   ```
   Debe conectar

3. **Verificar credenciales**:
   - Probar en navegador: http://192.168.1.108
   - Login con mismo usuario/password

4. **Verificar firewall**:
   - Cámara y computadora en misma red
   - Sin bloqueos de firewall

### ❌ "Error de autenticación"
- Verificar usuario/contraseña
- Algunos modelos usan "admin/12345" por defecto
- Revisar manual del modelo

### ❌ "Stream no disponible"
- Cambiar de "main" a "sub" stream
- Algunos modelos antiguos usan URLs diferentes

## 📊 URLS RTSP COMUNES HIKVISION

### Modelos Nuevos (2016+):
```
rtsp://user:pass@ip:554/Streaming/Channels/101   # Main stream
rtsp://user:pass@ip:554/Streaming/Channels/102   # Sub stream
```

### Modelos Antiguos:
```
rtsp://user:pass@ip:554/h264/ch1/main/av_stream  # Main
rtsp://user:pass@ip:554/h264/ch1/sub/av_stream   # Sub
```

### NVR (Grabadores):
```
rtsp://user:pass@ip:554/Streaming/Channels/201   # Cámara 2, stream 1
rtsp://user:pass@ip:554/Streaming/Channels/301   # Cámara 3, stream 1
```

## ✅ SIGUIENTE PASO

Una vez agregada la primera cámara exitosamente:

1. **Agregar más cámaras** repitiendo el proceso
2. **Configurar zonas** en Tab Temporizadores
3. **Ajustar delays** según necesidad operativa
4. **Probar detección** subiendo imagen de prueba

## 💡 TIPS PRO

1. **Nombres descriptivos**: "Entrada Principal" mejor que "Cam1"
2. **Documentar IPs**: Mantener lista de IP por ubicación
3. **Passwords seguros**: No usar defaults
4. **Sub-stream para preview**: Menor ancho de banda
5. **Main-stream para grabación**: Mejor calidad

## 📞 SOPORTE RÁPIDO

Si algo no funciona:
1. Verificar que puede acceder a la cámara desde navegador
2. Revisar logs del backend en la terminal
3. Probar URL RTSP en VLC primero
4. Verificar que no hay VPN activa

---

**¡LISTO!** Con estos pasos debería tener su primera cámara Hikvision funcionando en el sistema.

🦅 *"La tecnología compleja se vuelve simple cuando se presenta paso a paso"*
