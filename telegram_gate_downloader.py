#!/usr/bin/env python3
"""
Descargador específico para fotos de rejas desde Telegram
Filtra y organiza automáticamente
"""

import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto

# Configuración
API_ID = 'YOUR_API_ID'
API_HASH = 'YOUR_API_HASH'
PHONE = '+52XXXXXXXXXX'

# Palabras clave para filtrar
KEYWORDS_OPEN = ['abierta', 'open', 'entrada', 'entrando']
KEYWORDS_CLOSED = ['cerrada', 'closed', 'bloqueada']

async def download_gate_photos(client, chat_name, output_base='data/telegram'):
    """Descarga y organiza fotos de rejas"""
    
    # Crear directorios
    os.makedirs(f"{output_base}/gates_open", exist_ok=True)
    os.makedirs(f"{output_base}/gates_closed", exist_ok=True)
    os.makedirs(f"{output_base}/unknown", exist_ok=True)
    
    chat = await client.get_entity(chat_name)
    
    # Contadores
    stats = {'open': 0, 'closed': 0, 'unknown': 0, 'total': 0}
    
    # Fecha límite (últimos 30 días)
    date_limit = datetime.now() - timedelta(days=30)
    
    print(f"🔍 Buscando fotos de los últimos 30 días...")
    
    async for message in client.iter_messages(chat, reverse=True):
        # Saltar mensajes antiguos
        if message.date < date_limit:
            continue
            
        # Solo fotos
        if message.media and isinstance(message.media, MessageMediaPhoto):
            stats['total'] += 1
            
            # Determinar categoría
            text = (message.text or '').lower()
            category = 'unknown'
            
            if any(kw in text for kw in KEYWORDS_OPEN):
                category = 'gates_open'
                stats['open'] += 1
            elif any(kw in text for kw in KEYWORDS_CLOSED):
                category = 'gates_closed'
                stats['closed'] += 1
            else:
                stats['unknown'] += 1
            
            # Nombre del archivo
            timestamp = message.date.strftime("%Y%m%d_%H%M%S")
            filename = f"{category}_{timestamp}_{message.id}.jpg"
            filepath = os.path.join(output_base, category, filename)
            
            # Descargar
            try:
                await message.download_media(filepath)
                
                # Progreso
                if stats['total'] % 50 == 0:
                    print(f"📊 Procesadas: {stats['total']} | "
                          f"Abiertas: {stats['open']} | "
                          f"Cerradas: {stats['closed']} | "
                          f"Sin clasificar: {stats['unknown']}")
                          
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Resumen final
    print("\n" + "="*50)
    print("✅ DESCARGA COMPLETA")
    print(f"📊 Total procesadas: {stats['total']}")
    print(f"🟢 Puertas abiertas: {stats['open']}")
    print(f"🔴 Puertas cerradas: {stats['closed']}")
    print(f"❓ Sin clasificar: {stats['unknown']}")
    print("="*50)

async def main():
    client = TelegramClient('gate_photos_session', API_ID, API_HASH)
    
    try:
        await client.start(PHONE)
        print("✅ Conectado a Telegram")
        
        # Reemplazar con el nombre de tu chat
        await download_gate_photos(client, 'NOMBRE_DE_TU_CHAT')
        
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
