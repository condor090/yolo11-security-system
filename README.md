# YOLO11 Security System

Un sistema de seguridad inteligente basado en YOLO11 para la detección de rejas abiertas/cerradas, personas autorizadas y vehículos.

## 🚀 Características Principales

- **Detección de Rejas**: Identifica automáticamente si una reja está abierta o cerrada
- **Reconocimiento de Personas**: Distingue entre personas autorizadas y no autorizadas
- **Detección de Vehículos**: Identifica camiones, automóviles y motocicletas
- **Dashboard Web**: Interfaz de monitoreo en tiempo real con Streamlit
- **Alertas Inteligentes**: Sistema de notificaciones por eventos de seguridad
- **Contenedorizado**: Fácil despliegue con Docker y GPU/CPU

## 🏗️ Arquitectura del Sistema

```
YOLO11 Security System/
├── ultralytics-main/          # Código fuente YOLO11
├── project_files/
│   ├── scripts/              # Scripts principales
│   ├── configs/              # Configuraciones
│   └── apps/                 # Aplicaciones web
├── data/                     # Datasets
│   ├── train/               # Datos de entrenamiento
│   ├── val/                 # Datos de validación
│   └── test/                # Datos de prueba
├── models/                   # Modelos entrenados
├── runs/                     # Resultados de entrenamiento
├── logs/                     # Archivos de log
└── Dockerfile.security       # Configuración Docker
```

## 🛠️ Instalación y Configuración

### Prerequisitos

- Docker (versión 20.10+)
- NVIDIA Docker (opcional, para GPU)
- Git
- 8GB RAM mínimo
- GPU NVIDIA (recomendado)

### Instalación Rápida

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd yolo11_project
```

2. **Configurar y construir**:
```bash
# Dar permisos al script
chmod +x deploy.sh

# Construir imagen Docker
./deploy.sh build

# Configurar directorios y descargar modelos
./deploy.sh setup
```

3. **Ejecutar el sistema**:
```bash
# Dashboard web (recomendado para empezar)
./deploy.sh run-dashboard
# Acceder a: http://localhost:8501

# O modo interactivo para desarrollo
./deploy.sh run-interactive
```

## 📊 Clases de Detección

El sistema está configurado para detectar 7 clases principales:

| ID | Clase | Descripción |
|----|-------|-------------|
| 0 | `gate_open` | Reja o portón en posición abierta |
| 1 | `gate_closed` | Reja o portón en posición cerrada |
| 2 | `authorized_person` | Persona autorizada identificada |
| 3 | `unauthorized_person` | Persona no autorizada o desconocida |
| 4 | `truck` | Vehículo tipo camión |
| 5 | `car` | Vehículo tipo automóvil |
| 6 | `motorcycle` | Vehículo tipo motocicleta |

## 🚀 Guía de Uso

### 1. Dashboard Web (Recomendado)

```bash
./deploy.sh run-dashboard
```

Accede a `http://localhost:8501` para:
- Monitoreo en tiempo real
- Análisis de imágenes
- Visualización de estadísticas
- Configuración de alertas

### 2. Entrenamiento de Modelo

```bash
# Preparar datos en: data/train/ y data/val/
# Ejecutar entrenamiento
./deploy.sh run-training

# Monitorear progreso
./deploy.sh logs yolo11-security-train
```

### 3. Inferencia desde Línea de Comandos

```bash
# Modo interactivo
./deploy.sh run-interactive

# Dentro del contenedor:
python scripts/security_system.py --source 0 --confidence 0.6
python scripts/security_system.py --source /path/to/video.mp4 --save-video
```

### 4. API de Detección

```bash
# Iniciar servicio de inferencia
./deploy.sh run-inference

# El sistema estará disponible para procesar streams de video
```

## 📁 Preparación de Datos

### Estructura del Dataset

```
data/
├── train/
│   ├── images/              # Imágenes de entrenamiento
│   └── labels/              # Anotaciones YOLO (.txt)
├── val/
│   ├── images/              # Imágenes de validación
│   └── labels/              # Anotaciones YOLO (.txt)
└── test/
    ├── images/              # Imágenes de prueba
    └── labels/              # Anotaciones YOLO (.txt)
```

