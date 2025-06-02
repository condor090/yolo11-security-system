#!/usr/bin/env python3
"""
Probar URLs RTSP para la cámara con las credenciales correctas
"""

import cv2
import time

# Credenciales detectadas
IP = "192.168.1.11"
USERNAME = "admin"
PASSWORD = "Mayocabo1"

print("🔍 PROBANDO URLS RTSP PARA HIKVISION")
print("=" * 50)
print(f"IP: {IP}")
print(f"Usuario: {USERNAME}")
print(f"Contraseña: {'*' * len(PASSWORD)}")
print()

# URLs a probar (en orden de probabilidad)
urls_to_test = [
    f"rtsp://{USERNAME}:{PASSWORD}@{IP}:554/Streaming/Channels/101",     # Más común nueva
    f"rtsp://{USERNAME}:{PASSWORD}@{IP}:554/Streaming/Channels/1",       # Sin ceros
    f"rtsp://{USERNAME}:{PASSWORD}@{IP}:554/Streaming/channels/101",     # minúsculas
    f"rtsp://{USERNAME}:{PASSWORD}@{IP}:554/h264/ch1/main/av_stream",    # Formato antiguo
    f"rtsp://{USERNAME}:{PASSWORD}@{IP}:554/cam/realmonitor?channel=1&subtype=0",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP}:554/Streaming/Channels/102",     # Substream
    f"rtsp://{USERNAME}:{PASSWORD}@{IP}:554/live/ch00_0",                # Otro formato
    f"rtsp://{USERNAME}:{PASSWORD}@{IP}:554/",                           # Raíz
]

print("Probando diferentes URLs RTSP...")
print()

for i, url in enumerate(urls_to_test, 1):
    print(f"Prueba {i}/{len(urls_to_test)}: {url.replace(PASSWORD, '****')}")
    
    try:
        cap = cv2.VideoCapture(url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Esperar un poco para la conexión
        time.sleep(2)
        
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✅ ¡ÉXITO! Esta URL funciona")
            print(f"   Resolución: {frame.shape[1]}x{frame.shape[0]}")
            print(f"   FPS: {int(cap.get(cv2.CAP_PROP_FPS))}")
            print()
            print("📝 USA ESTA CONFIGURACIÓN EN EL DASHBOARD:")
            print(f"   IP: {IP}")
            print(f"   Puerto: 554")
            print(f"   Usuario: {USERNAME}")
            print(f"   Contraseña: {PASSWORD}")
            
            # Determinar canal y stream basado en la URL
            if "101" in url or "/1" in url:
                print(f"   Canal: 1")
                print(f"   Stream: main")
            elif "102" in url:
                print(f"   Canal: 1")
                print(f"   Stream: sub")
                
            print()
            print("💡 IMPORTANTE: La URL correcta es diferente a la que genera el sistema")
            print("   El sistema genera: /Streaming/Channels/100")
            print(f"   La correcta es: {url.split('554')[1].split('?')[0]}")
            
            cap.release()
            break
        else:
            print(f"❌ No funciona")
            
        cap.release()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()

else:
    print("❌ Ninguna URL funcionó")
    print()
    print("🔧 POSIBLES CAUSAS:")
    print("1. La cámara puede usar un formato RTSP no estándar")
    print("2. Puede requerir autenticación digest en lugar de basic")
    print("3. El firmware puede tener una ruta RTSP personalizada")
    print()
    print("💡 RECOMENDACIONES:")
    print("1. Accede a http://192.168.1.11 con admin/Mayocabo1")
    print("2. Busca en configuración la URL RTSP exacta")
    print("3. O busca el modelo exacto de la cámara para su documentación")
