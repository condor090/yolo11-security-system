#!/usr/bin/env python3
"""
Escáner de Cámaras Hikvision en la Red
Ayuda a encontrar las IPs de las cámaras
"""

import socket
import subprocess
import platform
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.auth import HTTPDigestAuth
import warnings
warnings.filterwarnings('ignore')

def get_network_range():
    """Obtener el rango de red local"""
    try:
        # Obtener IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Calcular rango de red (asumiendo /24)
        network = ipaddress.ip_network(f"{local_ip}/24", strict=False)
        return network
    except:
        return ipaddress.ip_network("192.168.1.0/24")

def check_hikvision_http(ip, timeout=2):
    """Verificar si es una cámara Hikvision por HTTP"""
    ports = [80, 8080]
    
    for port in ports:
        try:
            # Intentar acceder a la página de login
            url = f"http://{ip}:{port}"
            response = requests.get(url, timeout=timeout, verify=False)
            
            # Buscar indicadores de Hikvision
            if any(indicator in response.text.lower() for indicator in ['hikvision', 'hik', 'dvr', 'nvr']):
                return True, port
        except:
            pass
    
    return False, None

def check_rtsp_port(ip, port=554, timeout=1):
    """Verificar si el puerto RTSP está abierto"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((str(ip), port))
        sock.close()
        return result == 0
    except:
        return False

def scan_network():
    """Escanear la red en busca de cámaras Hikvision"""
    print("🔍 ESCÁNER DE CÁMARAS HIKVISION")
    print("=" * 50)
    
    # Obtener rango de red
    network = get_network_range()
    print(f"📡 Escaneando red: {network}")
    print(f"📊 Total de IPs a escanear: {network.num_addresses - 2}")
    print("\n⏳ Esto puede tomar 1-2 minutos...\n")
    
    found_cameras = []
    
    # Escanear en paralelo para mayor velocidad
    with ThreadPoolExecutor(max_workers=50) as executor:
        # Crear lista de IPs a escanear
        ips_to_scan = [ip for ip in network.hosts()]
        
        # Verificar cada IP
        futures = {}
        for ip in ips_to_scan:
            futures[executor.submit(check_rtsp_port, str(ip))] = ip
        
        # Procesar resultados
        checked = 0
        for future in futures:
            ip = futures[future]
            checked += 1
            
            # Mostrar progreso
            if checked % 10 == 0:
                print(f"Progreso: {checked}/{len(ips_to_scan)} IPs verificadas...", end='\r')
            
            try:
                has_rtsp = future.result()
                if has_rtsp:
                    # Verificar si es Hikvision
                    is_hik, http_port = check_hikvision_http(str(ip))
                    
                    camera_info = {
                        'ip': str(ip),
                        'rtsp_port': 554,
                        'http_port': http_port,
                        'confirmed_hikvision': is_hik
                    }
                    
                    found_cameras.append(camera_info)
                    
                    if is_hik:
                        print(f"\n✅ Cámara Hikvision encontrada: {ip}")
                    else:
                        print(f"\n⚠️  Posible cámara (RTSP activo): {ip}")
                        
            except Exception as e:
                pass
    
    print("\n\n" + "=" * 50)
    
    return found_cameras

def test_rtsp_url(ip, username='admin', password='12345'):
    """Generar y mostrar URL RTSP de prueba"""
    urls = [
        f"rtsp://{username}:{password}@{ip}:554/Streaming/Channels/101",
        f"rtsp://{username}:{password}@{ip}:554/h264/ch1/main/av_stream",
        f"rtsp://{username}:{password}@{ip}:554/cam/realmonitor?channel=1&subtype=0"
    ]
    
    print(f"\n📹 URLs RTSP para probar en VLC:")
    for i, url in enumerate(urls, 1):
        print(f"   {i}. {url}")

def show_results(cameras):
    """Mostrar resultados del escaneo"""
    if not cameras:
        print("❌ No se encontraron cámaras en la red")
        print("\n💡 Sugerencias:")
        print("   - Verificar que las cámaras estén encendidas")
        print("   - Verificar que estén en la misma red")
        print("   - Deshabilitar VPN si está activa")
        print("   - Verificar firewall")
    else:
        print(f"\n🎉 RESUMEN: {len(cameras)} dispositivo(s) encontrado(s)")
        print("\n📋 DISPOSITIVOS DETECTADOS:\n")
        
        for i, cam in enumerate(cameras, 1):
            print(f"{i}. IP: {cam['ip']}")
            print(f"   Puerto RTSP: {cam['rtsp_port']}")
            
            if cam['http_port']:
                print(f"   Puerto HTTP: {cam['http_port']}")
                print(f"   Web: http://{cam['ip']}:{cam['http_port']}")
            
            if cam['confirmed_hikvision']:
                print(f"   ✅ Confirmado: HIKVISION")
            else:
                print(f"   ⚠️  Tipo: Cámara IP genérica")
            
            # Mostrar URLs de prueba
            test_rtsp_url(cam['ip'])
            print()

def main():
    """Función principal"""
    try:
        cameras = scan_network()
        show_results(cameras)
        
        if cameras:
            print("\n🚀 SIGUIENTE PASO:")
            print("1. Probar las URLs en VLC (Media → Abrir ubicación de red)")
            print("2. Si funciona, agregar la cámara en el Dashboard")
            print("3. Usar la IP y credenciales correctas")
            
            print("\n📝 CREDENCIALES COMUNES:")
            print("   - admin / 12345")
            print("   - admin / admin")
            print("   - admin / (vacío)")
            print("   - admin / password")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Escaneo cancelado")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
