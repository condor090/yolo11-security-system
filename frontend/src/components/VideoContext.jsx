import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, Pause, SkipBack, SkipForward, Maximize, 
  Volume2, Download, Camera, AlertCircle, X
} from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:8889';

export default function VideoContext({ timer, onClose }) {
  const [isPlaying, setIsPlaying] = useState(true);
  const [currentFrame, setCurrentFrame] = useState(null);
  const [contextFrames, setContextFrames] = useState([]);
  const [frameIndex, setFrameIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [volume, setVolume] = useState(80);
  const intervalRef = useRef(null);
  const containerRef = useRef(null);

  // Cargar frames del contexto
  useEffect(() => {
    if (timer.has_camera && timer.camera_id) {
      loadContextVideo();
      loadLiveFrame();
    }
  }, [timer]);

  const loadLiveFrame = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/cameras/${timer.camera_id}/stream`);
      setCurrentFrame(response.data.image);
    } catch (error) {
      console.error('Error cargando frame:', error);
    }
  };

  const loadContextVideo = async () => {
    setIsLoading(true);
    try {
      const eventTime = new Date(timer.first_detected).toISOString();
      const response = await axios.get(
        `${API_URL}/api/cameras/${timer.camera_id}/context`,
        {
          params: {
            event_time: eventTime,
            before_seconds: 30,
            after_seconds: 30
          }
        }
      );
      
      setContextFrames(response.data.frames);
      
      // Encontrar frame más cercano al evento
      const eventIndex = response.data.frames.findIndex(
        f => new Date(f.timestamp) >= new Date(eventTime)
      );
      setFrameIndex(eventIndex > 0 ? eventIndex : 0);
      
    } catch (error) {
      console.error('Error cargando contexto:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Reproducción automática
  useEffect(() => {
    if (isPlaying && contextFrames.length > 0) {
      intervalRef.current = setInterval(() => {
        setFrameIndex(prev => {
          if (prev >= contextFrames.length - 1) {
            return 0; // Loop
          }
          return prev + 1;
        });
      }, 100); // ~10 fps
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, contextFrames]);

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      containerRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
    setIsFullscreen(!isFullscreen);
  };

  const skipFrames = (direction) => {
    const skip = direction === 'forward' ? 10 : -10;
    setFrameIndex(prev => {
      const newIndex = prev + skip;
      if (newIndex < 0) return 0;
      if (newIndex >= contextFrames.length) return contextFrames.length - 1;
      return newIndex;
    });
  };

  const downloadClip = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/cameras/${timer.camera_id}/record`);
      
      // Esperar 5 segundos y luego detener
      setTimeout(async () => {
        await axios.post(`${API_URL}/api/cameras/${timer.camera_id}/stop-recording`);
        toast.success('Clip guardado: ' + response.data.recording_path);
      }, 5000);
      
    } catch (error) {
      console.error('Error grabando:', error);
    }
  };

  const currentImage = contextFrames[frameIndex]?.image || currentFrame;
  const currentTime = contextFrames[frameIndex]?.timestamp || new Date().toISOString();
  const progress = contextFrames.length > 0 ? (frameIndex / contextFrames.length) * 100 : 0;

  return (
    <motion.div
      ref={containerRef}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={`bg-gray-900 rounded-lg overflow-hidden ${
        isFullscreen ? 'fixed inset-0 z-50' : 'relative'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <Camera className="w-5 h-5 text-blue-400" />
          <div>
            <h4 className="font-semibold">{timer.camera_name || 'Cámara'}</h4>
            <p className="text-xs text-gray-400">
              Contexto: {timer.door_id} • {new Date(currentTime).toLocaleTimeString()}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-700 rounded transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Video Area */}
      <div className="relative bg-black aspect-video">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
          </div>
        ) : currentImage ? (
          <>
            <img 
              src={currentImage} 
              alt="Video Context" 
              className="w-full h-full object-contain"
            />
            
            {/* Overlay de información */}
            <div className="absolute top-0 left-0 right-0 p-3 bg-gradient-to-b from-black/70 to-transparent">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-mono">
                    {new Date(currentTime).toLocaleTimeString('es-ES', { 
                      hour12: false, 
                      hour: '2-digit', 
                      minute: '2-digit', 
                      second: '2-digit' 
                    })}
                  </p>
                  {timer.alarm_triggered && (
                    <div className="flex items-center gap-1 mt-1">
                      <AlertCircle className="w-4 h-4 text-red-500" />
                      <span className="text-xs text-red-500">ALARMA ACTIVA</span>
                    </div>
                  )}
                </div>
                <div className="text-xs text-gray-300 text-right">
                  <p>FPS: {timer.camera_fps || '--'}</p>
                  <p>Frame: {frameIndex + 1}/{contextFrames.length}</p>
                </div>
              </div>
            </div>

            {/* Timeline del evento */}
            <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/70 to-transparent">
              <div className="relative h-1 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="absolute h-full bg-blue-500 transition-all"
                  style={{ width: `${progress}%` }}
                />
                {/* Marcador del evento */}
                <div 
                  className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-red-500 rounded-full"
                  style={{ left: '50%' }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>-30s</span>
                <span className="text-red-400">Evento</span>
                <span>+30s</span>
              </div>
            </div>
          </>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            <Camera className="w-16 h-16 opacity-20" />
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="p-3 bg-gray-800 border-t border-gray-700">
        <div className="flex items-center justify-between gap-3">
          {/* Play controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => skipFrames('back')}
              className="p-2 hover:bg-gray-700 rounded transition-colors"
              title="Retroceder 10 frames"
            >
              <SkipBack className="w-4 h-4" />
            </button>
            
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            
            <button
              onClick={() => skipFrames('forward')}
              className="p-2 hover:bg-gray-700 rounded transition-colors"
              title="Avanzar 10 frames"
            >
              <SkipForward className="w-4 h-4" />
            </button>
          </div>

          {/* Volume */}
          <div className="flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-gray-400" />
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={(e) => setVolume(e.target.value)}
              className="w-20 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={downloadClip}
              className="p-2 hover:bg-gray-700 rounded transition-colors"
              title="Guardar clip"
            >
              <Download className="w-4 h-4" />
            </button>
            
            <button
              onClick={toggleFullscreen}
              className="p-2 hover:bg-gray-700 rounded transition-colors"
              title="Pantalla completa"
            >
              <Maximize className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* AI Suggestion */}
        {timer.alarm_triggered && (
          <div className="mt-3 p-3 bg-blue-900/30 border border-blue-500/30 rounded-lg">
            <p className="text-sm text-blue-400">
              💡 <strong>Sugerencia IA:</strong> Verificar si es personal autorizado. 
              Patrón detectado: Acceso fuera de horario habitual.
            </p>
          </div>
        )}
      </div>
    </motion.div>
  );
}