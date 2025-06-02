import React, { useState, useEffect } from 'react';
import { 
  Shield, Save, RefreshCw, Info, 
  AlertTriangle, CheckCircle, Settings,
  Zap, Clock, Bell, Volume2
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = 'http://localhost:8889';

export default function SystemSettings() {
  const [config, setConfig] = useState({
    confidence_threshold: 0.75,
    detection_interval: 0.5,
    alarm_sound_enabled: true,
    alarm_duration: 10,
    clean_all_on_close: true,
    cooldown_minutes: 5
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/config`);
      if (response.data.config) {
        setConfig(prev => ({
          ...prev,
          confidence_threshold: response.data.config.confidence_threshold || 0.75,
          detection_interval: response.data.config.detection_interval || 0.5,
          alarm_sound_enabled: response.data.config.alarm_sound_enabled !== false,
          alarm_duration: response.data.config.alarm_duration || 10,
          clean_all_on_close: response.data.config.clean_all_on_close !== false,
          cooldown_minutes: response.data.config.cooldown_minutes || 5
        }));
      }
    } catch (error) {
      toast.error('Error cargando configuración del sistema');
    } finally {
      setIsLoading(false);
    }
  };

  const saveConfig = async () => {
    setIsSaving(true);
    try {
      await axios.put(`${API_URL}/api/config`, config);
      toast.success('Configuración del sistema guardada');
    } catch (error) {
      toast.error('Error guardando configuración');
    } finally {
      setIsSaving(false);
    }
  };

  const handleConfidenceChange = (value) => {
    setConfig(prev => ({
      ...prev,
      confidence_threshold: parseFloat(value)
    }));
  };

  const handleDetectionIntervalChange = (value) => {
    setConfig(prev => ({
      ...prev,
      detection_interval: parseFloat(value)
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Settings className="w-6 h-6 text-blue-400" />
          Configuración del Sistema
        </h2>
        <div className="flex gap-3">
          <button
            onClick={loadConfig}
            disabled={isLoading}
            className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Recargar
          </button>
          <button
            onClick={saveConfig}
            disabled={isSaving}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
          >
            <Save className="w-4 h-4" />
            {isSaving ? 'Guardando...' : 'Guardar Cambios'}
          </button>
        </div>
      </div>

      {/* Configuración de Detección YOLO */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <Shield className="w-5 h-5 text-blue-400" />
          Configuración de Detección YOLO
        </h3>

        <div className="space-y-6">
          {/* Umbral de Confianza */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-medium flex items-center gap-2">
                Umbral de Confianza
                <Info className="w-4 h-4 text-gray-400" title="Mínima confianza para considerar una detección válida" />
              </label>
              <span className="text-lg font-bold text-blue-400">
                {Math.round(config.confidence_threshold * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="50"
              max="95"
              step="5"
              value={config.confidence_threshold * 100}
              onChange={(e) => handleConfidenceChange(e.target.value / 100)}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>50% (Más detecciones)</span>
              <span>95% (Menos falsas alarmas)</span>
            </div>
            
            {config.confidence_threshold < 0.7 && (
              <div className="mt-3 p-3 bg-yellow-900/30 border border-yellow-500/30 rounded-lg flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5" />
                <div className="text-sm">
                  <p className="text-yellow-400 font-medium">Advertencia: Umbral bajo</p>
                  <p className="text-gray-300 mt-1">
                    Un umbral menor a 70% puede generar falsas alarmas. 
                    Recomendamos 75% o más para operación normal.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Intervalo de Detección */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-medium flex items-center gap-2">
                Intervalo de Detección
                <Info className="w-4 h-4 text-gray-400" title="Tiempo entre análisis YOLO" />
              </label>
              <span className="text-lg font-bold text-purple-400">
                {config.detection_interval}s
              </span>
            </div>
            <input
              type="range"
              min="0.1"
              max="2.0"
              step="0.1"
              value={config.detection_interval}
              onChange={(e) => handleDetectionIntervalChange(e.target.value)}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0.1s (Más CPU)</span>
              <span>2.0s (Menos CPU)</span>
            </div>
          </div>

          {/* Estadísticas de rendimiento */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-900/50 rounded-lg">
            <div className="text-center">
              <Zap className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
              <p className="text-sm text-gray-400">Detecciones/min</p>
              <p className="text-2xl font-bold">
                {Math.round(60 / config.detection_interval)}
              </p>
            </div>
            <div className="text-center">
              <Clock className="w-8 h-8 text-blue-400 mx-auto mb-2" />
              <p className="text-sm text-gray-400">Latencia máx.</p>
              <p className="text-2xl font-bold">
                {(config.detection_interval * 1000).toFixed(0)}ms
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Configuración de Alarmas */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <Bell className="w-5 h-5 text-red-400" />
          Configuración de Alarmas
        </h3>

        <div className="space-y-4">
          {/* Sonido de Alarma */}
          <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
            <div className="flex items-center gap-3">
              <Volume2 className="w-5 h-5 text-gray-400" />
              <div>
                <p className="font-medium">Alarma Sonora</p>
                <p className="text-sm text-gray-400">Activar sonido cuando se dispare una alarma</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={config.alarm_sound_enabled}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  alarm_sound_enabled: e.target.checked
                }))}
                className="sr-only peer" 
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
            </label>
          </div>

          {/* Duración de Alarma */}
          <div className="p-4 bg-gray-700/30 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-medium">Duración de Alarma</label>
              <span className="text-lg font-bold text-red-400">
                {config.alarm_duration}s
              </span>
            </div>
            <input
              type="range"
              min="5"
              max="30"
              step="5"
              value={config.alarm_duration}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                alarm_duration: parseInt(e.target.value)
              }))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Limpiar al cerrar */}
          <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-gray-400" />
              <div>
                <p className="font-medium">Limpiar alarmas al cerrar puertas</p>
                <p className="text-sm text-gray-400">Detener todas las alarmas cuando se detecte una puerta cerrada</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={config.clean_all_on_close}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  clean_all_on_close: e.target.checked
                }))}
                className="sr-only peer" 
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>

          {/* Tiempo de enfriamiento */}
          <div className="p-4 bg-gray-700/30 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-medium">Tiempo de enfriamiento</label>
              <span className="text-lg font-bold text-blue-400">
                {config.cooldown_minutes} min
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              value={config.cooldown_minutes}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                cooldown_minutes: parseInt(e.target.value)
              }))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <p className="text-xs text-gray-500 mt-2">
              Tiempo mínimo antes de volver a alertar sobre la misma puerta
            </p>
          </div>
        </div>
      </div>

      {/* Información sobre el sistema */}
      <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Info className="w-5 h-5 text-blue-400" />
          Información del Sistema
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="p-3 bg-gray-800/50 rounded-lg">
            <p className="text-gray-400 mb-1">Versión</p>
            <p className="font-semibold">v3.6.0</p>
          </div>
          <div className="p-3 bg-gray-800/50 rounded-lg">
            <p className="text-gray-400 mb-1">Modelo</p>
            <p className="font-semibold">YOLO11</p>
          </div>
          <div className="p-3 bg-gray-800/50 rounded-lg">
            <p className="text-gray-400 mb-1">Precisión</p>
            <p className="font-semibold">99.39% mAP50</p>
          </div>
          <div className="p-3 bg-gray-800/50 rounded-lg">
            <p className="text-gray-400 mb-1">Backend</p>
            <p className="font-semibold">FastAPI</p>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-gray-800/50 rounded-lg">
          <p className="text-sm text-gray-300">
            <strong>Desarrollado por:</strong> Virgilio IA - 100% generado por inteligencia artificial
          </p>
          <p className="text-sm text-gray-400 mt-1">
            Sistema de seguridad inteligente con detección de puertas en tiempo real
          </p>
        </div>
      </div>
    </div>
  );
}