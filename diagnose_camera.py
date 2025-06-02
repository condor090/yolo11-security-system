#!/usr/bin/env python3
"""
Diagnóstico de conexión de cámara Hikvision
"""

import requests
import cv2
import time
from requests.auth import HTTPDigestAuth, HTTPBasicAuth

# Datos de la cámara
IP = "192.168.1.11"
USERNAME = "admin"
PASSWORDS = ["12345", "admin", "password", "123456", "admin123", ""]  # Contraseñas comunes

print("🔍 DIAGNÓSTICO DE CÁMARA HIKVISION")
print("=" * 50)
print(f"IP: {IP}")
print()

# 1. Verificar acceso HTTP
print("1️⃣ Verificando acceso HTTP...")
for port in [80, 8080]:
    try:
        url = f"http://{IP}:{port}"
        response = requests.get(url, timeout=3)
        print(f"   ✅ Puerto {port} abierto - Status: {response.status_code}")
        
        # Verificar si es Hikvision
        if 'hikvision' in response.text.lower():
            print(f"   ✅ Confirmado: Es una cámara Hikvision")
            print(f"   🌐 Interfaz web: {url}")
    except:
        print(f"   ❌ Puerto {port} cerrado o sin respuesta")

# 2. Probar URLs RTSP comunes
print("\n2️⃣ Probando URLs RTSP...")
rtsp_urls = [
    f"rtsp://{USERNAME}:PASSWORD@{IP}:554/Streaming/Channels/101",  # Nuevo formato
    f"rtsp://{USERNAME}:PASSWORD@{IP}:554/Streaming/Channels/1",
    f"rtsp://{USERNAME}:PASSWORD@{IP}:554/h264/ch1/main/av_stream",  # Formato antiguo
    f"rtsp://{USERNAME}:PASSWORD@{IP}:554/cam/realmonitor?channel=1&subtype=0",
    f"rtsp://{USERNAME}:PASSWORD@{IP}:554/PSIA/streaming/channels/101"
]

print("\n📝 URLs RTSP para probar en VLC:")
for url in rtsp_urls[:3]:
    print(f"   {url.replace('PASSWORD', '****')}")

# 3. Intentar conexión con OpenCV
print("\n3️⃣ Probando conexión RTSP con credenciales comunes...")
successful_password = None

for password in PASSWORDS:
    for url_template in rtsp_urls[:2]:  # Probar solo los 2 formatos más comunes
        url = url_template.replace('PASSWORD', password)
        print(f"\n   Probando con contraseña: {'(vacía)' if password == '' else '*' * len(password)}")
        
        try:
            cap = cv2.VideoCapture(url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Dar tiempo para conectar
            time.sleep(2)
            
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"   ✅ ¡CONEXIÓN EXITOSA!")
                print(f"   ✅ Contraseña correcta: {password if password else '(sin contraseña)'}")
                print(f"   ✅ Resolución: {frame.shape[1]}x{frame.shape[0]}")
                successful_password = password
                cap.release()
                break
            cap.release()
        except Exception as e:
            pass
    
    if successful_password is not None:
        break

if successful_password is None:
    print("\n   ❌ No se pudo conectar con las contraseñas comunes")

# 4. Recomendaciones
print("\n4️⃣ RECOMENDACIONES:")
print("=" * 50)

if successful_password is not None:
    print(f"✅ La cámara está funcionando correctamente")
    print(f"✅ Usuario: {USERNAME}")
    print(f"✅ Contraseña: {successful_password if successful_password else '(sin contraseña)'}")
    print(f"\n🔧 En el dashboard, actualiza la cámara con:")
    print(f"   - Usuario: {USERNAME}")
    print(f"   - Contraseña: {successful_password}")
else:
    print("❌ No se pudo conectar automáticamente")
    print("\n🔧 Pasos a seguir:")
    print("1. Accede a la interfaz web de la cámara:")
    print(f"   http://{IP}")
    print("\n2. Verifica el usuario y contraseña correctos")
    print("\n3. Prueba estas URLs en VLC con tus credenciales:")
    for url in rtsp_urls[:2]:
        print(f"   {url.replace('PASSWORD', 'tu_contraseña')}")
    print("\n4. Una vez que funcione en VLC, actualiza en el dashboard")

print("\n💡 TIPS:")
print("- Las cámaras Hikvision nuevas usan: /Streaming/Channels/101")
print("- Las antiguas usan: /h264/ch1/main/av_stream")
print("- El usuario por defecto suele ser 'admin'")
print("- Contraseñas comunes: 12345, admin, 123456")
print("- Algunas cámaras requieren activación inicial vía web")
