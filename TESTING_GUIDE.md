# 🧪 Guía de Pruebas - YOLO11 Security System

Esta guía te ayudará a probar el sistema paso a paso usando las imágenes que subiste como ejemplo.

## 🚀 Inicio Rápido

### 1. Preparar el Entorno

```bash
# En el directorio del proyecto
cd /Users/Shared/yolo11_project

# Dar permisos al script
chmod +x deploy.sh

# Construir la imagen Docker
./deploy.sh build
```

### 2. Configurar Estructura de Datos

```bash
# Crear directorios necesarios
./deploy.sh setup

# Verificar estructura creada
ls -la data/
```

### 3. Preparar Imágenes de Prueba

Usando tus imágenes de ejemplo (reja cerrada y abierta):

```bash
# Crear directorio para imágenes de prueba
mkdir -p data/test_images

# Copiar tus imágenes (ajustar rutas según donde las tengas)
# Imagen 1: reja cerrada (08:21:34)
# Imagen 2: reja abierta con camión (09:19:39)
```

### 4. Primera Prueba - Dashboard Web

```bash
# Iniciar dashboard
./deploy.sh run-dashboard

# Abrir navegador en:
http://localhost:8501
```

**En el dashboard:**
1. Ve a "📸 Análisis de Imagen"
2. Sube tu primera imagen (reja cerrada)
3. Ajusta el umbral de confianza a 0.4-0.6
4. Observa las detecciones

## 📊 Pruebas Específicas

### Prueba 1: Detección de Estado de Reja

**Objetivo:** Verificar que el sistema detecta correctamente reja abierta/cerrada

**Pasos:**
1. Sube imagen con reja cerrada
2. Verifica detección de clase `gate_closed`
3. Sube imagen con reja abierta  
4. Verifica detección de clase `gate_open`

**Resultado esperado:**
- Bounding box alrededor de la reja
- Clasificación correcta del estado
- Confianza > 0.5

### Prueba 2: Detección de Vehículos

**Objetivo:** Sistema identifica vehículos correctamente

**Pasos:**
1. Usa imagen con el camión
2. Verifica detección de clase `truck`
3. Observa precisión del bounding box

**Resultado esperado:**
- Detección del camión con clase `truck`
- Bounding box preciso alrededor del vehículo

### Prueba 3: Detección de Personas

**Objetivo:** Identificar personas en las imágenes

**Pasos:**
1. Busca la persona visible en la imagen
2. Verifica si se detecta como `authorized_person` o `unauthorized_person`

**Nota:** Sin entrenamiento personalizado, podría no detectar personas pequeñas o lejanas.

## 🔧 Pruebas Avanzadas

### Modo Interactivo

```bash
# Acceder al contenedor
./deploy.sh run-interactive

# Dentro del contenedor, probar script directo:
python scripts/security_system.py --source /security_project/data/test_images/imagen1.jpg --confidence 0.5

# Para video (si tienes webcam):
python scripts/security_system.py --source 0 --confidence 0.6
```

### Análisis de Dataset

```bash
# Dentro del contenedor
python scripts/data_utils.py --action analyze --input-dir /security_project/data

# Visualizar muestras
python scripts/data_utils.py --action visualize --images-dir /security_project/data/test_images --labels-dir /security_project/data/test_labels --output-dir /security_project/runs/visualizations
```

### Docker Compose (Alternativa)

```bash
# Usando docker-compose para dashboard
docker-compose --profile dashboard up

# Para entrenamiento
docker-compose --profile training up

# Para Jupyter notebook
docker-compose --profile jupyter up
# Acceder a: http://localhost:8888 (token: security123)
```

## 📈 Resultados Esperados

### Con Modelo Pre-entrenado (COCO)

El modelo base YOLO11 detectará:
- ✅ **Vehículos**: Camiones, autos (clases generales)
- ✅ **Personas**: Detectará personas como clase genérica
- ❌ **Rejas**: NO detectará rejas específicamente (necesita entrenamiento)

### Después del Entrenamiento Personalizado

