#!/usr/bin/env python3
"""
Descargador masivo para AlertasFullYomjai
Descarga las 35,000 fotos organizadamente
"""

import os
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
import json
from tqdm import tqdm

# CONFIGURACIÓN - EDITAR ESTOS VALORES
API_ID = 26005180  # API ID configurado
API_HASH = 'c86549df51d1b77f390fe79020fb0ff3'  # API Hash configurado
PHONE = '+526624152145'  # Número configurado

# Configuración del grupo
GROUP_NAME = 'AlertasFullYomjai'  # Nombre exacto confirmado
OUTPUT_BASE = '/Users/Shared/yolo11_project/data/telegram_alertas'

async def download_all_photos(client):
    """Descarga todas las fotos del grupo AlertasFullYomjai"""
    
    # Crear estructura de directorios
    os.makedirs(f"{OUTPUT_BASE}/raw", exist_ok=True)
    os.makedirs(f"{OUTPUT_BASE}/metadata", exist_ok=True)
    
    try:
        # Obtener el grupo
        print(f"🔍 Buscando grupo: {GROUP_NAME}")
        group = await client.get_entity(GROUP_NAME)
        print(f"✅ Grupo encontrado: {group.title}")
        
        # Obtener total de mensajes
        total_messages = await client.get_messages(group, limit=1)
        total_count = total_messages.total
        print(f"📊 Total de mensajes en el grupo: {total_count:,}")
        
        # Contadores
        downloaded = 0
        skipped = 0
        errors = 0
        metadata = []
        
        # Barra de progreso
        pbar = tqdm(total=total_count, desc="Procesando mensajes")
        
        # Iterar sobre TODOS los mensajes
        async for message in client.iter_messages(group, limit=None):
            pbar.update(1)
            
            # Solo procesar fotos
            if message.media and isinstance(message.media, MessageMediaPhoto):
                try:
                    # Generar nombre único
                    date_str = message.date.strftime("%Y%m%d_%H%M%S")
                    filename = f"alert_{date_str}_{message.id}.jpg"
                    filepath = os.path.join(OUTPUT_BASE, "raw", filename)
                    
                    # Verificar si ya existe
                    if os.path.exists(filepath):
                        skipped += 1
                        continue
                    
                    # Descargar foto
                    await message.download_media(filepath)
                    downloaded += 1
                    
                    # Guardar metadata
                    meta = {
                        'filename': filename,
                        'message_id': message.id,
                        'date': message.date.isoformat(),
                        'sender_id': message.sender_id,
                        'text': message.text or '',
                        'has_location': hasattr(message, 'geo') and message.geo is not None
                    }
                    metadata.append(meta)
                    
                    # Actualizar cada 100 fotos
                    if downloaded % 100 == 0:
                        pbar.set_postfix({
                            'Descargadas': downloaded,
                            'Omitidas': skipped,
                            'Errores': errors
                        })
                        
                        # Guardar metadata parcial
                        with open(f"{OUTPUT_BASE}/metadata/metadata_partial_{downloaded}.json", 'w') as f:
                            json.dump(metadata[-100:], f, indent=2, ensure_ascii=False)
                
                except Exception as e:
                    errors += 1
                    print(f"\n❌ Error descargando mensaje {message.id}: {e}")
        
        pbar.close()
        
        # Guardar metadata completa
        print("\n💾 Guardando metadata completa...")
        with open(f"{OUTPUT_BASE}/metadata/metadata_complete.json", 'w') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Estadísticas finales
        print("\n" + "="*60)
        print("✅ DESCARGA COMPLETA")
        print(f"📊 Total de mensajes procesados: {total_count:,}")
        print(f"🖼️  Fotos descargadas: {downloaded:,}")
        print(f"⏭️  Fotos omitidas (ya existían): {skipped:,}")
        print(f"❌ Errores: {errors}")
        print(f"💾 Tamaño aproximado: {(downloaded * 0.2):.1f} GB")
        print(f"📁 Ubicación: {OUTPUT_BASE}")
        print("="*60)
        
        # Análisis rápido
        if metadata:
            print("\n📈 Análisis rápido de las fotos:")
            
            # Por fecha
            dates = [datetime.fromisoformat(m['date']).date() for m in metadata]
            unique_dates = len(set(dates))
            print(f"📅 Días únicos con fotos: {unique_dates}")
            
            # Con texto
            with_text = sum(1 for m in metadata if m['text'])
            print(f"💬 Fotos con descripción: {with_text:,} ({with_text/len(metadata)*100:.1f}%)")
            
            # Guardar resumen
            summary = {
                'total_downloaded': downloaded,
                'total_skipped': skipped,
                'total_errors': errors,
                'unique_dates': unique_dates,
                'photos_with_text': with_text,
                'download_date': datetime.now().isoformat()
            }
            
            with open(f"{OUTPUT_BASE}/download_summary.json", 'w') as f:
                json.dump(summary, f, indent=2)
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        raise

async def main():
    # Verificar configuración
    if API_ID == 12345678 or API_HASH == 'tu_api_hash_aqui':
        print("⚠️  ERROR: Debes configurar API_ID y API_HASH primero!")
        print("Ve a https://my.telegram.org para obtener tus credenciales")
        return
    
    print("🚀 Iniciando descarga masiva de AlertasFullYomjai")
    print(f"📁 Las fotos se guardarán en: {OUTPUT_BASE}")
    print("-" * 60)
    
    # Crear sesión
    client = TelegramClient('alertas_yomjai_session', API_ID, API_HASH)
    
    try:
        # Conectar
        await client.start(PHONE)
        print("✅ Conectado a Telegram exitosamente")
        
        # Descargar
        await download_all_photos(client)
        
    except KeyboardInterrupt:
        print("\n⚠️  Descarga interrumpida por el usuario")
    finally:
        await client.disconnect()
        print("\n👋 Desconectado de Telegram")

if __name__ == '__main__':
    # Crear directorio base si no existe
    os.makedirs(OUTPUT_BASE, exist_ok=True)
    
    # Ejecutar
    asyncio.run(main())
