#!/usr/bin/env python3
"""
Script para iniciar el backend con todas las funcionalidades
"""

import subprocess
import time
import sys
import os

def start_backend():
    print("🚀 Iniciando Backend YOLO11 Security System...")
    print("-" * 50)
    
    # Cambiar al directorio del proyecto
    os.chdir('/Users/Shared/yolo11_project')
    
    # Comando para iniciar el backend
    cmd = [sys.executable, 'backend/main.py']
    
    try:
        # Iniciar el proceso
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print("✅ Backend iniciado con PID:", process.pid)
        print("\n📡 Servidor corriendo en: http://localhost:8888")
        print("🔌 WebSocket en: ws://localhost:8888/ws")
        print("\n📚 Endpoints disponibles:")
        print("  - GET  /api/health - Estado del sistema")
        print("  - GET  /api/cameras - Lista de cámaras")
        print("  - GET  /api/statistics - Estadísticas")
        print("  - POST /api/detect - Analizar imagen")
        print("\n🛑 Presiona Ctrl+C para detener\n")
        print("-" * 50)
        
        # Leer output en tiempo real
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
            
            # Verificar si el proceso sigue vivo
            if process.poll() is not None:
                break
                
    except KeyboardInterrupt:
        print("\n\n⏹️ Deteniendo backend...")
        process.terminate()
        process.wait()
        print("✅ Backend detenido correctamente")
    except Exception as e:
        print(f"❌ Error: {e}")
        
if __name__ == "__main__":
    start_backend()
