// Zonas de exclusión para ignorar áreas problemáticas
export const EXCLUSION_ZONES = {
  cam_001: [
    {
      name: "Ventana falsa",
      x1: 100,
      y1: 50,
      x2: 300,
      y2: 200
    }
  ]
};

// Función para filtrar detecciones
export function filterDetections(detections, cameraId) {
  const zones = EXCLUSION_ZONES[cameraId] || [];
  
  return detections.filter(det => {
    const bbox = det.bbox;
    
    // Verificar si la detección está en zona excluida
    for (const zone of zones) {
      if (bbox.x1 >= zone.x1 && bbox.y1 >= zone.y1 &&
          bbox.x2 <= zone.x2 && bbox.y2 <= zone.y2) {
        return false; // Excluir esta detección
      }
    }
    
    return true; // Mantener la detección
  });
}