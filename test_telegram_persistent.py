#!/usr/bin/env python3
"""
Script de prueba para el sistema de alertas Telegram persistentes
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.telegram_service import telegram_service
from backend.utils.telegram_alert_manager import TelegramAlertManager
from datetime import datetime
import json

async def test_persistent_alerts():
    """Probar el sistema de alertas persistentes"""
    
    print("🧪 Iniciando prueba de alertas Telegram persistentes...")
    
    # Configurar servicio de Telegram (usar credenciales reales)
    config_path = "backend/configs/notification_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            telegram_config = config.get('telegram', {})
            
            if telegram_config.get('enabled'):
                telegram_service.configure(
                    bot_token=telegram_config.get('bot_token'),
                    chat_id=telegram_config.get('chat_id'),
                    enabled=True
                )
                print("✅ Telegram configurado correctamente")
            else:
                print("❌ Telegram no está habilitado en la configuración")
                return
    else:
        print("❌ No se encontró archivo de configuración")
        return
    
    # Crear gestor de alertas
    alert_manager = TelegramAlertManager(telegram_service)
    
    # Iniciar monitoreo
    await alert_manager.start_monitoring()
    print("✅ Monitor de alertas iniciado")
    
    # Simular una alerta
    print("\n📱 Creando alerta de prueba para 'Entrada Principal'...")
    await alert_manager.create_alert(
        zone_id="entrance_door_0",
        zone_name="Entrada Principal",
        camera_id="cam_001"
    )
    
    print("\n⏰ La alerta enviará mensajes cada 5 segundos")
    print("Observa los mensajes en Telegram...")
    print("\nPresiona Ctrl+C para detener la prueba")
    
    try:
        # Mantener el script corriendo
        while True:
            # Mostrar estadísticas
            stats = alert_manager.get_alert_statistics()
            active_alerts = alert_manager.get_active_alerts()
            
            print(f"\r📊 Alertas activas: {stats['total_active_alerts']} | "
                  f"Mensajes enviados: {stats['total_messages_sent']}", end='', flush=True)
            
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo prueba...")
        
        # Cancelar todas las alertas
        alert_manager.cancel_all_alerts()
        print("✅ Alertas canceladas")
        
        # Detener monitoreo
        await alert_manager.stop_monitoring()
        print("✅ Monitor detenido")

async def test_escalation():
    """Probar el escalamiento de intervalos"""
    
    print("\n🧪 Probando escalamiento de intervalos...")
    
    # Configurar Telegram
    config_path = "backend/configs/notification_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            telegram_config = config.get('telegram', {})
            
            telegram_service.configure(
                bot_token=telegram_config.get('bot_token'),
                chat_id=telegram_config.get('chat_id'),
                enabled=True
            )
    
    # Crear gestor
    alert_manager = TelegramAlertManager(telegram_service)
    await alert_manager.start_monitoring()
    
    # Crear alerta de emergencia (intervalo inicial 3s)
    print("\n🚨 Creando alerta de EMERGENCIA (intervalos cortos)...")
    await alert_manager.create_alert(
        zone_id="emergency_exit",
        zone_name="Salida de Emergencia",
        camera_id="cam_003"
    )
    
    print("\nEscalamiento esperado:")
    print("- Mensaje 1: Inmediato")
    print("- Mensaje 2: +3 segundos") 
    print("- Mensaje 3: +10 segundos")
    print("- Mensaje 4: +20 segundos")
    print("- Mensaje 5+: +30 segundos")
    
    print("\nObserva el escalamiento en Telegram...")
    print("Presiona Ctrl+C para detener\n")
    
    try:
        start_time = datetime.now()
        while True:
            elapsed = (datetime.now() - start_time).total_seconds()
            active = alert_manager.get_active_alerts()
            
            if "emergency_exit" in active:
                alert = active["emergency_exit"]
                print(f"\r⏱️ Tiempo: {elapsed:.0f}s | "
                      f"Mensajes: {alert['send_count']} | "
                      f"Próximo en: {alert['next_interval']}s", end='', flush=True)
            
            await asyncio.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n✅ Prueba completada")
        alert_manager.cancel_all_alerts()
        await alert_manager.stop_monitoring()

async def main():
    """Menú principal de pruebas"""
    
    print("🚀 YOMJAI - Prueba de Alertas Telegram Persistentes")
    print("=" * 50)
    print("\nSelecciona una prueba:")
    print("1. Prueba básica de alertas persistentes")
    print("2. Prueba de escalamiento de intervalos")
    print("3. Salir")
    
    choice = input("\nOpción: ")
    
    if choice == "1":
        await test_persistent_alerts()
    elif choice == "2":
        await test_escalation()
    else:
        print("👋 Saliendo...")

if __name__ == "__main__":
    asyncio.run(main())
