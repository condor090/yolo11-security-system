# 🚨 REPORTE DE FALSO POSITIVO

## Fecha: 26 de Mayo 2025, 17:45 hrs

### Descripción del Problema
El modelo detectó "gate_open" con 50-52% de confianza en una imagen que NO contenía ninguna puerta (ni abierta ni cerrada).

### Análisis
1. **Tipo de Error**: Falso Positivo
2. **Confianza**: 50-52% (justo en el límite)
3. **Posibles Causas**:
   - El modelo podría estar confundiendo:
     - Ventanas con puertas
     - Espacios entre objetos con aberturas
     - Patrones arquitectónicos similares
     - Reflejos o sombras

### Soluciones Propuestas

#### 1. Ajuste Inmediato del Umbral
```python
# Subir el umbral de confianza para reducir falsos positivos
confidence_threshold = 0.65  # En lugar de 0.50
```

#### 2. Análisis de Patrones
- Recopilar más ejemplos de falsos positivos
- Identificar qué elementos confunden al modelo
- Crear dataset de "negativos duros" (hard negatives)

#### 3. Re-entrenamiento Futuro
- Agregar imágenes similares etiquetadas como "sin puerta"
- Aumentar diversidad del dataset
- Incluir más ejemplos de:
  - Ventanas
  - Pasillos sin puertas
  - Espacios abiertos que no son puertas

#### 4. Validación Manual
Para casos críticos de seguridad:
- Si confianza < 65%: Requiere verificación humana
- Si confianza > 75%: Alta probabilidad de ser correcta
- Entre 65-75%: Zona gris, revisar contexto

### Configuración Recomendada Actualizada

```python
# Para reducir falsos positivos
CONFIDENCE_THRESHOLD = 0.65
IOU_THRESHOLD = 0.5

# Niveles de alerta
ALTA_CONFIANZA = 0.75    # Verde - Muy seguro
MEDIA_CONFIANZA = 0.65   # Amarillo - Revisar
BAJA_CONFIANZA = 0.50    # Rojo - Probablemente falso
```

### Acciones Inmediatas
1. ✅ Documentar este caso
2. ✅ Ajustar umbral en dashboard
3. ⏳ Recopilar más ejemplos similares
4. ⏳ Planear re-entrenamiento con negativos duros

### Nota para el Usuario
**Este es un comportamiento NORMAL en modelos de IA**. El 99.39% de precisión significa que ~1 de cada 100 detecciones puede ser incorrecta. La clave es ajustar los umbrales según sus necesidades de seguridad.
