## 🔧 Integración de Notificaciones Telegram en YOMJAI

### Configuración Implementada

**API Token**: 7907731965:AAE99G_I23PSPY4Iu2mB2c8J1l-fhTrYTK4
**Chat ID**: -4523731379

### Características Agregadas:

1. **Frontend (SystemConfig.jsx)**
   - Nueva sección "Configuración de Telegram"
   - Toggle para habilitar/deshabilitar
   - Campos para Bot Token y Chat ID
   - Opciones para enviar texto e imágenes
   - Botón de prueba para verificar conexión

2. **Backend (telegram_service.py)**
   - Servicio completo para envío de mensajes
   - Soporte para texto e imágenes con detecciones
   - Mensajes formateados con HTML
   - Notificaciones de:
     - 🚨 Puerta Abierta (alerta)
     - ✅ Puerta Cerrada (seguro)
     - 👁️ Alarma Reconocida
     - 📊 Resumen diario

3. **Integración en main.py**
   - Endpoints `/api/telegram/test` para pruebas
   - Envío automático cuando se detecta puerta abierta
   - Notificación cuando se cierra puerta
   - Incluye imagen con detecciones si está habilitado

### Próximos Pasos:

1. Abrir el navegador en http://localhost:3000
2. Ir a la pestaña "Configuración"
3. Activar "Notificaciones por Telegram"
4. Ingresar el Bot Token y Chat ID proporcionados
5. Guardar configuración
6. Probar con el botón "Enviar Mensaje de Prueba"

### Formato de Mensajes:

- **Alerta**: Incluye zona, hora, estado ACTIVA
- **Cierre**: Confirma zona segura
- **Imagen**: Frame con bounding boxes de detecciones

El sistema está listo para enviar alertas en tiempo real a Telegram.
