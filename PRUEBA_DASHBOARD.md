# 🧪 Guía de Prueba del Dashboard

## Dashboard está corriendo en: http://localhost:8502

## Pasos para Probar:

1. **Abrir el navegador** y navegar a http://localhost:8502

2. **En el Dashboard**:
   - Verás el título "Sistema de Seguridad YOLO11 - Detección de Puertas"
   - En la barra lateral, asegúrate de que esté seleccionado "📸 Análisis de Imagen"

3. **Subir una imagen de prueba**:
   - Usa el botón "Browse files" 
   - Navega a `/Users/Shared/yolo11_project/test_images/`
   - Selecciona cualquiera de las imágenes (imagen1.jpg, imagen2.jpg, imagen3.jpg)

4. **Verificar resultados**:
   - ✅ Debe mostrar la imagen original y la imagen con detecciones
   - ✅ Las métricas deben mostrar:
     - 🚪 Puertas Abiertas: número detectado
     - 🔒 Puertas Cerradas: número detectado
     - 📊 Total Detecciones: suma de ambas
     - 🎯 Confianza Promedio: porcentaje
   - ✅ El estado de seguridad debe mostrar:
     - Alerta roja si hay puertas abiertas
     - Estado verde si todas están cerradas
   - ✅ La tabla debe listar cada detección con su confianza

5. **Ajustar umbral de confianza**:
   - En la barra lateral, mueve el slider "Umbral de Confianza"
   - Valores más altos = menos detecciones pero más confiables
   - Valores más bajos = más detecciones pero posibles falsos positivos

## Imágenes de Prueba Disponibles:
- `test_images/imagen1.jpg` - Primera imagen de prueba
- `test_images/imagen2.jpg` - Segunda imagen de prueba  
- `test_images/imagen3.jpg` - Tercera imagen de prueba

## Si hay errores:
1. Verificar en la terminal donde está corriendo streamlit
2. Los errores aparecerán en rojo en la consola
3. Copiar el error para debug

## Para detener el dashboard:
- Presiona Ctrl+C en la terminal donde está corriendo
