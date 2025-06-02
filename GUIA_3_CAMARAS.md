# 📹 GUÍA: Configurar las 3 Cámaras Hikvision

## ✅ Cámaras Detectadas

| IP | Estado RTSP | Web | Acceso |
|---|---|---|---|
| 192.168.1.11 | ✅ Puerto 554 abierto | ✅ Puerto 80 | http://192.168.1.11 |
| 192.168.1.12 | ✅ Puerto 554 abierto | ✅ Puerto 80 | http://192.168.1.12 |
| 192.168.1.39 | ✅ Puerto 554 abierto | ✅ Puerto 80 | http://192.168.1.39 |

## 🚀 PASOS PARA CONFIGURAR TODAS

### Paso 1: Obtener Credenciales de Cada Cámara

Para cada cámara, necesita:

1. **Abrir en navegador**:
   - http://192.168.1.11
   - http://192.168.1.12
   - http://192.168.1.39

2. **Intentar login con**:
   - admin / Mayocabo1 (si todas usan la misma)
   - admin / 12345
   - admin / admin
   - admin / (contraseña en etiqueta de la cámara)

3. **Una vez dentro, verificar**:
   - Configuration → Network → Advanced → RTSP
   - Anotar si hay alguna URL RTSP específica
   - Verificar tipo de autenticación

### Paso 2: Configurar RTSP en Cada Cámara

**IMPORTANTE**: En cada cámara, ir a la configuración RTSP y:

1. ✅ **Habilitar RTSP** (si no está habilitado)
2. ✅ **Authentication**: Cambiar a "basic" o "digest/basic"
3. ✅ **Puerto**: Confirmar 554
4. ✅ **Guardar** y reiniciar si lo pide

### Paso 3: Agregar al Dashboard

#### Opción A: Usar el Escáner (Recomendado)
1. En el dashboard: **Configuración → Cámaras**
2. Click **"🔍 Buscar Cámaras"**
3. Aparecerán las 3 cámaras
4. Para cada una:
   - Click **"Usar"**
   - Completar nombre descriptivo
   - Ingresar usuario/contraseña
   - Asignar zona
   - Guardar

#### Opción B: Agregar Manualmente
1. Click **"+ Agregar Manual"**
2. Para cada cámara:
   ```
   Cámara 1:
   - Nombre: Entrada Principal (o el que prefiera)
   - IP: 192.168.1.11
   - Puerto: 554
   - Usuario: admin
   - Contraseña: (la que encontró)
   - Canal: 1
   - Stream: main
   - Zona: door_1
   
   Cámara 2:
   - Nombre: Zona de Carga
   - IP: 192.168.1.12
   - (resto igual, ajustando zona)
   
   Cámara 3:
   - Nombre: Estacionamiento
   - IP: 192.168.1.39
   - (resto igual, ajustando zona)
   ```

### Paso 4: Probar Conexiones

Para cada cámara agregada:
1. Click en **"🔌 Probar Conexión"**
2. Debe mostrar "Conexión exitosa"
3. El estado cambiará a 🟢 Online

## 🔧 SOLUCIÓN DE PROBLEMAS

### Si alguna cámara no conecta:

1. **Verificar en VLC primero**:
   ```
   rtsp://admin:[contraseña]@[IP]:554/Streaming/Channels/101
   ```

2. **Si es modelo antiguo, probar**:
   ```
   rtsp://admin:[contraseña]@[IP]:554/h264/ch1/main/av_stream
   ```

3. **Cambiar stream**:
   - De "main" a "sub" en el dashboard
   - Esto usa canal 102 en vez de 101

### Configuración por Zonas Sugerida:

| Cámara | IP | Zona Sugerida | Delay |
|--------|-----|---------------|-------|
| 1 | 192.168.1.11 | door_1 (Entrada Principal) | 30s |
| 2 | 192.168.1.12 | loading (Zona de Carga) | 300s |
| 3 | 192.168.1.39 | parking (Estacionamiento) | 120s |

## 📊 RESULTADO ESPERADO

Una vez configuradas correctamente:
- 3 cámaras mostrando 🟢 Online
- FPS activo en cada una
- En Monitor: al detectar puerta abierta, botón "Ver Video Contextual"
- Video de la cámara correcta según la zona

## 💡 TIPS

1. **Si todas usan la misma contraseña**, configura una y luego copia los datos
2. **Nombra las cámaras** según su ubicación física
3. **Asigna zonas correctas** para que el video contextual funcione bien
4. **Los delays** se pueden ajustar en Configuración → Temporizadores

---

¿Necesita ayuda con alguna cámara específica? 🦅
