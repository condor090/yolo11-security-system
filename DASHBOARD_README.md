# Dashboard de Seguridad YOLO11 - Detección de Puertas

## 🚀 Inicio Rápido

### Opción 1: Ejecutar localmente

```bash
# Instalar dependencias si no las tienes
pip install streamlit ultralytics pillow plotly

# Ejecutar el dashboard
python run_dashboard.py

# O directamente con streamlit
streamlit run project_files/apps/security_dashboard.py
```

### Opción 2: Usar Docker

```bash
# Construir imagen si no existe
./deploy.sh build

# Ejecutar dashboard
./deploy.sh run-dashboard
```

## 📸 Cómo Usar

1. **Abrir el Dashboard**: Navega a http://localhost:8501

2. **Modo Análisis de Imagen**:
   - Selecciona "📸 Análisis de Imagen" en el menú lateral
   - Ajusta el umbral de confianza (0.5 por defecto)
   - Sube una imagen con puertas/rejas
   - El sistema detectará automáticamente si están abiertas o cerradas

3. **Interpretación de Resultados**:
   - **🚪 Puertas Abiertas**: Número de puertas detectadas como abiertas
   - **🔒 Puertas Cerradas**: Número de puertas detectadas como cerradas
   - **📊 Total Detecciones**: Total de puertas detectadas
   - **🎯 Confianza Promedio**: Qué tan seguro está el modelo

## 🎯 Características

- ✅ Detección de puertas con 99.39% de precisión
- ✅ Interfaz web intuitiva
- ✅ Alertas visuales para puertas abiertas
- ✅ Métricas en tiempo real
- ✅ Tabla detallada de detecciones

## 📊 Modelo Utilizado

- **Ubicación**: `runs/gates/gate_detector_v1/weights/best.pt`
- **Precisión**: 99.39% mAP@50
- **Clases**: gate_open, gate_closed
- **Tamaño**: 15MB
- **Velocidad**: 30ms por imagen

## 🛠️ Próximas Mejoras

- [ ] Streaming de video en tiempo real
- [ ] Histórico de detecciones
- [ ] Sistema de notificaciones
- [ ] Soporte para múltiples cámaras

## 🐛 Solución de Problemas

Si el modelo no se encuentra:
```bash
# Verificar que el modelo existe
ls runs/gates/gate_detector_v1/weights/best.pt

# Si no existe, verificar la ruta correcta
find . -name "best.pt" -type f
```

Si Streamlit no funciona:
```bash
# Reinstalar streamlit
pip install --upgrade streamlit

# Verificar versión
streamlit version
```

## 📝 Notas

- El dashboard busca automáticamente el modelo entrenado
- Las imágenes se procesan en memoria, no se guardan
- El umbral de confianza afecta la sensibilidad de detección
