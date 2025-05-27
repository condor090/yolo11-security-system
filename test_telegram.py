#!/usr/bin/env python3
"""
Script de diagnóstico para verificar conexión con Telegram
"""

import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import getpass

# Credenciales
API_ID = 26005180
API_HASH = 'c86549df51d1b77f390fe79020fb0ff3'
PHONE = '+526624152145'

async def test_connection():
    """Prueba la conexión y lista los grupos"""
    
    client = TelegramClient('test_session', API_ID, API_HASH)
    
    try:
        await client.start(PHONE)
        print("✅ Conectado exitosamente!")
        
        # Obtener información del usuario
        me = await client.get_me()
        print(f"👤 Usuario: {me.first_name} {me.last_name or ''}")
        print(f"📱 Teléfono: {me.phone}")
        
        # Listar grupos
        print("\n📋 Buscando grupos...")
        dialogs = await client.get_dialogs()
        
        groups = []
        for dialog in dialogs:
            if dialog.is_group:
                groups.append(dialog)
                
        print(f"\n🔍 Encontrados {len(groups)} grupos:")
        for i, group in enumerate(groups[:10], 1):  # Mostrar solo los primeros 10
            print(f"{i}. {group.name}")
            
        # Buscar específicamente AlertasFullYomjai
        print("\n🎯 Buscando 'AlertasFullYomjai'...")
        found = False
        for dialog in dialogs:
            if 'alertas' in dialog.name.lower() or 'yomjai' in dialog.name.lower():
                print(f"✅ Encontrado: {dialog.name} (ID: {dialog.id})")
                found = True
                
        if not found:
            print("❌ No se encontró un grupo con 'AlertasFullYomjai' en el nombre")
            print("\nNombres similares encontrados:")
            for dialog in dialogs:
                if dialog.is_group and ('alert' in dialog.name.lower() or 
                                       'yom' in dialog.name.lower() or 
                                       'full' in dialog.name.lower()):
                    print(f"  - {dialog.name}")
        
    except SessionPasswordNeededError:
        print("\n🔐 Se requiere contraseña de dos factores")
        password = getpass.getpass('Ingrese su contraseña de 2FA: ')
        await client.sign_in(password=password)
        print("✅ Autenticación 2FA exitosa!")
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"Detalles: {e}")
        
    finally:
        await client.disconnect()

if __name__ == '__main__':
    print("🔍 Script de diagnóstico Telegram")
    print("-" * 40)
    asyncio.run(test_connection())
