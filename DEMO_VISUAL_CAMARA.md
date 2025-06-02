# 🎬 DEMO VISUAL: Agregar Cámara Hikvision

## 🔍 Paso 1: Encontrar la IP de su Cámara

### Opción A: Usar nuestro escáner
```bash
cd /Users/Shared/yolo11_project
python3 find_cameras.py
```

**Verá algo como:**
```
🔍 ESCÁNER DE CÁMARAS HIKVISION
==================================================
📡 Escaneando red: 192.168.1.0/24
📊 Total de IPs a escanear: 254

⏳ Esto puede tomar 1-2 minutos...

✅ Cámara Hikvision encontrada: 192.168.1.108
✅ Cámara Hikvision encontrada: 192.168.1.109

==================================================
🎉 RESUMEN: 2 dispositivo(s) encontrado(s)

1. IP: 192.168.1.108
   Puerto RTSP: 554
   Puerto HTTP: 80
   Web: http://192.168.1.108:80
   ✅ Confirmado: HIKVISION
```

### Opción B: Usar SADP Tool de Hikvision
![SADP Tool](https://www.hikvision.com/en/support/tools/hitools/sadp-for-windows/)

## 🖥️ Paso 2: Abrir el Dashboard

1. **Verificar que el sistema está corriendo:**
   - Terminal 1: Backend debe mostrar "Application startup complete"
   - Terminal 2: Frontend debe mostrar "Compiled successfully!"

2. **Abrir navegador:**
   ```
   http://localhost:3000
   ```

## 📸 Paso 3: Navegar a Configuración de Cámaras

### Vista del Dashboard:
```
┌─────────────────────────────────────────────────┐
│ YOLO11 Security System                          │
├─────────────────────────────────────────────────┤
│ [Dashboard] [Monitor] [Análisis] [Configuración]│
└─────────────────────────────────────────────────┘
                                          ↑
                                    Click aquí
```

### En Configuración:
```
┌─────────────────────────────────────────────────┐
│ [Cámaras] [Temporizadores] [Notificaciones]     │
└─────────────────────────────────────────────────┘
      ↑
 Click aquí
```

## ➕ Paso 4: Agregar Nueva Cámara

### Click en el botón:
```
┌─────────────────────────────────────────────────┐
│ 🎥 Configuración de Cámaras    [+ Agregar Cámara]│
└─────────────────────────────────────────────────┘
                                         ↑
                                   Click aquí
```

## 📝 Paso 5: Completar el Formulario

### Formulario con datos reales:
```
┌─────────────────────────────────────────────────┐
│ 📹 Nueva Cámara                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ ID de Cámara:     [cam_001          ] (auto)   │
│ Nombre:           [Entrada Principal ]          │
│                                                 │
│ Dirección IP:     [192.168.1.108    ]          │
│ Puerto RTSP:      [554              ]          │
│                                                 │
│ Usuario:          [admin            ]          │
│ Contraseña:       [••••••••         ]          │
│                                                 │
│ Canal:            [1 ▼]                        │
│ Calidad Stream:   [Principal (Alta) ▼]         │
│                                                 │
│ Zona Asignada:    [Puerta Principal ▼]         │
│                                                 │
│ ☑ Cámara habilitada                           │
│                                                 │
│ URL RTSP generada:                             │
│ rtsp://admin:****@192.168.1.108:554/...       │
│                                                 │
│        [Cancelar]    [Guardar Cámara]          │
└─────────────────────────────────────────────────┘
```

## ✅ Paso 6: Verificar Funcionamiento

### La cámara aparecerá en la lista:
```
┌─────────────────────────────────────────────────┐
│ 🎥 Entrada Principal                            │
│ IP: 192.168.1.108:554 • 🟢 EN VIVO             │
│ Usuario: admin                                  │
│ Canal/Stream: 1 / main                          │
│ Zona: Puerta Principal (Delay: 30s)            │
│ Estado: Habilitada                              │
│                                                 │
│ [🔌 Probar] [✏️ Editar] [🗑️ Eliminar]           │
│ [📋 Copiar URL RTSP]                            │
│                                                 │
│ ✅ Conectada • FPS: 25                          │
└─────────────────────────────────────────────────┘
```

## 🎯 Paso 7: Probar en el Monitor

1. **Ir a tab Monitor**
2. **Simular detección** (o esperar una real)
3. **Ver el botón nuevo:**

```
┌─────────────────────────────────────────────────┐
│ 🚪 door_1                                       │
│ Tiempo abierto: 0:45                           │
│ ████████████░░░░░░░ 45%                        │
│ Alarma en: 15s                                  │
│                                                 │
│ [🎬 Ver Video Contextual]                       │
│ [✓ Reconocer]                                  │
└─────────────────────────────────────────────────┘
```

## 🎬 Video Contextual en Acción

Al hacer click en "Ver Video Contextual":
```
┌─────────────────────────────────────────────────┐
│ 📹 Entrada Principal                            │
│ Contexto: door_1 • 17:32:45                     │
├─────────────────────────────────────────────────┤
│                                                 │
│         [Vista previa del video]                │
│                                                 │
│ ├──────────┼──────────┤                        │
│ -30s     Evento     +30s                       │
│                                                 │
│ [▶️] [⏸️] [⏮️] [⏭️] [💾] [⛶]                    │
│                                                 │
│ 💡 Sugerencia IA: Verificar si es personal     │
│    autorizado. Patrón: Acceso fuera de horario │
└─────────────────────────────────────────────────┘
```

## 🛠️ Troubleshooting Visual

### Si ve 🔴 Desconectada:
1. **Click en "Probar Conexión"**
2. **Verificar mensaje de error:**
   - "Timeout" → Verificar IP
   - "401 Unauthorized" → Verificar usuario/password
   - "Connection refused" → Verificar puerto

### Probar en VLC:
1. **Copiar URL RTSP** (botón en la cámara)
2. **Abrir VLC**
3. **Media → Abrir ubicación de red**
4. **Pegar URL**
5. **Si funciona en VLC, debe funcionar en el sistema**

## 📱 Resultado Final

Su sistema ahora:
- ✅ Detecta puertas abiertas
- ✅ Muestra video de la cámara correcta
- ✅ Guarda contexto ±30 segundos
- ✅ Todo desde una interfaz web profesional

---

**¡FELICITACIONES!** 🎉

Ha integrado exitosamente su primera cámara Hikvision real al sistema YOLO11 Security.

🦅 *"La seguridad profesional ahora está al alcance de un click"*
