# 🚀 GUÍA RÁPIDA - SISTEMA DE ALERTAS TELEGRAM

## ⚡ Setup Rápido (5 minutos)

### 1. Crear Bot de Telegram
```bash
# En Telegram:
1. Buscar @BotFather
2. Enviar: /newbot
3. Nombre: YOMJAI Alerts
4. Username: yomjai_alerts_bot
5. Copiar el TOKEN
```

### 2. Obtener Chat ID
```bash
# Opción A: Bot @userinfobot
1. Buscar @userinfobot en Telegram
2. Enviar cualquier mensaje
3. Copiar el ID

# Opción B: Crear grupo
1. Crear grupo en Telegram
2. Agregar el bot al grupo
3. Enviar: /my_id al grupo
```

### 3. Configurar YOMJAI
```json
// Editar: alerts/alert_config_v2.json
{
  "telegram": {
    "enabled": true,
    "bot_token": "TU_TOKEN_AQUI",
    "chat_id": "TU_CHAT_ID"
  }
}
```

### 4. Probar
```bash
# Test rápido
curl -X POST http://localhost:8889/api/telegram/test \
  -H "Content-Type: application/json" \
  -d '{
    "bot_token": "TU_TOKEN",
    "chat_id": "TU_CHAT_ID"
  }'
```

---

## 📱 Comportamiento del Sistema

### ✅ Lo que SÍ hace:
- **Espera** que expire el timer antes de alertar
- **Envía imagen** en la primera alerta
- **Repite** mensajes cada X segundos (configurable)
- **Escala** la urgencia: 5s → 10s → 20s → 30s → 60s
- **Actualiza** imagen cada 5 mensajes
- **Cancela** todo al cerrar la puerta

### ❌ Lo que NO hace:
- NO alerta cuando se abre la puerta
- NO spam con imágenes en cada mensaje
- NO continúa después de cerrar
- NO envía a múltiples grupos (por ahora)

---

## ⚙️ Configuración por Zona

```json
// backend/configs/telegram_alert_config.json
{
  "intervals_by_zone": {
    "entrance": 5,      // Entrada: urgente (5s)
    "loading": 30,      // Carga: paciente (30s)
    "emergency": 3,     // Emergencia: crítico (3s)
    "warehouse": 60     // Almacén: relajado (60s)
  }
}
```

---

## 🎯 Casos de Uso

### 1. Entrada Principal (Alta Prioridad)
- Timer: 15 segundos
- Alertas: Cada 5 segundos
- Escalamiento rápido

### 2. Zona de Carga (Operación Normal)
- Timer: 5 minutos
- Alertas: Cada 30 segundos
- Permite trabajo normal

### 3. Salida de Emergencia (Crítico)
- Timer: 5 segundos
- Alertas: Cada 3 segundos
- Máxima urgencia

---

## 🔍 Monitoreo

### Dashboard
- Badge azul "Telegram activo" en timers
- Contador de mensajes enviados
- Tiempo hasta próximo envío

### Logs Útiles
```bash
# Ver actividad de Telegram
tail -f backend.log | grep "📱"

# Ver alarmas activadas
tail -f backend.log | grep "ALARMA ACTIVADA"

# Ver imágenes capturadas
tail -f backend.log | grep "📸"
```

---

## 🛠️ Solución de Problemas

### No llegan mensajes
```bash
# 1. Verificar configuración
cat alerts/alert_config_v2.json | grep telegram -A5

# 2. Test manual
python test_telegram_simple.py

# 3. Verificar logs
tail -f backend.log | grep -i error
```

### No llegan imágenes
```bash
# 1. Verificar cámara
curl http://localhost:8889/api/cameras

# 2. Verificar captura
tail -f backend.log | grep "Imagen capturada"
```

---

## 📊 Formato de Alertas

### Primera Alerta (15s después)
```
[IMAGEN]
🚨 ALERTA ACTIVA - Puerta Abierta

📍 Zona: Entrada Principal
📹 Cámara: cam_001
⏱️ Tiempo: 0m 15s
📨 Notificación #1

⚠️ ALERTA: Puerta abierta detectada

⏰ Próximo en 5s
```

### Alerta Urgente (2+ minutos)
```
🚨🚨🚨 ALERTA ACTIVA

📍 Zona: Entrada Principal
⏱️ Tiempo: 2m 30s
📨 Notificación #8

⚠️ URGENTE: Verificar zona

⏰ Próximo en 20s
```

### Alerta Crítica (5+ minutos)
```
🚨🚨🚨🚨🚨 ALERTA ACTIVA

📍 Zona: Entrada Principal
⏱️ Tiempo: 5m 15s
📨 Notificación #15

⚠️ CRÍTICO: Atención INMEDIATA

⏰ Próximo en 60s
```

---

## 💡 Tips Profesionales

1. **Grupos por Turno**: Crear diferentes grupos para cada turno
2. **Sonido Distintivo**: Configurar tono especial en Telegram
3. **Prioridad**: Fijar el chat de alertas
4. **Historial**: Telegram guarda todo el historial
5. **Escalamiento**: Agregar supervisores después de X minutos

---

## 🔄 Flujo Completo

```
1. Puerta abre → Timer silencioso
2. 15s después → Primera alerta + imagen
3. +5s → Recordatorio #2 (texto)
4. +10s → Recordatorio #3 (texto)
5. +20s → Recordatorio #4 (texto)
6. +30s → Recordatorio #5 + imagen nueva
7. Puerta cierra → "✅ Puerta cerrada"
```

---

**Comando de Emergencia**
```bash
# Detener TODAS las alarmas
curl -X POST http://localhost:8889/api/alarms/stop-all
```

---

*Sistema desarrollado por Virgilio IA*  
*"La persistencia vence la resistencia"*
