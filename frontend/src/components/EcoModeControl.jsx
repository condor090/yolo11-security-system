import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Leaf, Activity, AlertTriangle, Zap,
  Settings, Info, ChevronDown, Save
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = 'http://localhost:8889';

const EcoModeControl = () => {
  const [ecoStatus, setEcoStatus] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [settings, setSettings] = useState({
    idle_timeout: 30,
    alert_timeout: 10,
    motion_threshold: 0.02
  });

  // Colores por estado
  const stateColors = {
    idle: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/50' },
    alert: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/50' },
    active: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/50' }
  };

  // Iconos por estado
  const stateIcons = {
    idle: <Leaf className="w-5 h-5" />,
    alert: <AlertTriangle className="w-5 h-5" />,
    active: <Zap className="w-5 h-5" />
  };

  // Cargar estado inicial
  useEffect(() => {
    loadEcoStatus();
    const interval = setInterval(loadEcoStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const loadEcoStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/eco-mode`);
      if (response.data.eco_mode.enabled) {
        setEcoStatus(response.data.eco_mode);
        setSettings({
          idle_timeout: response.data.eco_mode.settings.idle_timeout,
          alert_timeout: response.data.eco_mode.settings.alert_timeout,
          motion_threshold: response.data.eco_mode.settings.motion_threshold
        });
      }
    } catch (error) {
      console.error('Error cargando estado Eco:', error);
    }
  };

  const updateSettings = async () => {
    try {
      await axios.put(`${API_URL}/api/eco-mode`, settings);
      toast.success('Configuración actualizada', {
        icon: '🍃',
        style: {
          borderRadius: '10px',
          background: '#1f2937',
          color: '#fff',
        }
      });
      loadEcoStatus();
    } catch (error) {
      toast.error('Error actualizando configuración');
    }
  };

  const forceState = async (state) => {
    try {
      await axios.put(`${API_URL}/api/eco-mode`, { force_state: state });
      toast.success(`Estado cambiado a ${state.toUpperCase()}`, {
        style: {
          borderRadius: '10px',
          background: '#1f2937',
          color: '#fff',
        }
      });
      loadEcoStatus();
    } catch (error) {
      toast.error('Error cambiando estado');
    }
  };

  if (!ecoStatus) return null;

  const currentState = ecoStatus.current_state || 'idle';
  const colors = stateColors[currentState];
  const cpu = ecoStatus.status?.estimated_cpu || '0%';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gray-800/50 backdrop-blur rounded-xl border ${colors.border} overflow-hidden`}
    >
      {/* Header - Siempre visible */}
      <div 
        className={`p-4 ${colors.bg} cursor-pointer transition-all`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={colors.text}>
              {stateIcons[currentState]}
            </div>
            <div>
              <h3 className="font-semibold flex items-center gap-2">
                Modo Eco Inteligente
                <span className={`text-xs px-2 py-1 rounded-full ${colors.bg} ${colors.text}`}>
                  {currentState.toUpperCase()}
                </span>
              </h3>
              <p className="text-sm text-gray-400">
                CPU: {cpu} • FPS: {ecoStatus.status?.config?.fps || 0} • 
                {currentState === 'idle' && ' Ahorrando energía'}
                {currentState === 'alert' && ' Movimiento detectado'}
                {currentState === 'active' && ' Procesando detecciones'}
              </p>
            </div>
          </div>
          
          <ChevronDown 
            className={`w-5 h-5 text-gray-400 transition-transform ${
              isExpanded ? 'rotate-180' : ''
            }`}
          />
        </div>
      </div>

      {/* Contenido expandible */}
      {isExpanded && (
        <motion.div
          initial={{ height: 0 }}
          animate={{ height: 'auto' }}
          className="border-t border-gray-700/50"
        >
          {/* Estados */}
          <div className="p-4 space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-3">Estados del Sistema</h4>
              <div className="grid grid-cols-3 gap-2">
                {['idle', 'alert', 'active'].map((state) => (
                  <button
                    key={state}
                    onClick={() => forceState(state)}
                    className={`p-3 rounded-lg border transition-all ${
                      currentState === state
                        ? `${stateColors[state].bg} ${stateColors[state].border}`
                        : 'bg-gray-700/30 border-gray-600 hover:bg-gray-700/50'
                    }`}
                  >
                    <div className={`flex flex-col items-center gap-2 ${
                      currentState === state ? stateColors[state].text : 'text-gray-400'
                    }`}>
                      {stateIcons[state]}
                      <span className="text-xs font-medium">
                        {state.charAt(0).toUpperCase() + state.slice(1)}
                      </span>
                      <span className="text-xs">
                        {state === 'idle' && '~5% CPU'}
                        {state === 'alert' && '~20% CPU'}
                        {state === 'active' && '~50% CPU'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Métricas actuales */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-700/30 rounded-lg p-3">
                <p className="text-xs text-gray-400">Tiempo sin movimiento</p>
                <p className="text-lg font-semibold">
                  {Math.round(ecoStatus.status?.time_since_motion || 0)}s
                </p>
              </div>
              <div className="bg-gray-700/30 rounded-lg p-3">
                <p className="text-xs text-gray-400">Tiempo sin detección</p>
                <p className="text-lg font-semibold">
                  {Math.round(ecoStatus.status?.time_since_detection || 0)}s
                </p>
              </div>
            </div>

            {/* Configuración */}
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-400">Configuración</h4>
              
              <div>
                <label className="flex justify-between items-center mb-1">
                  <span className="text-sm">Timeout a IDLE</span>
                  <span className="text-sm text-blue-400">{settings.idle_timeout}s</span>
                </label>
                <input
                  type="range"
                  min="10"
                  max="120"
                  value={settings.idle_timeout}
                  onChange={(e) => setSettings({...settings, idle_timeout: parseInt(e.target.value)})}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="flex justify-between items-center mb-1">
                  <span className="text-sm">Timeout a ALERT</span>
                  <span className="text-sm text-blue-400">{settings.alert_timeout}s</span>
                </label>
                <input
                  type="range"
                  min="5"
                  max="30"
                  value={settings.alert_timeout}
                  onChange={(e) => setSettings({...settings, alert_timeout: parseInt(e.target.value)})}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="flex justify-between items-center mb-1">
                  <span className="text-sm">Sensibilidad de movimiento</span>
                  <span className="text-sm text-blue-400">{(settings.motion_threshold * 100).toFixed(0)}%</span>
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={settings.motion_threshold * 100}
                  onChange={(e) => setSettings({...settings, motion_threshold: e.target.value / 100})}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <button
                onClick={updateSettings}
                className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <Save className="w-4 h-4" />
                Guardar Configuración
              </button>
            </div>

            {/* Info */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
              <div className="flex gap-2">
                <Info className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="text-xs text-blue-400">
                  <p>El Modo Eco reduce el consumo de CPU hasta un 90% en períodos de inactividad.</p>
                  <p className="mt-1">• IDLE: Solo detecta movimiento</p>
                  <p>• ALERT: Detecta con baja frecuencia</p>
                  <p>• ACTIVE: Máxima precisión</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default EcoModeControl;