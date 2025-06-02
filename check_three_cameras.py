#!/usr/bin/env python3
"""
Verificar las 3 cámaras encontradas
"""

import socket
import requests
from concurrent.futures import ThreadPoolExecutor
import time

print("🔍 VERIFICACIÓN DE LAS 3 CÁMARAS HIKVISION")
print("=" * 50)

cameras = {
    '192.168.1.11': 'Cámara 1',
    '192.168.1.12': 'Cámara 2', 
    '192.168.1.39': 'Cámara 3'
}

def check_camera(ip):
    info = {'ip': ip, 'rtsp': False, 'http': False, 'http_port': None, 'hikvision': False}
    
    # Check RTSP
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, 554))
        sock.close()
        info['rtsp'] = (result == 0)
    except:
        pass
    
    # Check HTTP
    for port in [80, 8080]:
        try:
            resp = requests.get(f'http://{ip}:{port}', timeout=2)
            info['http'] = True
            info['http_port'] = port
            if 'hikvision' in resp.text.lower() or 'hik' in resp.text.lower():
                info['hikvision'] = True
            break
        except:
            pass
    
    return info

# Verificar todas las cámaras
print("\nVerificando cámaras...\n")

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(check_camera, ip): ip for ip in cameras.keys()}
    
    for future in futures:
        ip = futures[future]
        try:
            result = future.result()
            print(f"📹 {cameras[ip]} ({ip}):")
            print(f"   RTSP Puerto 554: {'✅ Abierto' if result['rtsp'] else '❌ Cerrado'}")
            print(f"   HTTP: {'✅ Activo' if result['http'] else '❌ No detectado'}")
            if result['http']:
                print(f"   Puerto Web: {result['http_port']}")
                print(f"   Hikvision: {'✅ Confirmado' if result['hikvision'] else '⚠️  No confirmado'}")
                print(f"   URL Web: http://{ip}:{result['http_port']}")
            print()
        except Exception as e:
            print(f"❌ Error verificando {ip}: {e}\n")

print("=" * 50)
print("📝 RESUMEN:")
print("\nPara agregar estas cámaras al sistema:")
print("1. Vaya a cada URL web y obtenga las credenciales")
print("2. En el dashboard: Configuración → Cámaras")
print("3. Use 'Buscar Cámaras' o 'Agregar Manual'")
print("4. Configure cada una con sus credenciales")
print("\n💡 URLS RTSP típicas de Hikvision:")
print("   - Nueva: rtsp://user:pass@IP:554/Streaming/Channels/101")
print("   - Antigua: rtsp://user:pass@IP:554/h264/ch1/main/av_stream")
