# 📋 CHECKLIST: Configuración RTSP en Cámara Hikvision

## 🔍 Qué Buscar en la Interfaz Web

### 1️⃣ **Ubicación del RTSP** (varía por modelo)
- **Configuration → Network → Advanced Settings → RTSP**
- **Configuration → Network → Advanced → Integration Protocol**
- **Settings → Network → Advanced → Platform Access**

### 2️⃣ **Configuraciones Importantes**

#### ✅ **RTSP Authentication**
- [ ] Cambiar de "digest" a "digest/basic" o "basic"
- [ ] O probar "disable" temporalmente para test

#### ✅ **RTSP Port**
- [ ] Verificar que sea 554
- [ ] Si es diferente, anotar el puerto

#### ✅ **Enable RTSP**
- [ ] Asegurarse que esté habilitado/checked

### 3️⃣ **Mientras Está Ahí, Anote:**

#### 📝 **URL RTSP Exacta**
Algunas cámaras muestran la URL exacta:
- Puede aparecer como "RTSP URL" o "Stream URL"
- Ejemplo: `rtsp://[IP]:[PORT]/Streaming/Channels/101`

#### 📝 **Modelo de Cámara**
- Usualmente en: System → Device Info
- O en la parte superior de la interfaz

### 4️⃣ **Si Encuentra "ONVIF"**
- [ ] Habilitar ONVIF
- [ ] Crear usuario ONVIF si lo pide
- [ ] Anotar puerto ONVIF (usually 80)

### 5️⃣ **Posibles Problemas/Soluciones**

#### ❌ **Si no encuentra RTSP**
- Buscar "Streaming" o "Protocol"
- Puede estar bajo "Integration" o "Platform"

#### ❌ **Si pide activar licencia**
- Algunas funciones requieren activación
- Seguir el proceso de activación

#### ❌ **Si hay múltiples streams**
- Main Stream (101): Alta calidad
- Sub Stream (102): Baja calidad
- Third Stream (103): Móvil

### 📸 **Tips**
1. **Tome screenshots** de la configuración RTSP
2. **Anote cualquier URL** que muestre
3. **Si hay ejemplos**, copiarlos

### 🔄 **Después de Cambiar**
1. **Guardar/Save** la configuración
2. Algunos modelos requieren **reboot**
3. Esperar 1-2 minutos

---

**Estaré aquí esperando los resultados para ayudarle con la configuración correcta** 🦅
