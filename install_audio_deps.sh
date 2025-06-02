#!/bin/bash
# Script de instalación de dependencias para el Sistema de Audio Multi-fase

echo "🔊 Instalando dependencias para el Sistema de Audio Multi-fase..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instalar pygame para reproducción de audio
echo "📦 Instalando pygame..."
pip install pygame

# Instalar numpy y scipy para generación de sonidos
echo "📦 Instalando numpy y scipy..."
pip install numpy scipy

# Opcional: pyttsx3 para Text-to-Speech futuro
echo "📦 Instalando pyttsx3 (opcional para TTS)..."
pip install pyttsx3

echo "✅ Dependencias instaladas correctamente"

# Generar archivos de sonido si no existen
if [ ! -d "backend/sounds" ]; then
    echo "🎵 Generando archivos de sonido..."
    python3 backend/utils/generate_sounds.py
fi

echo "🎊 Sistema de Audio Multi-fase listo para usar!"
