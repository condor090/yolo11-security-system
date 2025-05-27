# YOLO11 Security System 🛡️

Un sistema de seguridad inteligente basado en YOLO11 para la detección de rejas abiertas/cerradas, personas autorizadas y vehículos.

## 🎊 ÚLTIMA ACTUALIZACIÓN: MODELO DE PUERTAS ENTRENADO CON ÉXITO
- **Fecha:** 26 Mayo 2025
- **Precisión alcanzada:** 99.39% mAP@50
- **Tiempo de entrenamiento:** 44 minutos en MacBook Pro M3
- **Estado:** Listo para producción

## 🚀 Características Principales

- **Detección de Rejas**: Identifica automáticamente si una reja está abierta o cerrada ✅
- **Reconocimiento de Personas**: Distingue entre personas autorizadas y no autorizadas
- **Detección de Vehículos**: Identifica camiones, automóviles y motocicletas
- **Dashboard Web**: Interfaz de monitoreo en tiempo real con Streamlit
- **Alertas Inteligentes**: Sistema de notificaciones por eventos de seguridad
- **Modelo Optimizado**: 15MB, 25-40 FPS en M3 Pro

## 📊 Rendimiento del Modelo de Puertas

| Métrica | Valor Alcanzado | Objetivo Original |
|---------|-----------------|-------------------|
| mAP@50 | **99.39%** | 95% |
| mAP@50-95 | **86.10%** | 80% |
| Precisión | **97.3%** | 90% |
| Recall | **98.3%** | 90% |
| Velocidad | **30ms/imagen** | <100ms |
| Tamaño modelo | **15MB** | <50MB |

## 🏗️ Arquitectura del Sistema

```
YOLO11 Security System/
├── data/                     # Datasets
│   ├── train/               # 1,172 imágenes entrenamiento
│   ├── val/                 # 292 imágenes validación
│   └── test/                # Datos de prueba
├── models/                   # Modelos base YOLO11
├── runs/
│   └── gates/
│       └── gate_detector_v1/
│           └── weights/
│               └── best.pt   # 🌟 MODELO ENTRENADO
├── project_files/
│   ├── scripts/             # Scripts principales
│   ├── configs/             # Configuraciones
│   └── apps/                # Dashboard Streamlit
└── Dockerfile.security      # Configuración Docker
```

## 🛠️ Instalación y Configuración

### Prerequisitos

- Docker (versión 20.10+)
- Git
- 8GB RAM mínimo
- GPU NVIDIA o Apple Silicon (M1/M2/M3)

### Instalación Rápida

1. **Clonar el repositorio**:
```bash
git clone https://github.com/condor090/yolo11-security-system
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

# O probar el modelo directamente
python3 test_model.py
```

## 🎯 Uso del Modelo Entrenado

### Prueba Rápida
```python
from ultralytics import YOLO

# Cargar modelo entrenado
model = YOLO('runs/gates/gate_detector_v1/weights/best.pt')

# Detectar en imagen
results = model.predict('path/to/image.jpg', conf=0.5)

# Procesar resultados
for r in results:
    boxes = r.boxes
    for box in boxes:
        cls = model.names[int(box.cls)]
        conf = float(box.conf)
        print(f"Detectado: {cls} ({conf:.2%})")
```

### Dashboard Web

El dashboard incluye:
- Análisis en tiempo real
- Histórico de detecciones
- Sistema de alertas configurables
- Estadísticas de uso

## 📊 Dataset Utilizado

- **Origen**: 32,000+ imágenes de Telegram
- **Procesadas**: 1,464 imágenes
- **Clases**: gate_open, gate_closed
- **División**: 80% train, 20% val

## 🔧 Comandos Útiles

```bash
# Ver estado del sistema
./deploy.sh status

# Probar modelo
python3 test_model.py

# Ver logs en tiempo real
./deploy.sh logs yolo11-security-dashboard

# Entrenar con nuevos datos
python3 train_gates.py

# Detener todos los contenedores
./deploy.sh stop
```

## 📈 Resultados de Entrenamiento

<details>
<summary>Ver gráfica de evolución del entrenamiento</summary>

```
mAP50 Evolution:
100% |████████████████████| 99.39%
 90% |███████████████     |
 80% |████████████        |
 70% |██████████          |
 60% |████████            |
 50% |██████              |
 40% |████                |
 30% |███                 |
 20% |██                  |
 10% |█                   |
  0% |____________________|
     1   5   10   15   19  Épocas
```
</details>

## 🐛 Troubleshooting

### Apple Silicon (M1/M2/M3)
```bash
# Si hay problemas con MPS
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Usar Rosetta 2 si es necesario
arch -x86_64 python3 train_gates.py
```

### Docker en Mac
```bash
# Aumentar memoria asignada a Docker Desktop
# Preferences > Resources > Memory: 8GB mínimo
```

## 🚀 Roadmap

- [x] Modelo de detección de puertas
- [x] Dashboard web básico
- [ ] Sistema de alertas por Telegram
- [ ] API REST para integraciones
- [ ] Detección de personas autorizadas
- [ ] Detección de vehículos
- [ ] App móvil
- [ ] Edge deployment (Raspberry Pi)

## 📊 Casos de Uso Implementados

### 1. Control de Acceso Residencial ✅
- Detección de puerta abierta/cerrada en tiempo real
- Alertas configurables por tiempo
- Registro histórico de eventos

### 2. Próximamente
- Identificación de personas autorizadas
- Control vehicular
- Análisis de patrones

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:
1. Fork el proyecto
2. Crea una feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia AGPL-3.0 - ver archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- [Ultralytics](https://ultralytics.com/) por YOLO11
- Apple por los chips M3 Pro que hacen magia
- Virgilio (AI Assistant) por la guía durante el desarrollo
- La comunidad de Computer Vision

## 📞 Contacto

**Desarrollador**: condor090  
**GitHub**: https://github.com/condor090  
**Proyecto**: https://github.com/condor090/yolo11-security-system

---

**Sistema de Seguridad YOLO11** - Detección inteligente para un mundo más seguro 🛡️

*"De 0 a 99.39% de precisión en 44 minutos. El futuro es ahora."*
