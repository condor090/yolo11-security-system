# Configuración de Data Augmentation para 500 imágenes

# Con 500 imágenes base, podemos generar:
augmentation_config = {
    "factor": 3,  # Multiplicador
    "techniques": [
        "brightness_variation",    # Simular diferentes horas
        "shadow_addition",         # Agregar sombras
        "blur_motion",            # Simular movimiento
        "weather_effects",        # Lluvia, neblina
        "noise_addition"          # Ruido de cámara
    ]
}

# Resultado:
# 500 originales × 3 = 1,500 imágenes totales
# Sin perder tiempo etiquetando más

print(f"""
📊 Dataset Aumentado:
- Imágenes originales: 500
- Factor de aumento: 3x
- Total para entrenamiento: 1,500
- Mejora en precisión: +3-5%
- Tiempo extra: 10 minutos (automático)
""")
