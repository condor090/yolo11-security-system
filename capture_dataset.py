#!/usr/bin/env python3
"""
Capturador de imágenes para re-entrenamiento
Captura frames de las cámaras para crear nuevo dataset
"""

import cv2
import os
import time
import json
from datetime import datetime
from pathlib import Path
import asyncio
import aiohttp

class DatasetCapture:
    def __init__(self, output_dir="captured_dataset", interval=5):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.interval = interval
        self.api_url = "http://localhost:8889"
        
    async def capture_frames(self):
        """Capturar frames de todas las cámaras activas"""
        print("🎥 Iniciando captura de dataset...")
        print(f"📁 Guardando en: {self.output_dir}")
        print(f"⏱️  Intervalo: {self.interval} segundos")
        print("\n[Presiona Ctrl+C para detener]\n")
        
        session = aiohttp.ClientSession()
        frame_count = 0
        
        try:
            while True:
                # Obtener lista de cámaras
                async with session.get(f"{self.api_url}/api/cameras") as response:
                    data = await response.json()
                    cameras = data.get('cameras', {})
                
                for cam_id, cam_info in cameras.items():
                    if cam_info.get('connected'):
                        # Obtener frame actual
                        async with session.get(f"{self.api_url}/api/cameras/{cam_id}/stream") as response:
                            if response.status == 200:
                                frame_data = await response.json()
                                
                                # Decodificar imagen base64
                                import base64
                                import numpy as np
                                
                                img_data = frame_data['image'].split(',')[1]
                                img_bytes = base64.b64decode(img_data)
                                nparr = np.frombuffer(img_bytes, np.uint8)
                                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                
                                # Guardar imagen
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"{cam_id}_{timestamp}_{frame_count:04d}.jpg"
                                filepath = self.output_dir / filename
                                
                                cv2.imwrite(str(filepath), img)
                                frame_count += 1
                                
                                print(f"✅ Capturado: {filename} - Frame #{frame_count}")
                
                # Esperar intervalo
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            print(f"\n\n🏁 Captura detenida")
            print(f"📊 Total de frames capturados: {frame_count}")
            print(f"📁 Guardados en: {self.output_dir}")
            
            # Crear archivo de metadata
            metadata = {
                "total_frames": frame_count,
                "capture_date": datetime.now().isoformat(),
                "interval_seconds": self.interval,
                "cameras": list(cameras.keys())
            }
            
            with open(self.output_dir / "capture_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
                
        finally:
            await session.close()

    def create_labelimg_script(self):
        """Crear script para etiquetar con LabelImg"""
        script_content = """#!/bin/bash
# Script para etiquetar imágenes con LabelImg

echo "🏷️  Preparando etiquetado de dataset..."

# Crear archivo de clases
echo "gate_open" > classes.txt
echo "gate_closed" >> classes.txt

# Verificar si LabelImg está instalado
if ! command -v labelImg &> /dev/null; then
    echo "📦 Instalando LabelImg..."
    pip install labelImg
fi

echo "🚀 Iniciando LabelImg..."
echo "📌 Instrucciones:"
echo "   1. Usa 'w' para crear bounding box"
echo "   2. Selecciona 'gate_open' o 'gate_closed'"
echo "   3. Guarda con Ctrl+S"
echo "   4. Siguiente imagen con 'd'"
echo ""

labelImg captured_dataset classes.txt
"""
        
        script_path = self.output_dir.parent / "label_dataset.sh"
        with open(script_path, "w") as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        print(f"\n📝 Script de etiquetado creado: {script_path}")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Capturador de dataset para re-entrenamiento")
    parser.add_argument("--interval", type=int, default=5, help="Segundos entre capturas")
    parser.add_argument("--output", default="captured_dataset", help="Directorio de salida")
    
    args = parser.parse_args()
    
    capturer = DatasetCapture(args.output, args.interval)
    capturer.create_labelimg_script()
    await capturer.capture_frames()

if __name__ == "__main__":
    asyncio.run(main())
