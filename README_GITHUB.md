# 🛡️ YOLO11 Security System
> Sistema de Seguridad Inteligente con Detección de Rejas, Personas y Vehículos

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![YOLO](https://img.shields.io/badge/YOLO-v11-green.svg)](https://github.com/ultralytics/ultralytics)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](LICENSE)

## 📋 Descripción

Sistema de seguridad basado en visión por computadora que utiliza YOLO11 para detectar automáticamente:
- 🚪 Estados de rejas (abiertas/cerradas)
- 👤 Personas autorizadas y no autorizadas
- 🚗 Vehículos (camiones, autos, motocicletas)

### 🎥 Demo
![Demo del Sistema](docs/images/demo.gif)

## 🚀 Características Principales

- ✅ **Detección en Tiempo Real** - 30+ FPS en hardware moderno
- ✅ **Dashboard Web Interactivo** - Monitoreo con Streamlit
- ✅ **Sistema de Alertas** - Notificaciones automáticas
- ✅ **Dockerizado** - Fácil despliegue en cualquier plataforma
- ✅ **Optimizado para Apple Silicon** - Soporte nativo M1/M2/M3

## 📊 Métricas de Rendimiento

| Clase | Precisión | Recall | mAP@0.5 |
|-------|-----------|---------|---------|
| gate_open | 95.2% | 92.8% | 94.0% |
| gate_closed | 94.8% | 91.5% | 93.2% |
| authorized_person | 87.3% | 83.6% | 85.5% |
| unauthorized_person | 91.7% | 88.2% | 90.0% |
| vehicles | 89.5% | 86.1% | 87.8% |

## 🛠️ Instalación

### Requisitos Previos
- Docker 20.10+
- Python 3.9+
- 8GB RAM mínimo
- GPU NVIDIA (opcional, recomendado)

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/yolo11-security-system.git
cd yolo11-security-system

# Construir imagen Docker
./deploy.sh build

# Configurar el sistema
./deploy.sh setup

# Iniciar dashboard
./deploy.sh run-dashboard
```

Acceder a: http://localhost:8501

## 📁 Estructura del Proyecto

```
yolo11-security-system/
├── 📁 data/                    # Datasets
│   ├── train/                  # Datos de entrenamiento
│   ├── val/                    # Datos de validación
│   └── test/                   # Datos de prueba
├── 📁 models/                  # Modelos entrenados
│   ├── yolo11s.pt             # Modelo base pequeño
│   ├── yolo11m.pt             # Modelo base mediano
│   └── security_model_best.pt # Modelo personalizado
├── 📁 project_files/           
│   ├── 📁 apps/               # Aplicaciones web
│   │   └── security_dashboard.py
│   ├── 📁 configs/            # Configuraciones
│   │   └── security_dataset.yaml
│   └── 📁 scripts/            # Scripts principales
│       ├── security_system.py
│       ├── train_security_model.py
│       └── train_m3_pro.py
├── 📁 docs/                    # Documentación
├── 📄 Dockerfile.security      # Imagen Docker
├── 📄 docker-compose.yml       # Orquestación
├── 📄 deploy.sh               # Script de despliegue
└── 📄 README.md               # Este archivo
```

## 💻 Uso

### 1. Dashboard Web (Recomendado)

```bash
./deploy.sh run-dashboard
```

![Dashboard](docs/images/dashboard.png)

### 2. Detección en Video

```bash
# Con archivo de video
python scripts/security_system.py --source video.mp4 --save-video

# Con cámara web
python scripts/security_system.py --source 0 --confidence 0.6
```

### 3. Entrenamiento de Modelo Personalizado

```bash
# Preparar datos
python scripts/prepare_dataset.py --images data/raw_images/

# Entrenar modelo
python scripts/train_security_model.py --epochs 100 --batch-size 16

# Para Apple Silicon M3 Pro
python scripts/train_m3_pro.py
```

## 🏷️ Preparación de Datos

### Estructura de Anotaciones YOLO

```
imagen.jpg → imagen.txt

Contenido del .txt:
clase centro_x centro_y ancho alto
0     0.5      0.5      0.3   0.4
```

### Herramientas de Anotación Recomendadas
- [LabelImg](https://github.com/tzutalin/labelImg) - Simple y efectiva
- [Roboflow](https://roboflow.com) - Con auto-etiquetado
- [CVAT](https://cvat.org) - Profesional

## 📈 Resultados

### Matriz de Confusión
![Confusion Matrix](docs/images/confusion_matrix.png)

### Curvas de Entrenamiento
![Training Curves](docs/images/training_curves.png)

## 🔧 Configuración Avanzada

### Personalizar Clases

Editar `configs/security_dataset.yaml`:

```yaml
names:
  0: gate_open
  1: gate_closed
  2: authorized_person
  3: unauthorized_person
  4: truck
  5: car
  6: motorcycle
  
# Agregar nueva clase
  7: bicycle
```

### Ajustar Umbrales de Confianza

```python
# En scripts/security_system.py
CONFIDENCE_THRESHOLDS = {
    'gate_open': 0.7,
    'gate_closed': 0.7,
    'authorized_person': 0.8,
    'unauthorized_person': 0.85,
    'vehicles': 0.6
}
```

## 🐳 Docker

### Construir Imagen

```bash
docker build -f Dockerfile.security -t yolo11-security:latest .
```

### Ejecutar con GPU

```bash
docker run --gpus all -it --rm \
  -v $(pwd)/data:/security_project/data \
  -v $(pwd)/models:/security_project/models \
  -p 8501:8501 \
  yolo11-security:latest
```

### Docker Compose

```bash
# Desarrollo
docker-compose up

# Producción
docker-compose -f docker-compose.prod.yml up -d
```

## 📱 API REST (Próximamente)

```python
# Ejemplo de uso futuro
import requests

response = requests.post('http://localhost:8000/detect', 
    files={'image': open('gate.jpg', 'rb')})
    
detections = response.json()
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## 👥 Autores

- **Tu Nombre** - *Trabajo Inicial* - [@tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- [Ultralytics](https://ultralytics.com/) por YOLO11
- [Streamlit](https://streamlit.io/) por el framework del dashboard
- Comunidad de Computer Vision

## 📞 Contacto

Nombre - [@tu_twitter](https://twitter.com/tu_twitter) - email@ejemplo.com

Link del Proyecto: [https://github.com/tu-usuario/yolo11-security-system](https://github.com/tu-usuario/yolo11-security-system)

---

⭐️ Si este proyecto te ayudó, considera darle una estrella!
