#!/usr/bin/env python3
"""
Script interactivo para probar las credenciales de la cámara
"""
import os
import cv2
import time

def test_camera_credentials():
    print("🎥 Configurador de Cámara RTSP")
    print("=" * 60)
    
    # IP predeterminada
    ip = input("\nIngrese la IP de la cámara [192.168.1.11]: ").strip() or "192.168.1.11"
    
    # Usuario predeterminado
    username = input("Ingrese el usuario [admin]: ").strip() or "admin"
    
    # Contraseña
    import getpass
    password = getpass.getpass("Ingrese la contraseña: ")
    
    if not password:
        print("⚠️  La contraseña es requerida")
        return
    
    print(f"\n📡 Probando conexión con {ip}...")
    print(f"   Usuario: {username}")
    print(f"   Contraseña: {'*' * len(password)}")
    
    # URLs comunes de Hikvision
    urls = [
        f"rtsp://{username}:{password}@{ip}:554/Streaming/Channels/101",
        f"rtsp://{username}:{password}@{ip}:554/Streaming/Channels/1",
        f"rtsp://{username}:{password}@{ip}:554/ch1/main/av_stream",
        f"rtsp://{username}:{password}@{ip}:554/h264/ch1/main/av_stream",
    ]
    
    working_url = None
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Probando formato {i}...")
        
        try:
            cap = cv2.VideoCapture(url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Esperar conexión
            time.sleep(2)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ ¡ÉXITO! Formato {i} funciona")
                    working_url = url
                    cap.release()
                    break
                else:
                    print(f"❌ Conectado pero sin frames")
            else:
                print(f"❌ No conectado")
                
            cap.release()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    if working_url:
        print("\n" + "="*60)
        print("🎉 ¡Cámara configurada exitosamente!")
        print("\nPara activar la cámara en el sistema:")
        print("1. Ve a la pestaña Configuración > Cámaras")
        print("2. Actualiza los siguientes campos:")
        print(f"   - Usuario: {username}")
        print(f"   - Contraseña: {password}")
        print(f"   - Canal/Stream: /Streaming/Channels/101")
        print("\n¿Desea actualizar automáticamente el archivo de configuración? (s/n): ", end="")
        
        if input().lower() == 's':
            # Actualizar configuración
            import json
            config_path = "/Users/Shared/yolo11_project/backend/cameras/camera_config.json"
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            config["cam_001"]["username"] = username
            config["cam_001"]["password"] = password
            config["cam_001"]["ip"] = ip
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Configuración actualizada")
            print("🔄 Reinicie el backend para aplicar los cambios")
    else:
        print("\n❌ No se pudo conectar con la cámara")
        print("\nPosibles soluciones:")
        print("1. Verifique que la IP sea correcta")
        print("2. Verifique las credenciales")
        print("3. Asegúrese de que RTSP esté habilitado en la cámara")
        print("4. Verifique que el puerto 554 esté abierto")

if __name__ == "__main__":
    test_camera_credentials()
