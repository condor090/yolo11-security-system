import React, { useState, useEffect } from 'react';
import { 
  Speaker, Save, Plus, Trash2, Clock, Volume2, 
  Play, Pause, Settings, Info, Music
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = 'http://localhost:8889';

const AVAILABLE_SOUNDS = [
  { value: 'ding_dong.mp3', label: 'Ding Dong' },
  { value: 'beep_alert.mp3', label: 'Beep Alert' },
  { value: 'alarm_siren.mp3', label: 'Alarm Siren' }
];

export default function AudioZoneConfig() {
  const [config, setConfig] = useState({
    enabled: true,
    default_phases: {
      phase_1: { percentage: 50, interval_seconds: 10, sound: 'ding_dong.mp3', volume: 0.5 },
      phase_2: { percentage: 90, interval_seconds: 5, sound: 'beep_alert.mp3', volume: 0.7 },
      phase_3: { percentage: 100, interval_seconds: 0, sound: 'alarm_siren.mp3', volume: 1.0 }
    },
    zone_audio_configs: {}
  });

  const [selectedZone, setSelectedZone] = useState('default');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [zones, setZones] = useState(['default', 'entrance', 'loading', 'emergency']);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/audio/config`);
      if (response.data.config) {
        setConfig(response.data.config);
      }
    } catch (error) {
      toast.error('Error cargando configuración de audio');
    } finally {
      setIsLoading(false);
    }
  };

  const saveConfig = async () => {
    setIsSaving(true);
    try {
      await axios.put(`${API_URL}/api/audio/config`, config);
      toast.success('Configuración de audio guardada');
    } catch (error) {
      toast.error('Error guardando configuración');
    } finally {
      setIsSaving(false);
    }
  };

  const getCurrentZoneConfig = () => {
    return config.zone_audio_configs[selectedZone] || { use_custom: false };
  };

  const updateZoneConfig = (updates) => {
    setConfig(prev => ({
      ...prev,
      zone_audio_configs: {
        ...prev.zone_audio_configs,
        [selectedZone]: {
          ...getCurrentZoneConfig(),
          ...updates
        }
      }
    }));
  };

  const addPhase = () => {
    const currentConfig = getCurrentZoneConfig();
    const phases = currentConfig.phases || [];
    const newPhase = {
      name: `phase_${phases.length + 1}`,
      duration_seconds: 10,
      interval_seconds: 5,
      sound: 'ding_dong.mp3',
      volume: 0.5
    };

    updateZoneConfig({
      phases: [...phases, newPhase]
    });
  };

  const updatePhase = (index, updates) => {
    const currentConfig = getCurrentZoneConfig();
    const phases = [...(currentConfig.phases || [])];
    phases[index] = { ...phases[index], ...updates };
    updateZoneConfig({ phases });
  };

  const removePhase = (index) => {
    const currentConfig = getCurrentZoneConfig();
    const phases = currentConfig.phases.filter((_, i) => i !== index);
    updateZoneConfig({ phases });
  };

  const testSound = async (sound, phase) => {
    try {
      // Mapear sonidos a fases esperadas por el backend
      const phaseMap = {
        'ding_dong.mp3': 'friendly',
        'beep_alert.mp3': 'moderate', 
        'alarm_siren.mp3': 'critical'
      };
      
      const phaseName = phase || phaseMap[sound] || 'friendly';
      await axios.post(`${API_URL}/api/audio/test/${phaseName}`);
    } catch (error) {
      toast.error('Error reproduciendo sonido');
    }
  };

  const zoneConfig = getCurrentZoneConfig();
  const isCustomMode = zoneConfig.use_custom;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Speaker className="w-6 h-6 text-purple-400" />
          Configuración de Audio por Zona
        </h2>
        <button
          onClick={saveConfig}
          disabled={isSaving}
          className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg transition-colors"
        >
          <Save className="w-4 h-4" />
          {isSaving ? 'Guardando...' : 'Guardar Cambios'}
        </button>
      </div>

      {/* Selector de Zona */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <div className="flex items-center justify-between mb-4">
          <label className="text-lg font-semibold">Seleccionar Zona</label>
          <select
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-sm focus:border-purple-500 focus:outline-none"
          >
            {zones.map(zone => (
              <option key={zone} value={zone}>
                {zone === 'default' ? 'Configuración por Defecto' : zone}
              </option>
            ))}
          </select>
        </div>

        {/* Toggle Modo */}
        <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
          <div className="flex items-center gap-3">
            <Settings className="w-5 h-5 text-gray-400" />
            <div>
              <p className="font-medium">Modo de Configuración</p>
              <p className="text-sm text-gray-400">
                {isCustomMode ? 'Tiempos Absolutos' : 'Porcentajes del Temporizador'}
              </p>
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={isCustomMode}
              onChange={(e) => updateZoneConfig({ use_custom: e.target.checked })}
              className="sr-only peer"
              disabled={selectedZone === 'default'}
            />
            <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600 peer-disabled:opacity-50"></div>
          </label>
        </div>
      </div>

      {/* Configuración por Porcentajes */}
      {!isCustomMode && (
        <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
          <h3 className="text-lg font-semibold mb-6">Configuración por Porcentajes</h3>
          
          <div className="space-y-6">
            {/* Fase 1 */}
            <div className="p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Music className="w-5 h-5 text-green-400" />
                  <span className="font-medium text-green-400">Fase 1: Recordatorio Amigable</span>
                </div>
                <button
                  onClick={() => testSound(config.default_phases.phase_1.sound, 'friendly')}
                  className="text-xs bg-green-600 hover:bg-green-700 px-3 py-1 rounded transition-colors"
                >
                  Probar
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400">Activación</label>
                  <div className="flex items-center gap-2 mt-1">
                    <span>0% -</span>
                    <input
                      type="number"
                      value={config.default_phases.phase_1.percentage}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        default_phases: {
                          ...prev.default_phases,
                          phase_1: {
                            ...prev.default_phases.phase_1,
                            percentage: parseInt(e.target.value) || 50
                          }
                        }
                      }))}
                      className="w-16 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
                    />
                    <span>%</span>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm text-gray-400">Intervalo</label>
                  <div className="flex items-center gap-2 mt-1">
                    <input
                      type="number"
                      value={config.default_phases.phase_1.interval_seconds}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        default_phases: {
                          ...prev.default_phases,
                          phase_1: {
                            ...prev.default_phases.phase_1,
                            interval_seconds: parseInt(e.target.value) || 10
                          }
                        }
                      }))}
                      className="w-16 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
                    />
                    <span>segundos</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Fase 2 */}
            <div className="p-4 bg-yellow-900/20 border border-yellow-500/30 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Music className="w-5 h-5 text-yellow-400" />
                  <span className="font-medium text-yellow-400">Fase 2: Alerta Moderada</span>
                </div>
                <button
                  onClick={() => testSound(config.default_phases.phase_2.sound, 'moderate')}
                  className="text-xs bg-yellow-600 hover:bg-yellow-700 px-3 py-1 rounded transition-colors"
                >
                  Probar
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400">Activación</label>
                  <div className="flex items-center gap-2 mt-1">
                    <input
                      type="number"
                      value={config.default_phases.phase_1.percentage}
                      disabled
                      className="w-16 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm opacity-50"
                    />
                    <span>% -</span>
                    <input
                      type="number"
                      value={config.default_phases.phase_2.percentage}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        default_phases: {
                          ...prev.default_phases,
                          phase_2: {
                            ...prev.default_phases.phase_2,
                            percentage: parseInt(e.target.value) || 90
                          }
                        }
                      }))}
                      className="w-16 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
                    />
                    <span>%</span>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm text-gray-400">Intervalo</label>
                  <div className="flex items-center gap-2 mt-1">
                    <input
                      type="number"
                      value={config.default_phases.phase_2.interval_seconds}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        default_phases: {
                          ...prev.default_phases,
                          phase_2: {
                            ...prev.default_phases.phase_2,
                            interval_seconds: parseInt(e.target.value) || 5
                          }
                        }
                      }))}
                      className="w-16 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
                    />
                    <span>segundos</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Fase 3 */}
            <div className="p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Music className="w-5 h-5 text-red-400" />
                  <span className="font-medium text-red-400">Fase 3: Alarma Crítica</span>
                </div>
                <button
                  onClick={() => testSound(config.default_phases.phase_3.sound, 'critical')}
                  className="text-xs bg-red-600 hover:bg-red-700 px-3 py-1 rounded transition-colors"
                >
                  Probar
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400">Activación</label>
                  <div className="flex items-center gap-2 mt-1">
                    <span>></span>
                    <input
                      type="number"
                      value={config.default_phases.phase_2.percentage}
                      disabled
                      className="w-16 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm opacity-50"
                    />
                    <span>% (al expirar timer)</span>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm text-gray-400">Modo</label>
                  <select
                    value={config.default_phases.phase_3.interval_seconds}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      default_phases: {
                        ...prev.default_phases,
                        phase_3: {
                          ...prev.default_phases.phase_3,
                          interval_seconds: parseInt(e.target.value)
                        }
                      }
                    }))}
                    className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm mt-1"
                  >
                    <option value="0">Continuo</option>
                    <option value="1">Cada 1 segundo</option>
                    <option value="2">Cada 2 segundos</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Configuración Personalizada */}
      {isCustomMode && selectedZone !== 'default' && (
        <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold">Configuración Personalizada: {selectedZone}</h3>
            <button
              onClick={addPhase}
              className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 px-3 py-1.5 rounded-lg transition-colors text-sm"
            >
              <Plus className="w-4 h-4" />
              Agregar Fase
            </button>
          </div>

          <div className="space-y-4">
            {(zoneConfig.phases || []).map((phase, index) => (
              <div key={index} className="p-4 bg-gray-700/30 rounded-lg border border-gray-600/50">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-medium">Fase {index + 1}: {phase.name}</h4>
                  <button
                    onClick={() => removePhase(index)}
                    className="text-red-400 hover:text-red-300 p-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div>
                    <label className="text-xs text-gray-400">Duración</label>
                    <div className="flex items-center gap-1 mt-1">
                      <input
                        type="number"
                        value={phase.duration_seconds}
                        onChange={(e) => updatePhase(index, { 
                          duration_seconds: e.target.value === '-1' ? -1 : parseInt(e.target.value) || 10 
                        })}
                        className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
                      />
                      <span className="text-xs">s</span>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs text-gray-400">Intervalo</label>
                    <div className="flex items-center gap-1 mt-1">
                      <input
                        type="number"
                        step="0.1"
                        value={phase.interval_seconds}
                        onChange={(e) => updatePhase(index, { 
                          interval_seconds: parseFloat(e.target.value) || 1 
                        })}
                        className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm"
                      />
                      <span className="text-xs">s</span>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs text-gray-400">Sonido</label>
                    <select
                      value={phase.sound}
                      onChange={(e) => updatePhase(index, { sound: e.target.value })}
                      className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm mt-1"
                    >
                      {AVAILABLE_SOUNDS.map(sound => (
                        <option key={sound.value} value={sound.value}>
                          {sound.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-xs text-gray-400">Volumen</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={phase.volume * 100}
                      onChange={(e) => updatePhase(index, { 
                        volume: parseInt(e.target.value) / 100 
                      })}
                      className="w-full mt-2"
                    />
                  </div>
                </div>

                {phase.duration_seconds === -1 && (
                  <p className="text-xs text-yellow-400 mt-2">
                    <Info className="w-3 h-3 inline mr-1" />
                    Duración infinita - continuará hasta que se cierre la puerta
                  </p>
                )}
              </div>
            ))}

            {(!zoneConfig.phases || zoneConfig.phases.length === 0) && (
              <div className="text-center py-8 text-gray-400">
                <Speaker className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No hay fases configuradas</p>
                <p className="text-sm mt-1">Haz clic en "Agregar Fase" para comenzar</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Información */}
      <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Info className="w-5 h-5 text-blue-400" />
          Información sobre la Configuración
        </h3>
        
        <div className="space-y-3 text-sm text-gray-300">
          <p>
            • <strong>Modo Porcentajes:</strong> Las fases se activan según el porcentaje del tiempo total del temporizador de cada zona.
          </p>
          <p>
            • <strong>Modo Tiempos Absolutos:</strong> Define duraciones específicas para cada fase, ideal para zonas críticas.
          </p>
          <p>
            • <strong>Duración -1:</strong> La fase continuará indefinidamente hasta que se resuelva la alerta.
          </p>
          <p>
            • <strong>Intervalo 0:</strong> El sonido se reproducirá de forma continua sin pausas.
          </p>
        </div>
      </div>
    </div>
  );
}