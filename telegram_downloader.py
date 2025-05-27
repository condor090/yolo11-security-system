#!/usr/bin/env python3
"""
Script para descargar masivamente fotos de Telegram
Usa Telethon para automatizar la descarga
"""

import os
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
import argparse

# Necesitarás estos valores de https://my.telegram.org
API_ID = 'YOUR_API_ID'  # Reemplazar con tu API ID
API_HASH = 'YOUR_API_HASH'  # Reemplazar con tu API Hash
PHONE = '+52XXXXXXXXXX'  # Tu número de teléfono

async def download_media(client, chat_name, output_dir, limit=None):
    """
    Descarga todas las fotos de un chat/canal
    
    Args:
        client: Cliente de Telegram
        chat_name: Nombre del chat o canal
        output_dir: Directorio de salida
        limit: Límite de descargas (None = todas)
    """
    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Obtener el chat
    chat = await client.get_entity(chat_name)
    
    # Contador
    downloaded = 0
    skipped = 0
    
    print(f"📥 Descargando fotos de: {chat_name}")
    print(f"📁 Guardando en: {output_dir}")
    print("-" * 50)
    
    # Iterar sobre mensajes
    async for message in client.iter_messages(chat, limit=limit):
        # Solo procesar fotos
        if message.media and isinstance(message.media, MessageMediaPhoto):
            # Generar nombre único
            timestamp = message.date.strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}_{message.id}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            # Verificar si ya existe
            if os.path.exists(filepath):
                skipped += 1
                continue
            
            try:
                # Descargar
                await message.download_media(filepath)
                downloaded += 1
                
                # Progreso cada 100 fotos
                if downloaded % 100 == 0:
                    print(f"✅ Descargadas: {downloaded} fotos")
                    
            except Exception as e:
                print(f"❌ Error descargando {filename}: {e}")
    
    print("-" * 50)
    print(f"✅ Descarga completa!")
    print(f"📊 Total descargadas: {downloaded}")
    print(f"⏭️  Omitidas (ya existían): {skipped}")

async def main():
    parser = argparse.ArgumentParser(description='Descargar fotos de Telegram')
    parser.add_argument('--chat', required=True, help='Nombre del chat/canal')
    parser.add_argument('--output', default='telegram_photos', help='Directorio de salida')
    parser.add_argument('--limit', type=int, help='Límite de fotos a descargar')
    args = parser.parse_args()
    
    # Crear cliente
    client = TelegramClient('session', API_ID, API_HASH)
    
    try:
        # Conectar
        await client.start(PHONE)
        print("✅ Conectado a Telegram")
        
        # Descargar
        await download_media(client, args.chat, args.output, args.limit)
        
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
