#!/usr/bin/env python3
"""
Script para crear sesión de Telegram y guardarla
Esto evitará pedir el código cada vez
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import json
import os

# Credenciales
API_ID = 26005180
API_HASH = 'c86549df51d1b77f390fe79020fb0ff3'
PHONE = '+526624152145'

# El código que proporcionaste
CODE = '28719'

async def create_session():
    """Crea y guarda la sesión de Telegram"""
    
    # Usar StringSession para poder guardarla
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    
    try:
        await client.connect()
        
        # Enviar número de teléfono
        print("📱 Enviando número de teléfono...")
        await client.send_code_request(PHONE)
        
        # Intentar usar el código proporcionado
        print(f"📝 Intentando con código: {CODE}")
        try:
            await client.sign_in(PHONE, CODE)
            print("✅ ¡Autenticación exitosa!")
            
            # Guardar la sesión
            session_string = client.session.save()
            
            # Guardar en archivo
            session_data = {
                'session': session_string,
                'phone': PHONE,
                'api_id': API_ID
            }
            
            with open('telegram_session.json', 'w') as f:
                json.dump(session_data, f)
            
            print("💾 Sesión guardada exitosamente")
            
            # Verificar grupos
            print("\n🔍 Buscando grupos...")
            dialogs = await client.get_dialogs()
            
            found_alertas = False
            for dialog in dialogs:
                if dialog.is_group and ('alertas' in dialog.name.lower() or 'yomjai' in dialog.name.lower()):
                    print(f"✅ Encontrado: {dialog.name}")
                    found_alertas = True
                    
                    # Guardar información del grupo
                    group_info = {
                        'name': dialog.name,
                        'id': dialog.id,
                        'access_hash': dialog.entity.access_hash if hasattr(dialog.entity, 'access_hash') else None
                    }
                    
                    with open('alertas_group_info.json', 'w') as f:
                        json.dump(group_info, f)
                    break
            
            if not found_alertas:
                print("❌ No se encontró el grupo AlertasFullYomjai")
                print("\nGrupos disponibles (primeros 10):")
                for i, dialog in enumerate(dialogs[:10]):
                    if dialog.is_group:
                        print(f"  {i+1}. {dialog.name}")
            
        except Exception as e:
            print(f"❌ Error con el código: {e}")
            print("\nEl código puede haber expirado. Por favor:")
            print("1. Ejecute 'python3 test_telegram.py' en Terminal")
            print("2. Ingrese el nuevo código que reciba")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        
    finally:
        await client.disconnect()

if __name__ == '__main__':
    print("🔐 Creando sesión de Telegram...")
    print("-" * 40)
    
    # Verificar si el código es reciente
    print("⚠️  NOTA: Este código debe ser usado dentro de 2 minutos de haberlo recibido")
    print(f"Código a usar: {CODE}")
    print()
    
    asyncio.run(create_session())
