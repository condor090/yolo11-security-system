import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Maximize2, Minimize2, Camera, Loader, 
  AlertCircle, RefreshCw, ZoomIn, ZoomOut,
  Download, Settings, Wifi, WifiOff, Eye, EyeOff,
  Leaf, AlertTriangle, Zap
} from 'lucide-react';
import MjpegStream from './MjpegStream';

export default function VideoStream({ 
  cameraId, 
  cameraName = "Cámara",
  showControls = true,
  enableDetections = true,
  className = "",
  onError = null,
  onDetection = null
}) {
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fps, setFps] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [useMjpeg, setUseMjpeg] = useState(false);
  const [detections, setDetections] = useState([]);
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(true);
  const reconnectAttempts = useRef(0);
  
  // Estadísticas
  const frameCount = useRef(0);
  const lastFpsUpdate = useRef(Date.now());

  useEffect(() => {
    if (!cameraId) return;

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [cameraId]);

  const connectWebSocket = () => {
    setIsLoading(true);
    setError(null);

    const ws = new WebSocket(`ws://localhost:8889/ws/camera/${cameraId}`);
    ws.binaryType = 'arraybuffer';
    
    ws.onopen = () => {
      console.log(`WebSocket conectado para cámara ${cameraId}`);
      setIsConnected(true);
      setIsLoading(false);
      reconnectAttempts.current = 0;
    };

    ws.onmessage = async (event) => {
      try {
        // El backend envía metadata + frame en formato binario
        const arrayBuffer = event.data;
        const dataView = new DataView(arrayBuffer);
        
        // Leer longitud de metadata (primeros 4 bytes)
        const metadataLength = dataView.getUint32(0);
        
        // Extraer metadata JSON
        const metadataBytes = new Uint8Array(arrayBuffer, 4, metadataLength);
        const metadataJson = new TextDecoder().decode(metadataBytes);
        const metadata = JSON.parse(metadataJson);
        
        // Actualizar detecciones
        if (metadata.detections) {
          setDetections(metadata.detections);
          if (onDetection && metadata.detections.length > 0) {
            onDetection(metadata.detections);
          }
        }
        
        // Extraer frame JPEG (ya tiene las detecciones dibujadas por el backend)
        const frameStart = 4 + metadataLength;
        const frameBlob = new Blob([arrayBuffer.slice(frameStart)], { type: 'image/jpeg' });
        const imageUrl = URL.createObjectURL(frameBlob);
        
        const img = new Image();
        img.onload = () => {
          const canvas = canvasRef.current;
          if (canvas) {
            const ctx = canvas.getContext('2d');
            
            // Ajustar canvas al tamaño de la imagen
            if (canvas.width !== img.width || canvas.height !== img.height) {
              canvas.width = img.width;
              canvas.height = img.height;
            }
            
            // Limpiar y dibujar con zoom
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (zoom !== 1) {
              ctx.save();
              ctx.translate(canvas.width/2, canvas.height/2);
              ctx.scale(zoom, zoom);
              ctx.translate(-canvas.width/2, -canvas.height/2);
            }
            
            // Dibujar imagen (ya tiene las detecciones del backend)
            ctx.drawImage(img, 0, 0);
            
            if (zoom !== 1) {
              ctx.restore();
            }
            
            // Limpiar URL
            URL.revokeObjectURL(imageUrl);
            
            // Actualizar FPS
            updateFPS();
          }
        };
        
        img.src = imageUrl;
        
      } catch (error) {
        console.error('Error procesando frame:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Error de conexión');
      setIsConnected(false);
      reconnectAttempts.current++;
      
      // Si falla más de 3 veces, cambiar a MJPEG
      if (reconnectAttempts.current > 3) {
        console.log('Cambiando a MJPEG después de múltiples fallos');
        setUseMjpeg(true);
      }
      
      if (onError) onError(error);
    };

    ws.onclose = () => {
      console.log('WebSocket desconectado');
      setIsConnected(false);
      
      // Reconectar después de 3 segundos si no es cierre intencional
      if (!useMjpeg) {
        setTimeout(() => {
          if (wsRef.current === ws) {
            connectWebSocket();
          }
        }, 3000);
      }
    };

    wsRef.current = ws;
  };

  const updateFPS = () => {
    frameCount.current++;
    const now = Date.now();
    const elapsed = now - lastFpsUpdate.current;
    
    if (elapsed >= 1000) {
      setFps(Math.round((frameCount.current * 1000) / elapsed));
      frameCount.current = 0;
      lastFpsUpdate.current = now;
    }
  };

  const handleFullscreen = () => {
    const container = canvasRef.current?.parentElement;
    if (!container) return;

    if (!isFullscreen) {
      if (container.requestFullscreen) {
        container.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.25, 1));
  };

  const handleSnapshot = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.toBlob((blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `snapshot_${cameraId}_${Date.now()}.jpg`;
      a.click();
      URL.revokeObjectURL(url);
    }, 'image/jpeg', 0.95);
  };

  const handleReconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    setUseMjpeg(false);
    reconnectAttempts.current = 0;
    connectWebSocket();
  };

  return (
    <div className={`relative bg-black rounded-lg overflow-hidden ${className}`}>
      {/* Canvas para el video o MJPEG fallback */}
      <div className="relative aspect-video">
        {useMjpeg ? (
          <>
            <MjpegStream cameraId={cameraId} className="w-full h-full" />
            <div className="absolute top-2 right-2 bg-yellow-600/80 text-xs px-2 py-1 rounded flex items-center gap-1">
              <WifiOff className="w-3 h-3" />
              MJPEG Mode
            </div>
          </>
        ) : (
          <canvas
            ref={canvasRef}
            className="w-full h-full object-contain"
          />
        )}

        {/* Overlay de estado */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="text-center">
              <Loader className="w-12 h-12 animate-spin mx-auto mb-2" />
              <p className="text-sm">Conectando con {cameraName}...</p>
            </div>
          </div>
        )}

        {error && !isConnected && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-2" />
              <p className="text-sm text-red-400">{error}</p>
              <button
                onClick={handleReconnect}
                className="mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm flex items-center gap-2 mx-auto"
              >
                <RefreshCw className="w-4 h-4" />
                Reintentar
              </button>
            </div>
          </div>
        )}

        {/* Controles */}
        {showControls && isConnected && (
          <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/70 to-transparent p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {/* FPS */}
                <div className="text-xs bg-black/50 px-2 py-1 rounded">
                  FPS: {fps}
                </div>
                
                {/* Zoom */}
                {zoom > 1 && (
                  <div className="text-xs bg-blue-600/50 px-2 py-1 rounded">
                    Zoom: {zoom}x
                  </div>
                )}
                
                {/* Estado de detecciones */}
                {enableDetections && detections.length > 0 && (
                  <div className={`text-xs px-2 py-1 rounded flex items-center gap-2 ${
                    detections.some(d => d.class_name === 'gate_open')
                      ? 'bg-red-600/50'
                      : 'bg-green-600/50'
                  }`}>
                    <span>{detections.filter(d => d.class_name === 'gate_open').length} abiertas</span>
                    <span>/</span>
                    <span>{detections.filter(d => d.class_name === 'gate_closed').length} cerradas</span>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2">
                {/* Zoom controls */}
                <button
                  onClick={handleZoomOut}
                  className="p-2 hover:bg-white/20 rounded transition-colors"
                  disabled={zoom <= 1}
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                
                <button
                  onClick={handleZoomIn}
                  className="p-2 hover:bg-white/20 rounded transition-colors"
                  disabled={zoom >= 3}
                >
                  <ZoomIn className="w-4 h-4" />
                </button>

                {/* Snapshot */}
                <button
                  onClick={handleSnapshot}
                  className="p-2 hover:bg-white/20 rounded transition-colors"
                  title="Capturar imagen"
                >
                  <Camera className="w-4 h-4" />
                </button>

                {/* Fullscreen */}
                <button
                  onClick={handleFullscreen}
                  className="p-2 hover:bg-white/20 rounded transition-colors"
                  title={isFullscreen ? "Salir de pantalla completa" : "Pantalla completa"}
                >
                  {isFullscreen ? (
                    <Minimize2 className="w-4 h-4" />
                  ) : (
                    <Maximize2 className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Header con estado */}
      <div className="absolute top-0 inset-x-0 bg-gradient-to-b from-black/70 to-transparent p-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium">{cameraName}</h3>
          <div className="flex items-center gap-2">
            {/* Indicador de detecciones activas */}
            {enableDetections && detections.length > 0 && (
              <div className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full animate-pulse ${
                  detections.some(d => d.class_name === 'gate_open')
                    ? 'bg-red-500'
                    : 'bg-green-500'
                }`} />
                <span className="text-xs">YOLO</span>
              </div>
            )}
            
            {/* Estado de conexión */}
            {isConnected ? (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-xs text-green-400">EN VIVO</span>
              </div>
            ) : (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-red-500 rounded-full" />
                <span className="text-xs text-red-400">DESCONECTADO</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}