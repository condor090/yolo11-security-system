#!/usr/bin/env python3
"""
Descargador simplificado para AlertasFullYomjai
Usando el ID del grupo directamente
"""

import os
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
import json
from tqdm import tqdm

# Credenciales
API_ID = 26005180
API_HASH = 'c86549df51d1b77f390fe79020fb0ff3'
PHONE = '+526624152145'

# Configuración
OUTPUT_DIR = '/Users/Shared/yolo11_project/data/telegram_photos'

async def download_group_photos():
    """Descarga fotos del grupo AlertasFullYomjai"""
    
    # Crear directorio
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    client = TelegramClient('alertas_session', API_ID, API_HASH)
    
    try:
        # Conectar
        await client.start(PHONE)
        print("✅ Conectado a Telegram")
        
        # Buscar el grupo
        print("🔍 Buscando grupo AlertasFullYomjai...")
        
        target_group = None
        async for dialog in client.iter_dialogs():
            if dialog.is_group and 'AlertasFullYomjai' in dialog.name:
                target_group = dialog
                print(f"✅ Grupo encontrado: {dialog.name}")
                break
        
        if not target_group:
            print("❌ No se encontró el grupo AlertasFullYomjai")
            return
        
        # Contar mensajes totales
        print("📊 Analizando mensajes del grupo...")
        total_count = 0
        photo_count = 0
        
        # Primera pasada para contar
        async for message in client.iter_messages(target_group.entity, limit=None):
            total_count += 1
            if message.media and isinstance(message.media, MessageMediaPhoto):
                photo_count += 1
            
            if total_count % 1000 == 0:
                print(f"Analizados {total_count} mensajes, {photo_count} fotos encontradas...")
        
        print(f"\n📊 Total: {total_count} mensajes, {photo_count} fotos")
        
        # Confirmar descarga
        print(f"\n💾 Se descargarán {photo_count} fotos (~{photo_count * 0.2:.1f} MB)")
        print(f"📁 Destino: {OUTPUT_DIR}")
        
        # Segunda pasada para descargar
        print("\n⬇️ Iniciando descarga...")
        
        downloaded = 0
        errors = 0
        
        pbar = tqdm(total=photo_count, desc="Descargando fotos")
        
        async for message in client.iter_messages(target_group.entity, limit=None):
            if message.media and isinstance(message.media, MessageMediaPhoto):
                try:
                    # Nombre único
                    date_str = message.date.strftime("%Y%m%d_%H%M%S")
                    filename = f"puerta_{date_str}_{message.id}.jpg"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    
                    # Descargar si no existe
                    if not os.path.exists(filepath):
                        await message.download_media(filepath)
                        downloaded += 1
                    
                    pbar.update(1)
                    
                except Exception as e:
                    errors += 1
                    print(f"\n❌ Error: {e}")
        
        pbar.close()
        
        # Resumen
        print("\n" + "="*50)
        print("✅ DESCARGA COMPLETA")
        print(f"📸 Fotos descargadas: {downloaded}")
        print(f"❌ Errores: {errors}")
        print(f"📁 Ubicación: {OUTPUT_DIR}")
        print("="*50)
        
        # Crear archivo de resumen
        summary = {
            'group_name': target_group.name,
            'total_messages': total_count,
            'total_photos': photo_count,
            'downloaded': downloaded,
            'errors': errors,
            'download_date': datetime.now().isoformat()
        }
        
        with open(os.path.join(OUTPUT_DIR, 'download_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nSi el error persiste, use Telegram Desktop para descargar manualmente")
        
    finally:
        await client.disconnect()

if __name__ == '__main__':
    print("🚀 Descargador de fotos - AlertasFullYomjai")
    print("-" * 50)
    asyncio.run(download_group_photos())
