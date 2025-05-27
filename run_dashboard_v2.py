#!/usr/bin/env python3
"""
Script de lanzamiento rápido para el Dashboard V2
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Ruta al dashboard V2
    dashboard_path = Path(__file__).parent / 'project_files' / 'apps' / 'security_dashboard_v2.py'
    
    if not dashboard_path.exists():
        print(f"❌ Error: No se encuentra el dashboard en {dashboard_path}")
        sys.exit(1)
    
    print("🚀 Iniciando Sistema de Seguridad YOLO11 V2")
    print("=" * 60)
    print("Características principales:")
    print("  ⏱️  Temporizadores configurables por zona")
    print("  🔊 Sistema de alarma sonora")
    print("  📊 Monitor en tiempo real")
    print("  🎯 Detección de puertas con 99.39% precisión")
    print("=" * 60)
    print("\nAbriendo dashboard en el navegador...\n")
    
    # Ejecutar streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8502",  # Puerto diferente para no conflicto
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard cerrado correctamente")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
