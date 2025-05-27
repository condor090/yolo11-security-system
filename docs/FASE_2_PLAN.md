# 🚨 FASE 2: SISTEMA DE ALERTAS

## Objetivo
Implementar un sistema robusto de notificaciones en tiempo real cuando se detecten puertas abiertas.

## Alcance

### 1. Sistema de Alertas Multi-canal
- [ ] Email (Gmail SMTP)
- [ ] Telegram Bot
- [ ] WhatsApp (opcional)
- [ ] Notificaciones push web
- [ ] Registro en base de datos

### 2. Lógica de Alertas Inteligente
- [ ] Evitar spam (cooldown entre alertas)
- [ ] Niveles de severidad
- [ ] Horarios de alerta personalizables
- [ ] Agrupación de eventos cercanos

### 3. Dashboard de Alertas
- [ ] Historial de eventos
- [ ] Estadísticas de alertas
- [ ] Configuración de notificaciones
- [ ] Vista de timeline

### 4. Grabación de Evidencia
- [ ] Captura de imagen cuando se detecta puerta abierta
- [ ] Almacenamiento organizado por fecha/hora
- [ ] Limpieza automática de archivos antiguos

## Plan de Implementación

### Semana 1: Backend de Alertas
1. **Día 1-2**: Sistema de notificaciones base
   - Clase AlertManager
   - Integración con Gmail
   - Tests unitarios

2. **Día 3-4**: Telegram Bot
   - Crear bot con BotFather
   - Implementar comandos básicos
   - Envío de imágenes con detecciones

3. **Día 5-7**: Base de datos
   - SQLite para almacenamiento local
   - Modelo de datos para eventos
   - API de consultas

### Semana 2: Frontend y Optimización
1. **Día 8-9**: Dashboard de alertas
   - Vista de historial
   - Gráficas de actividad
   - Configuración de usuario

2. **Día 10-11**: Lógica inteligente
   - Sistema de cooldown
   - Agrupación de eventos
   - Filtros por horario

3. **Día 12-14**: Testing y documentación
   - Pruebas integrales
   - Documentación de usuario
   - Video demo

## Arquitectura Propuesta

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   YOLO Model    │────▶│ Alert Engine │────▶│   Channels  │
│  (Detección)    │     │  (Lógica)    │     │ (Telegram,  │
└─────────────────┘     └──────────────┘     │  Email...)  │
                               │              └─────────────┘
                               ▼
                        ┌──────────────┐
                        │   Database   │
                        │  (SQLite)    │
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  Dashboard   │
                        │ (Histórico)  │
                        └──────────────┘
```

## Tecnologías a Utilizar

- **Backend**: Python, SQLAlchemy, APScheduler
- **Notificaciones**: python-telegram-bot, smtplib
- **Base de datos**: SQLite
- **Frontend**: Streamlit (extender dashboard actual)
- **Queue**: Python Queue o Redis (para procesamiento asíncrono)

## Métricas de Éxito

1. **Tiempo de respuesta**: < 3 segundos desde detección hasta notificación
2. **Confiabilidad**: 99.9% de alertas enviadas exitosamente
3. **Usabilidad**: Configuración en < 5 minutos
4. **Escalabilidad**: Soportar múltiples cámaras/ubicaciones

## Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Spam de notificaciones | Alto | Sistema de cooldown configurable |
| Fallas de conectividad | Medio | Queue local con reintentos |
| Falsos positivos | Medio | Umbral configurable + confirmación visual |
| Límites de API | Bajo | Rate limiting inteligente |

## Entregables

1. **Código**:
   - `alert_manager.py` - Motor de alertas
   - `notification_channels.py` - Implementaciones de canales
   - `alert_database.py` - Capa de persistencia

2. **Configuración**:
   - `alerts_config.yaml` - Configuración de alertas
   - `.env` - Credenciales (no en git)

3. **Documentación**:
   - Guía de configuración
   - API reference
   - Troubleshooting guide

4. **Tests**:
   - Unit tests para cada componente
   - Integration tests end-to-end
   - Simulador de eventos

## Primeros Pasos

1. Crear estructura de directorios
2. Implementar AlertManager básico
3. Configurar Gmail SMTP
4. Prueba de concepto enviando primera alerta

---

**Inicio**: 26 de Mayo 2025
**Estimación**: 2 semanas
**Prioridad**: Alta