### Formato de Anotaciones

Cada archivo `.txt` contiene las anotaciones en formato YOLO:
```
class_id center_x center_y width height
```

Ejemplo:
```
0 0.5 0.3 0.4 0.2    # gate_open
2 0.7 0.8 0.1 0.3    # authorized_person
```

### Herramientas de Anotación Recomendadas

- [LabelImg](https://github.com/tzutalin/labelImg)
- [CVAT](https://cvat.org/)
- [Roboflow](https://roboflow.com/)

## ⚙️ Configuración Avanzada

### Parámetros de Entrenamiento

Editar `project_files/configs/security_dataset.yaml`:

```yaml
train_config:
  epochs: 300
  batch_size: 16
  learning_rate: 0.01
  image_size: 640

augmentation:
  degrees: 10.0
  translate: 0.1
  scale: 0.5
  fliplr: 0.0  # No flip horizontal para mantener orientación
```

### Configuración de Alertas

```python
# En scripts/security_system.py
ALERT_THRESHOLDS = {
    'unauthorized_person': 0.8,
    'gate_open_duration': 300,  # segundos
    'multiple_vehicles': 3
}
```

## 📈 Métricas y Evaluación

### Métricas Objetivo por Clase

| Clase | Precisión | Recall |
|-------|-----------|--------|
| gate_open | 95% | 90% |
| gate_closed | 95% | 90% |
| authorized_person | 85% | 80% |
| unauthorized_person | 90% | 85% |
| truck | 90% | 85% |
| car | 85% | 80% |
| motorcycle | 80% | 75% |

### Comandos de Evaluación

```bash
# Validar modelo
docker exec yolo11-security python scripts/train_security_model.py --validate

# Exportar modelo
docker exec yolo11-security python scripts/train_security_model.py --export
```

## 🔧 Comandos Útiles

```bash
# Ver estado del sistema
./deploy.sh status

# Ver logs en tiempo real
./deploy.sh logs yolo11-security-dashboard

# Detener todos los contenedores
./deploy.sh stop

# Limpiar sistema completamente
./deploy.sh clean

# Acceso interactivo al contenedor
./deploy.sh run-interactive
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error de GPU**:
```bash
# Verificar NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

2. **Memoria insuficiente**:
```bash
# Reducir batch size en configuración
# O usar modelo más pequeño: yolo11s.pt
```

3. **Puertos ocupados**:
```bash
# Cambiar puertos en deploy.sh
-p 8502:8501  # En lugar de 8501:8501
```

4. **Datos no encontrados**:
```bash
# Verificar estructura de directorios
ls -la data/train/images/
ls -la data/train/labels/
```

## 📊 Casos de Uso

### 1. Control de Acceso Vehicular
- Detección automática de apertura/cierre de rejas
- Identificación de vehículos autorizados
- Registro de eventos de entrada/salida

### 2. Seguridad Perimetral
- Detección de personas no autorizadas
- Alertas en tiempo real
- Grabación de eventos de seguridad

### 3. Monitoreo de Tráfico
- Conteo de vehículos por tipo
- Análisis de patrones de tráfico
- Estadísticas de uso

## 🔮 Funcionalidades Futuras

- [ ] Reconocimiento facial para personas autorizadas
- [ ] Detección de matrículas vehiculares
- [ ] Integración con sistemas de alarmas
- [ ] API REST para integraciones
- [ ] Análisis de comportamiento anómalo
- [ ] Reportes automáticos por email
- [ ] App móvil para monitoreo

## 📞 Soporte

Para reportar bugs o solicitar funcionalidades:
- Crear un issue en el repositorio
- Incluir logs relevantes
- Especificar configuración del sistema

## 📄 Licencia

Este proyecto está bajo la licencia AGPL-3.0 - ver archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- [Ultralytics](https://ultralytics.com/) por YOLO11
- Comunidad de Computer Vision
- Contribuidores del proyecto

---

**Sistema de Seguridad YOLO11** - Detección inteligente para un mundo más seguro 🛡️