Con datos anotados y entrenamiento:
- ✅ **Estados de reja**: gate_open / gate_closed
- ✅ **Personas autorizadas/no autorizadas**
- ✅ **Vehículos específicos**: truck, car, motorcycle
- ✅ **Alta precisión** en tu escenario específico

## 🎯 Plan de Entrenamiento

### 1. Recolección de Datos

**Necesitas crear un dataset con:**
- 500-1000 imágenes de rejas abiertas
- 500-1000 imágenes de rejas cerradas  
- 300-500 imágenes con personas autorizadas
- 300-500 imágenes con personas no autorizadas
- 200-400 imágenes con diferentes vehículos

### 2. Anotación

**Herramientas recomendadas:**
- [LabelImg](https://github.com/tzutalin/labelImg) - Fácil de usar
- [CVAT](https://cvat.org/) - Profesional, basado en web
- [Roboflow](https://roboflow.com/) - Con funciones de augmentation

**Formato YOLO:** Cada imagen necesita un archivo `.txt` con:
```
class_id center_x center_y width height
```

### 3. Estructura del Dataset

```
data/
├── train/
│   ├── images/          # 80% de tus imágenes
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   └── labels/          # Anotaciones correspondientes
│       ├── img001.txt
│       ├── img002.txt
│       └── ...
├── val/
│   ├── images/          # 15% de tus imágenes
│   └── labels/
└── test/
    ├── images/          # 5% de tus imágenes
    └── labels/
```

### 4. Ejecutar Entrenamiento

```bash
# Verificar que tienes datos preparados
ls data/train/images/ | wc -l
ls data/val/images/ | wc -l

# Iniciar entrenamiento
./deploy.sh run-training

# Monitorear progreso
./deploy.sh logs yolo11-security-train

# O usar TensorBoard
docker-compose --profile tensorboard up
# Acceder a: http://localhost:6006
```

## 🐛 Solución de Problemas

### Problema: No se detectan rejas

**Causa:** Modelo base no fue entrenado para rejas
**Solución:** Necesitas entrenar modelo personalizado

### Problema: Baja precisión

**Causas posibles:**
- Umbral de confianza muy alto
- Iluminación diferente a datos de entrenamiento
- Ángulo de cámara muy distinto

**Soluciones:**
- Reducir umbral de confianza a 0.3-0.5
- Incluir más variedad en dataset de entrenamiento
- Aplicar data augmentation

### Problema: Error de GPU

```bash
# Verificar NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Si no funciona, usar CPU
# Editar docker-compose.yml y remover sección 'deploy'
```

### Problema: Memoria insuficiente

**Soluciones:**
- Reducir batch_size en configuración (8 o 4)
- Usar modelo más pequeño: `yolo11s.pt` en lugar de `yolo11m.pt`
- Reducir tamaño de imagen: 416 en lugar de 640

## 📋 Checklist de Pruebas

- [ ] ✅ Docker construido exitosamente
- [ ] ✅ Dashboard web funciona (puerto 8501)
- [ ] ✅ Subida de imagen funciona
- [ ] ✅ Detección de vehículos (camión) funciona
- [ ] ✅ Interfaz responsive y sin errores
- [ ] ⚠️ Detección de rejas (requiere entrenamiento)
- [ ] ⚠️ Clasificación de personas (requiere entrenamiento)
- [ ] 🔄 Entrenamiento con datos personalizados
- [ ] 🔄 Validación del modelo entrenado
- [ ] 🔄 Despliegue en producción

## 📞 Soporte

Si encuentras problemas:

1. **Revisar logs:**
   ```bash
   ./deploy.sh logs yolo11-security-dashboard
   ```

2. **Verificar recursos:**
   ```bash
   ./deploy.sh status
   docker stats
   ```

3. **Limpiar y reiniciar:**
   ```bash
   ./deploy.sh stop
   ./deploy.sh clean
   ./deploy.sh build
   ```

4. **Modo debug:**
   ```bash
   ./deploy.sh run-interactive
   # Ejecutar comandos manualmente dentro del contenedor
   ```

---

**¡Listo para probar tu sistema de seguridad inteligente!** 🛡️

La detección básica funcionará inmediatamente, pero para obtener los mejores resultados en tu escenario específico, necesitarás entrenar el modelo con tus propios datos anotados.
