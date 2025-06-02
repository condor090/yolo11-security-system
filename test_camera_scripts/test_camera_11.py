#!/usr/bin/env python3
"""
Test de conexión para cámara Hikvision en 192.168.1.11
"""
import cv2
import time

def test_rtsp_urls(ip, username="admin", password="Admin123"):
    """Prueba diferentes URLs RTSP comunes para Hikvision"""
    
    urls_to_test = [
        # Formato más común de Hikvision
        f"rtsp://{username}:{password}@{ip}:554/Streaming/Channels/101",
        f"rtsp://{username}:{password}@{ip}:554/Streaming/Channels/1",
        f"rtsp://{username}:{password}@{ip}:554/ch1/main/av_stream",
        f"rtsp://{username}:{password}@{ip}:554/live/ch00_0",
        f"rtsp://{username}:{password}@{ip}:554/cam/realmonitor?channel=1&subtype=0",
        # Sin autenticación (por si está configurada así)
        f"rtsp://{ip}:554/Streaming/Channels/101",
        f"rtsp://{ip}:554/Streaming/Channels/1",
    ]
    
    print(f"🎥 Probando conexión con cámara en {ip}")
    print("=" * 60)
    
    for i, url in enumerate(urls_to_test, 1):
        print(f"\n[{i}/{len(urls_to_test)}] Probando: {url.replace(password, '*' * len(password))}")
        
        try:
            cap = cv2.VideoCapture(url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Esperar un momento para la conexión
            time.sleep(2)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"✅ ¡ÉXITO! Conexión establecida")
                    print(f"   Resolución: {width}x{height}")
                    print(f"   URL correcta: {url.replace(password, '*' * len(password))}")
                    
                    # Guardar un frame de prueba
                    cv2.imwrite(f'/Users/Shared/yolo11_project/test_camera_scripts/test_frame_{ip.replace(".", "_")}.jpg', frame)
                    print(f"   Frame guardado como test_frame_{ip.replace('.', '_')}.jpg")
                    
                    cap.release()
                    return url
                else:
                    print("❌ Conectado pero no se pueden leer frames")
            else:
                print("❌ No se pudo abrir la conexión")
                
            cap.release()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n❌ No se pudo conectar con ninguna URL")
    print("\n💡 Sugerencias:")
    print("1. Verifica que la IP sea correcta: ping", ip)
    print("2. Verifica las credenciales (usuario/contraseña)")
    print("3. Asegúrate de que RTSP esté habilitado en la cámara")
    print("4. Revisa que el puerto 554 esté abierto")
    
    return None

if __name__ == "__main__":
    # Probar con la cámara
    result = test_rtsp_urls("192.168.1.11")
    
    if result:
        print("\n" + "=" * 60)
        print("🎉 ¡Cámara lista para usar!")
        print(f"URL RTSP funcional: {result.replace('Admin123', '*' * 8)}")
        print("\nPara actualizar la configuración en el sistema:")
        print("1. Ve a la pestaña Configuración")
        print("2. Actualiza los campos de la cámara")
        print("3. El sistema se reconectará automáticamente")
