## 🔧 SOLUCIÓN: Cámara Sin Conexión

### 📊 Diagnóstico Actual

La cámara **192.168.1.11** está:
- ✅ **Respondiendo al ping** - La cámara está en la red
- ✅ **Puerto 554 abierto** - RTSP está activo
- ✅ **HTTP en puerto 80** - Interfaz web disponible
- ❌ **Error 401** - Credenciales incorrectas

### 🔑 El Problema: Credenciales

La cámara está rechazando la conexión porque:
1. El usuario/contraseña no son correctos
2. La cámara puede requerir activación inicial
3. Las credenciales por defecto fueron cambiadas

### ✅ SOLUCIONES

#### Opción 1: Acceder a la Interfaz Web (Recomendado)

1. **Abrir navegador y visitar:**
   ```
   http://192.168.1.11
   ```

2. **Buscar las credenciales:**
   - En la etiqueta de la cámara
   - En el manual
   - Credenciales comunes:
     - admin / 12345
     - admin / admin
     - admin / password
     - admin / (contraseña en la etiqueta)

3. **Si es primera vez:**
   - Puede pedir activar la cámara
   - Crear nueva contraseña

#### Opción 2: Probar en VLC Primero

1. **Abrir VLC**
2. **Media → Abrir ubicación de red**
3. **Probar estas URLs con diferentes contraseñas:**
   ```
   rtsp://admin:12345@192.168.1.11:554/Streaming/Channels/101
   rtsp://admin:admin@192.168.1.11:554/Streaming/Channels/101
   rtsp://admin:password@192.168.1.11:554/Streaming/Channels/101
   ```

4. **Si funciona en VLC, usar esas credenciales en el dashboard**

#### Opción 3: Reset de Fábrica (Último Recurso)

Si no recuerda las credenciales:
1. Localizar botón reset en la cámara
2. Mantener presionado 10-15 segundos con cámara encendida
3. Esperar reinicio
4. Credenciales volverán a las de fábrica

### 🔄 Una Vez Tenga las Credenciales Correctas

1. **En el Dashboard:**
   - Click en ✏️ Editar en la cámara
   - Actualizar usuario y contraseña
   - Guardar cambios

2. **Click en 🔌 Probar Conexión**
   - Debería mostrar "Conexión exitosa"

3. **El estado cambiará a:**
   - 🟢 Online
   - FPS activo
   - Sin errores

### 💡 TIPS IMPORTANTES

1. **Hikvision nuevas (2016+):**
   - Requieren activación por web primera vez
   - No aceptan contraseñas simples
   - Usuario siempre es "admin"

2. **URLs RTSP varían por modelo:**
   - Nuevas: `/Streaming/Channels/101`
   - Antiguas: `/h264/ch1/main/av_stream`
   - NVR: `/Streaming/Channels/201` (cámara 2)

3. **Si sigue sin funcionar:**
   - Verificar firewall de Windows/Mac
   - Confirmar misma red (sin VLAN)
   - Deshabilitar VPN si está activa

### 🚀 ACCIÓN INMEDIATA

1. **Abra:** http://192.168.1.11
2. **Obtenga las credenciales correctas**
3. **Actualice en el dashboard**
4. **¡Listo!**

La cámara está funcionando perfectamente, solo necesita las credenciales correctas.
