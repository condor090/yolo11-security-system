# 📖 Guía de Interpretación de Detecciones

## Caso: Detecciones Múltiples de la Misma Puerta

### Síntoma
El modelo detecta la misma puerta varias veces con cajas superpuestas.

### Interpretación
- **Una puerta real** = Posibles múltiples detecciones
- Las cajas rojas superpuestas indican que el modelo ve la puerta desde diferentes "perspectivas"
- Confianza similar (50-52%) sugiere que ambas detecciones son válidas

### Soluciones Recomendadas

#### 1. Aplicar Non-Maximum Suppression (NMS) más agresivo
```python
# En el código, ajustar el parámetro iou_threshold
results = model.predict(image, conf=0.5, iou=0.5)  # Reducir de 0.7 a 0.5
```

#### 2. Post-procesamiento manual
```python
def merge_overlapping_boxes(detections, iou_threshold=0.5):
    """Combinar detecciones que se superponen significativamente"""
    # Implementar lógica para fusionar cajas
    pass
```

#### 3. Ajustar el umbral de confianza
- Si subes el umbral a 0.6, podrías quedarte con solo una detección
- Pero podrías perder detecciones válidas en otros casos

### Recomendación para el Usuario

**Para uso práctico**:
- Si ves múltiples cajas en la misma área = **1 puerta abierta**
- La confianza promedio (51%) indica detección confiable
- Para alertas de seguridad: Una o más detecciones de "gate_open" = Puerta abierta, tomar acción

### Métricas Correctas para este Caso
- 🚪 Puertas Abiertas: **1** (aunque muestre 2 detecciones)
- 🔒 Puertas Cerradas: **0**
- 🎯 Confianza: **51%** (promedio)

## Otros Casos Comunes

### Caso 2: Puerta Parcialmente Visible
- El modelo puede no detectarla si está muy obstruida
- Solución: Bajar umbral de confianza a 0.3-0.4

### Caso 3: Reflejos o Sombras
- Pueden causar falsos positivos
- Solución: Entrenar con más ejemplos de estas condiciones

### Caso 4: Puertas Múltiples Reales
- Si hay varias puertas, cada una tendrá su caja
- Verificar visualmente para confirmar

## Configuración Óptima Sugerida

Para la mayoría de casos:
```
Umbral de Confianza: 0.45-0.55
IOU Threshold: 0.5
```

Esto balancea entre detectar todas las puertas y evitar duplicados excesivos.
