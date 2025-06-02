# 🔧 SOLUCIÓN: Error de Conexión RTSP

## 📊 Diagnóstico

La cámara **192.168.1.11** está rechazando la conexión RTSP con error 401 (No autorizado), a pesar de tener las credenciales correctas.

### 🔍 Problema Identificado

1. **URL RTSP generada**: `rtsp://admin:Mayocabo1@192.168.1.11:554/Streaming/Channels/100`
2. **Error**: 401 Unauthorized
3. **Causa probable**: 
   - La cámara puede usar autenticación **digest** en lugar de **basic**
   - El formato de URL puede ser diferente
   - La cámara puede requerir configuración adicional

## ✅ SOLUCIONES

### Solución 1: Verificar en VLC (Recomendado)

1. **Abrir VLC**
2. **Media → Abrir ubicación de red**
3. **Probar estas URLs:**
   ```
   rtsp://admin:Mayocabo1@192.168.1.11:554/Streaming/Channels/101
   rtsp://admin:Mayocabo1@192.168.1.11:554/Streaming/Channels/1
   rtsp://admin:Mayocabo1@192.168.1.11:554/h264/ch1/main/av_stream
   rtsp://192.168.1.11:554/Streaming/Channels/101
   ```
4. **Si VLC pide credenciales**, ingrese:
   - Usuario: admin
   - Contraseña: Mayocabo1

### Solución 2: Verificar Configuración en la Cámara

1. **Acceder a**: http://192.168.1.11
2. **Login con**: admin / Mayocabo1
3. **Buscar en el menú**:
   - Configuration → Network → Advanced → RTSP
   - O similar según el modelo
4. **Verificar**:
   - Autenticación RTSP habilitada
   - Tipo de autenticación (basic/digest)
   - URL RTSP exacta

### Solución 3: Habilitar RTSP en la Cámara

Es posible que RTSP esté deshabilitado o requiera activación:

1. **En la interfaz web de la cámara**:
   - Configuration → Network → Advanced Settings
   - Buscar "RTSP" o "Streaming"
   - Habilitar RTSP
   - Verificar puerto (554)
   - Tipo de autenticación: probar "basic" o "digest/basic"

### Solución 4: Usar ONVIF

Si la cámara soporta ONVIF:
1. Habilitar ONVIF en la cámara
2. La URL podría ser:
   ```
   rtsp://admin:Mayocabo1@192.168.1.11:554/onvif1
   ```

## 🛠️ SOLUCIÓN TEMPORAL

Mientras resolvemos el RTSP, puede:

1. **Usar el stream HTTP** (si está disponible):
   - Algunas cámaras Hikvision ofrecen stream por HTTP
   - Verificar en la interfaz web

2. **Cambiar el tipo de stream**:
   - En el dashboard, editar la cámara
   - Cambiar de "main" a "sub"
   - Esto usa `/Streaming/Channels/102`

## 📝 INFORMACIÓN ADICIONAL NECESARIA

Para ayudarle mejor, necesitaría saber:

1. **¿Puede ver el video en VLC?**
2. **¿Qué modelo exacto de cámara Hikvision es?**
3. **¿En la interfaz web, puede ver el video en vivo?**

## 💡 NOTA IMPORTANTE

El problema NO es del sistema, sino de la configuración RTSP de la cámara. Una vez que funcione en VLC, funcionará en el sistema.

**Siguiente paso**: Probar en VLC para confirmar la URL correcta.
