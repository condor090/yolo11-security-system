# 🍎 Guía de Entrenamiento para Apple M3 Pro
# Optimizada para 60 imágenes de rejas abiertas

## 🎯 Plan Específico para tu Hardware

### ✅ **Tu M3 Pro es EXCELENTE para este proyecto**
- **CPU**: M3 Pro (11 cores) - Sobresaliente
- **RAM**: 18 GB - Perfecto
- **GPU**: M3 Pro GPU - Muy buena
- **Tiempo estimado**: 30-60 minutos total

## 📋 **Preparación de tus 60 Imágenes**

### 1. **Organizar tus Imágenes**
```bash
# Crear estructura para tus 60 imágenes
mkdir -p data/raw_images/gate_open
mkdir -p data/raw_images/gate_closed

# Copiar tus imágenes:
# - 60 imágenes de rejas abiertas → data/raw_images/gate_open/
# - Idealmente algunas de rejas cerradas → data/raw_images/gate_closed/
```

### 2. **División Inteligente del Dataset**
```bash
# Para 60 imágenes, división recomendada:
# - Train: 48 imágenes (80%)
# - Val: 12 imágenes (20%)
# - Test: Usar las mismas de validación

# Si tienes solo rejas abiertas, necesitarás al menos 10-20 de cerradas
# O usar data augmentation agresivo
```

### 3. **Anotación de Imágenes**

**Opción A: Herramienta Gráfica (Recomendada)**
```bash
# Instalar LabelImg
pip install labelImg

# Ejecutar
labelImg

# Configuración:
# - Open Dir: data/raw_images/gate_open/
# - Change Save Dir: data/train/labels/
# - Formato: YOLO
# - Clase: gate_open (ID: 0)
```

**Opción B: Anotación Semi-automática**
```bash
# Usar modelo pre-entrenado para ayudar
python scripts/auto_annotate_gates.py --input data/raw_images/ --output data/train/
```

## 🚀 **Entrenamiento Optimizado**

### 1. **Preparar Entorno**
```bash
cd /Users/Shared/yolo11_project
./deploy.sh build
./deploy.sh setup
```

### 2. **Ejecutar Entrenamiento M3 Pro**
```bash
# Método 1: Script optimizado (Recomendado)
./deploy.sh run-interactive
# Dentro del contenedor:
python scripts/train_m3_pro.py

# Método 2: Docker Compose
docker-compose --profile training up
```

### 3. **Monitorear Progreso**
```bash
# Logs en tiempo real
./deploy.sh logs yolo11-security-train

# TensorBoard (opcional)
docker-compose --profile tensorboard up
# Abrir: http://localhost:6006
```

## 📊 **Configuración Optimizada para M3 Pro**

### **Parámetros Perfectos para tu Hardware:**
```yaml
# Configuración específica para 60 imágenes + M3 Pro
modelo: yolo11s.pt          # Ligero, perfecto para datasets pequeños
batch_size: 12              # Óptimo para 18GB RAM
epochs: 150                 # Suficiente para 60 imágenes
learning_rate: 0.01         # Conservador para evitar overfitting
patience: 30                # Early stopping agresivo
device: "mps"               # GPU M3 Pro
workers: 6                  # 6 de tus 11 cores
cache: true                 # Usar tus 18GB RAM
```

### **Data Augmentation Específico para Rejas:**
```yaml
# Optimizado para estructuras fijas como rejas
degrees: 5.0                # Rotación mínima (rejas son fijas)
fliplr: 0.0                 # NO flip horizontal (orientación importa)
hsv_h: 0.01                 # Cambio de color mínimo
mosaic: 0.8                 # Moderado para dataset pequeño
```

## ⏱️ **Timeline Esperado**

```
Hora 0:00 - Preparación de datos (15-30 min)
├── Organizar 60 imágenes
├── Anotar con LabelImg
└── Dividir train/val

Hora 0:30 - Entrenamiento (30-60 min)
├── Épocas 1-50: Aprendizaje inicial
├── Épocas 50-100: Refinamiento
├── Épocas 100-150: Fine-tuning
└── Early stopping si converge antes

Hora 1:30 - Evaluación y exportación (10 min)
├── Validación final
├── Exportar modelo
└── Pruebas rápidas

Total: ~1.5-2 horas (incluyendo preparación)
```

## 🎯 **Resultados Esperados**

### **Con 60 Imágenes Bien Anotadas:**
- ✅ **Precisión**: 85-95% (excelente para uso real)
- ✅ **Recall**: 80-90% (detectará la mayoría de rejas)
- ✅ **Velocidad**: 30-50 FPS en tu M3 Pro
- ✅ **Tamaño modelo**: ~20-40 MB (muy eficiente)

### **Limitaciones con Dataset Pequeño:**
- ⚠️ Puede sobreajustarse a tus condiciones específicas
- ⚠️ Podría no generalizar bien a iluminación muy diferente
- ⚠️ Necesitará más datos para robustez extrema

## 🚨 **Consejos Críticos para Éxito**

### 1. **Calidad sobre Cantidad**
```bash
# Mejor 60 imágenes bien anotadas que 200 mal anotadas
# Asegúrate de que los bounding boxes sean precisos
# Incluye variedad: diferentes horas, ángulos, iluminación
```

### 2. **Anotación Precisa**
```bash
# Bounding box debe cubrir toda la reja visible
# Ser consistente con los límites
# No incluir partes del fondo en el bbox
```

### 3. **Validación Realista**
```bash
# Guarda 2-3 imágenes completamente nuevas para test final
# No las uses durante entrenamiento
# Úsalas para verificar que realmente funciona
```

## 🐛 **Troubleshooting M3 Pro**

### **Problema: Error de GPU MPS**
```bash
# Solución: Usar CPU temporalmente
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

### **Problema: Memoria insuficiente**
```bash
# Solución: Reducir batch size
batch_size: 8  # en lugar de 12
```

### **Problema: Entrenamiento muy lento**
```bash
# Solución: Verificar configuración
cache: true     # Debe estar activado
workers: 6      # Usar múltiples cores
```

## 🎉 **Después del Entrenamiento**

### **Probar tu Modelo:**
```bash
# Test con imagen nueva
python scripts/security_system.py \
  --model models/gate_detector_m3.pt \
  --source path/to/test_image.jpg \
  --confidence 0.5

# Test con webcam
python scripts/security_system.py \
  --model models/gate_detector_m3.pt \
  --source 0 \
  --confidence 0.5
```

### **Integrar en Dashboard:**
```bash
# El dashboard automáticamente usará tu modelo entrenado
./deploy.sh run-dashboard
# Ir a: http://localhost:8501
```

---

## ✅ **CONCLUSIÓN: Tu M3 Pro es PERFECTO para este proyecto**

**Ventajas de tu setup:**
- 🚀 **M3 Pro GPU**: Aceleración nativa con Metal
- 💾 **18 GB RAM**: Suficiente para cache completo
- ⚡ **11 cores**: Procesamiento paralelo eficiente
- 🔋 **Eficiencia energética**: No se sobrecalentará

**Con 60 imágenes bien preparadas, obtendrás un modelo funcional y preciso en menos de 2 horas.**

¿Quieres que te ayude con algún paso específico de la preparación de datos o tienes alguna duda sobre el proceso?
