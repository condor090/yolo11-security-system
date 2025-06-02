#!/bin/bash
# Script de instalación y configuración para descarga masiva de Telegram

echo "🚀 Configurando descargador de Telegram..."

# Instalar Telethon
pip3 install telethon pillow tqdm

echo ""
echo "📋 Pasos para usar el descargador:"
echo ""
echo "1. Ve a https://my.telegram.org"
echo "2. Inicia sesión con tu número"
echo "3. Crea una aplicación"
echo "4. Copia API_ID y API_HASH"
echo ""
echo "5. Edita telegram_downloader.py con tus credenciales:"
echo "   API_ID = 'tu_api_id'"
echo "   API_HASH = 'tu_api_hash'"
echo "   PHONE = '+52 tu_numero'"
echo ""
echo "6. Ejecutar:"
echo "   python telegram_downloader.py --chat 'Nombre_del_Chat' --output fotos_telegram"
echo ""
echo "💡 Tips:"
echo "- Para canales públicos: usar @nombre_canal"
echo "- Para chats privados: usar el nombre exacto"
echo "- Agregar --limit 100 para probar con 100 fotos primero"
echo ""
echo "✅ Instalación completa!"
