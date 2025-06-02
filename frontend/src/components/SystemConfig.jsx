import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, Save, RefreshCw, Info, 
  AlertTriangle, CheckCircle, Settings,
  Zap, Clock, Bell, Volume2, Send, MessageSquare,
  Speaker, Music, VolumeX
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = 'http://localhost:8889';

export default function SystemConfig() {
  const [config, setConfig] = useState({
    confidence_threshold: 0.75,
    detection_interval: 0.5,
    alarm_sound_enabled: true,
    alarm_duration: 10,
    timer_delays: {
      door_1: 30,
      door_2: 30,
      entrance: 15,
      loading: 300,
      emergency: 5
    },
    telegram: {
      enabled: false,
      bot_token: '',
      chat_id: '',
      send_alerts: true,
      send_images: true
    }
  });
  
  const [audioConfig, setAudioConfig] = useState({
    enabled: false,
    zone_configs: {
      default: {
        friendly_duration: 30,
        moderate_duration: 120,
        enable_voice: true,
        enable_night_mode: true
      }
    },
    volume_schedule: {
      day: { start: 8, end: 20, volume: 0.8 },
      night: { start: 20, end: 8, volume: 0.5 }
    }
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadConfig();
    loadAudioConfig();
  }, []);

  const loadConfig = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/config`);
      if (response.data.config) {
        setConfig(prev => ({
          ...prev,
          ...response.data.config,
          // Asegurar que telegram existe con valores por defecto
          telegram: {
            enabled: false,
            bot_token: '',
            chat_id: '',
            send_alerts: true,
            send_images: true,
            ...response.data.config.telegram
          }
        }));
      }
    } catch (error) {
      toast.error('Error cargando configuración');
    } finally {
      setIsLoading(false);
    }
  };

  const loadAudioConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/audio/config`);
      if (response.data.config) {
        setAudioConfig(response.data.config);
      }
    } catch (error) {
      console.error('Error cargando configuración de audio:', error);
    }
  };

  const saveConfig = async () => {
    setIsSaving(true);
    try {
      // Guardar configuración general
      await axios.put(`${API_URL}/api/config`, config);
      
      // Guardar configuración de audio
      await axios.put(`${API_URL}/api/audio/config`, audioConfig);
      
      toast.success('Configuración guardada');
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

      {/* Configuración de Detección */}
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
        </div>
      </div>

      {/* Configuración de Audio Multi-fase */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <Speaker className="w-5 h-5 text-purple-400" />
          Sistema de Audio Multi-fase
        </h3>

        <div className="space-y-4">
          {/* Habilitar Audio */}
          <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
            <div className="flex items-center gap-3">
              <Volume2 className="w-5 h-5 text-gray-400" />
              <div>
                <p className="font-medium">Alarmas Sonoras Progresivas</p>
                <p className="text-sm text-gray-400">Sistema de audio que escala según el tiempo</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={audioConfig.enabled}
                onChange={(e) => setAudioConfig(prev => ({
                  ...prev,
                  enabled: e.target.checked
                }))}
                className="sr-only peer" 
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          {audioConfig.enabled && (
            <>
              {/* Fases de Audio */}
              <div className="space-y-3">
                <div className="p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Music className="w-5 h-5 text-green-400" />
                      <span className="font-medium text-green-400">Fase 1: Recordatorio Amigable</span>
                    </div>
                    <button
                      onClick={() => axios.post(`${API_URL}/api/audio/test/friendly`)}
                      className="text-xs bg-green-600 hover:bg-green-700 px-3 py-1 rounded transition-colors"
                    >
                      Probar
                    </button>
                  </div>
                  <p className="text-sm text-gray-300 mb-2">Ding-dong suave cada 10 segundos</p>
                  <div className="flex items-center gap-4">
                    <label className="text-sm">Duración:</label>
                    <input
                      type="number"
                      value={audioConfig.zone_configs.default.friendly_duration}
                      onChange={(e) => setAudioConfig(prev => ({
                        ...prev,
                        zone_configs: {
                          ...prev.zone_configs,
                          default: {
                            ...prev.zone_configs.default,
                            friendly_duration: parseInt(e.target.value) || 30
                          }
                        }
                      }))}
                      className="w-20 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
                    />
                    <span className="text-sm text-gray-400">segundos</span>
                  </div>
                </div>

                <div className="p-4 bg-yellow-900/20 border border-yellow-500/30 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Bell className="w-5 h-5 text-yellow-400" />
                      <span className="font-medium text-yellow-400">Fase 2: Alerta Moderada</span>
                    </div>
                    <button
                      onClick={() => axios.post(`${API_URL}/api/audio/test/moderate`)}
                      className="text-xs bg-yellow-600 hover:bg-yellow-700 px-3 py-1 rounded transition-colors"
                    >
                      Probar
                    </button>
                  </div>
                  <p className="text-sm text-gray-300 mb-2">Beep intermitente cada 5 segundos</p>
                  <div className="flex items-center gap-4">
                    <label className="text-sm">Duración:</label>
                    <input
                      type="number"
                      value={audioConfig.zone_configs.default.moderate_duration}
                      onChange={(e) => setAudioConfig(prev => ({
                        ...prev,
                        zone_configs: {
                          ...prev.zone_configs,
                          default: {
                            ...prev.zone_configs.default,
                            moderate_duration: parseInt(e.target.value) || 120
                          }
                        }
                      }))}
                      className="w-20 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
                    />
                    <span className="text-sm text-gray-400">segundos</span>
                  </div>
                </div>

                <div className="p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-red-400" />
                      <span className="font-medium text-red-400">Fase 3: Alarma Crítica</span>
                    </div>
                    <button
                      onClick={() => axios.post(`${API_URL}/api/audio/test/critical`)}
                      className="text-xs bg-red-600 hover:bg-red-700 px-3 py-1 rounded transition-colors"
                    >
                      Probar
                    </button>
                  </div>
                  <p className="text-sm text-gray-300">Sirena continua hasta que se cierre la puerta</p>
                </div>
              </div>

              {/* Configuración de Volumen por Horario */}
              <div className="p-4 bg-gray-700/30 rounded-lg">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <VolumeX className="w-4 h-4 text-gray-400" />
                  Volumen por Horario
                </h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Día ({audioConfig.volume_schedule.day.start}:00 - {audioConfig.volume_schedule.day.end}:00)</span>
                    <span className="text-sm font-bold text-blue-400">{Math.round(audioConfig.volume_schedule.day.volume * 100)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Noche ({audioConfig.volume_schedule.night.start}:00 - {audioConfig.volume_schedule.night.end}:00)</span>
                    <span className="text-sm font-bold text-purple-400">{Math.round(audioConfig.volume_schedule.night.volume * 100)}%</span>
                  </div>
                  <div className="flex items-center gap-2 mt-3 p-2 bg-gray-800/50 rounded">
                    <Info className="w-4 h-4 text-gray-400" />
                    <p className="text-xs text-gray-400">
                      El volumen se ajusta automáticamente según el horario para evitar molestias
                    </p>
                  </div>
                </div>
              </div>

              {/* Opciones adicionales */}
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                  <label className="text-sm font-medium">Anuncios de voz (TTS)</label>
                  <input 
                    type="checkbox" 
                    checked={audioConfig.zone_configs.default.enable_voice}
                    onChange={(e) => setAudioConfig(prev => ({
                      ...prev,
                      zone_configs: {
                        ...prev.zone_configs,
                        default: {
                          ...prev.zone_configs.default,
                          enable_voice: e.target.checked
                        }
                      }
                    }))}
                    className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
                  />
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                  <label className="text-sm font-medium">Modo nocturno automático</label>
                  <input 
                    type="checkbox" 
                    checked={audioConfig.zone_configs.default.enable_night_mode}
                    onChange={(e) => setAudioConfig(prev => ({
                      ...prev,
                      zone_configs: {
                        ...prev.zone_configs,
                        default: {
                          ...prev.zone_configs.default,
                          enable_night_mode: e.target.checked
                        }
                      }
                    }))}
                    className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
                  />
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Configuración de Telegram */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <Send className="w-5 h-5 text-blue-400" />
          Configuración de Telegram
        </h3>

        <div className="space-y-4">
          {/* Habilitar Telegram */}
          <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
            <div className="flex items-center gap-3">
              <MessageSquare className="w-5 h-5 text-gray-400" />
              <div>
                <p className="font-medium">Notificaciones por Telegram</p>
                <p className="text-sm text-gray-400">Enviar alertas a un grupo o chat de Telegram</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={config.telegram.enabled}
                onChange={(e) => setConfig(prev => ({
                  ...prev,
                  telegram: {
                    ...prev.telegram,
                    enabled: e.target.checked
                  }
                }))}
                className="sr-only peer" 
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {config.telegram.enabled && (
            <>
              {/* Bot Token */}
              <div className="p-4 bg-gray-700/30 rounded-lg">
                <label className="text-sm font-medium mb-2 block">Bot Token de Telegram</label>
                <input
                  type="text"
                  value={config.telegram.bot_token}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    telegram: {
                      ...prev.telegram,
                      bot_token: e.target.value
                    }
                  }))}
                  placeholder="Ej: 7907731965:AAE99G_I23PSPY4Iu2mB2c8J1l-fhTrYTK4"
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-sm focus:border-blue-500 focus:outline-none"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Obten el token desde @BotFather en Telegram
                </p>
              </div>

              {/* Chat ID */}
              <div className="p-4 bg-gray-700/30 rounded-lg">
                <label className="text-sm font-medium mb-2 block">Chat ID</label>
                <input
                  type="text"
                  value={config.telegram.chat_id}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    telegram: {
                      ...prev.telegram,
                      chat_id: e.target.value
                    }
                  }))}
                  placeholder="Ej: -4523731379"
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-sm focus:border-blue-500 focus:outline-none"
                />
                <p className="text-xs text-gray-500 mt-2">
                  ID del grupo o chat donde enviar las alertas (con el - si es grupo)
                </p>
              </div>

              {/* Opciones de envío */}
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                  <label className="text-sm font-medium">Enviar alertas de texto</label>
                  <input 
                    type="checkbox" 
                    checked={config.telegram.send_alerts}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      telegram: {
                        ...prev.telegram,
                        send_alerts: e.target.checked
                      }
                    }))}
                    className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                  />
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                  <label className="text-sm font-medium">Enviar imágenes con detecciones</label>
                  <input 
                    type="checkbox" 
                    checked={config.telegram.send_images}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      telegram: {
                        ...prev.telegram,
                        send_images: e.target.checked
                      }
                    }))}
                    className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Botón de prueba */}
              <button
                onClick={async () => {
                  try {
                    const response = await axios.post(`${API_URL}/api/telegram/test`, {
                      bot_token: config.telegram.bot_token,
                      chat_id: config.telegram.chat_id
                    });
                    toast.success('Mensaje de prueba enviado');
                  } catch (error) {
                    toast.error('Error al enviar mensaje de prueba');
                  }
                }}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
              >
                <Send className="w-4 h-4" />
                Enviar Mensaje de Prueba
              </button>
            </>
          )}
        </div>
      </div>

      {/* Información sobre el botón Reconocer */}
      <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Info className="w-5 h-5 text-blue-400" />
          ¿Cómo funciona el botón "Reconocer"?
        </h3>
        
        <div className="space-y-3 text-sm">
          <p className="text-gray-300">
            Cuando se detecta una puerta abierta y la alarma se activa, el botón 
            <span className="text-blue-400 font-medium"> "Reconocer" </span>
            permite al operador indicar que está consciente de la situación.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-400 mb-2" />
              <p className="font-medium text-green-400">Al presionar "Reconocer":</p>
              <ul className="mt-2 space-y-1 text-gray-300">
                <li>• Se silencia la alarma sonora</li>
                <li>• Se registra que viste la alerta</li>
                <li>• El timer continúa contando</li>
                <li>• Se marca como "atendido"</li>
              </ul>
            </div>
            
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-yellow-400 mb-2" />
              <p className="font-medium text-yellow-400">NO hace:</p>
              <ul className="mt-2 space-y-1 text-gray-300">
                <li>• NO detiene el timer</li>
                <li>• NO cierra la alerta</li>
                <li>• NO marca como "falsa alarma"</li>
                <li>• NO desactiva la detección</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}