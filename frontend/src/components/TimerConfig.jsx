import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Clock, Save, RefreshCw, Plus, Trash2, 
  AlertCircle, Info, Edit2
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = 'http://localhost:8889';

export default function TimerConfig() {
  const [timerDelays, setTimerDelays] = useState({});
  const [profiles, setProfiles] = useState({});
  const [editingZone, setEditingZone] = useState(null);
  const [newDelay, setNewDelay] = useState('');
  const [isAddingZone, setIsAddingZone] = useState(false);
  const [newZone, setNewZone] = useState({ id: '', name: '', delay: 30 });
  const [stats, setStats] = useState({});

  // Perfiles predefinidos
  const predefinedProfiles = {
    normal: {
      name: 'Horario Normal',
      icon: '🏢',
      delays: { default: 30, entrance: 15, loading: 300, emergency: 5 }
    },
    rush: {
      name: 'Hora Pico',
      icon: '🚦',
      delays: { default: 45, entrance: 20, loading: 360, emergency: 10 }
    },
    night: {
      name: 'Nocturno',
      icon: '🌙',
      delays: { default: 15, entrance: 10, loading: 180, emergency: 5 }
    },
    weekend: {
      name: 'Fin de Semana',
      icon: '📅',
      delays: { default: 60, entrance: 30, loading: 600, emergency: 15 }
    }
  };

  // Cargar configuración al montar
  useEffect(() => {
    loadConfig();
    loadStats();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/config`);
      setTimerDelays(response.data.config.timer_delays || {});
      setProfiles(response.data.config.profiles || predefinedProfiles);
    } catch (error) {
      console.error('Error cargando configuración:', error);
      toast.error('Error cargando configuración');
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/statistics`);
      setStats(response.data.statistics || {});
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
    }
  };

  const saveConfig = async () => {
    try {
      await axios.put(`${API_URL}/api/config`, {
        timer_delays: timerDelays,
        profiles: profiles
      });
      toast.success('Configuración guardada');
    } catch (error) {
      toast.error('Error guardando configuración');
    }
  };

  const updateDelay = (zone, delay) => {
    const newDelays = { ...timerDelays, [zone]: parseInt(delay) };
    setTimerDelays(newDelays);
  };

  const deleteZone = (zone) => {
    if (window.confirm(`¿Eliminar zona ${zone}?`)) {
      const newDelays = { ...timerDelays };
      delete newDelays[zone];
      setTimerDelays(newDelays);
    }
  };

  const addZone = () => {
    if (newZone.id && !timerDelays[newZone.id]) {
      setTimerDelays({
        ...timerDelays,
        [newZone.id]: parseInt(newZone.delay)
      });
      setNewZone({ id: '', name: '', delay: 30 });
      setIsAddingZone(false);
      toast.success('Zona agregada');
    } else {
      toast.error('ID de zona inválido o ya existe');
    }
  };

  const applyProfile = (profileKey) => {
    const profile = predefinedProfiles[profileKey];
    if (profile) {
      setTimerDelays({ ...timerDelays, ...profile.delays });
      toast.success(`Perfil "${profile.name}" aplicado`);
    }
  };

  const formatTime = (seconds) => {
    if (seconds >= 60) {
      const minutes = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${minutes}m ${secs > 0 ? secs + 's' : ''}`;
    }
    return `${seconds}s`;
  };

  return (
    <div className="space-y-6">
      {/* Header con perfiles */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" />
            Configuración de Temporizadores
          </h3>
          
          <button
            onClick={saveConfig}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
          >
            <Save className="w-4 h-4" />
            Guardar Cambios
          </button>
        </div>

        {/* Perfiles rápidos */}
        <div className="mb-6">
          <p className="text-sm text-gray-400 mb-3">Aplicar perfil predefinido:</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(predefinedProfiles).map(([key, profile]) => (
              <button
                key={key}
                onClick={() => applyProfile(key)}
                className="p-3 bg-gray-700/50 hover:bg-gray-700 rounded-lg transition-all text-center"
              >
                <div className="text-2xl mb-1">{profile.icon}</div>
                <div className="text-sm font-medium">{profile.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Lista de zonas */}
        <div className="space-y-3">
          {Object.entries(timerDelays).map(([zone, delay]) => (
            <motion.div
              key={zone}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg"
            >
              <div className="flex-1">
                <div className="font-medium">{zone}</div>
                <div className="text-sm text-gray-400">
                  {zone === 'default' ? 'Tiempo por defecto' : `Zona: ${zone}`}
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                {editingZone === zone ? (
                  <>
                    <input
                      type="number"
                      value={newDelay}
                      onChange={(e) => setNewDelay(e.target.value)}
                      className="w-20 px-2 py-1 bg-gray-800 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                      min="1"
                      max="3600"
                    />
                    <button
                      onClick={() => {
                        updateDelay(zone, newDelay);
                        setEditingZone(null);
                      }}
                      className="p-2 bg-green-600 hover:bg-green-700 rounded transition-colors"
                    >
                      <Save className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setEditingZone(null)}
                      className="p-2 bg-gray-600 hover:bg-gray-700 rounded transition-colors"
                    >
                      ✕
                    </button>
                  </>
                ) : (
                  <>
                    <div className="text-2xl font-bold text-blue-400 min-w-[80px] text-right">
                      {formatTime(delay)}
                    </div>
                    <button
                      onClick={() => {
                        setEditingZone(zone);
                        setNewDelay(delay.toString());
                      }}
                      className="p-2 hover:bg-gray-700 rounded transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    {zone !== 'default' && (
                      <button
                        onClick={() => deleteZone(zone)}
                        className="p-2 hover:bg-gray-700 rounded transition-colors text-red-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Agregar nueva zona */}
        {isAddingZone ? (
          <div className="mt-4 p-4 bg-gray-700/30 rounded-lg">
            <h4 className="font-medium mb-3">Nueva Zona</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <input
                type="text"
                placeholder="ID de zona (ej: parking)"
                value={newZone.id}
                onChange={(e) => setNewZone({ ...newZone, id: e.target.value })}
                className="px-3 py-2 bg-gray-800 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              />
              <input
                type="number"
                placeholder="Delay en segundos"
                value={newZone.delay}
                onChange={(e) => setNewZone({ ...newZone, delay: e.target.value })}
                className="px-3 py-2 bg-gray-800 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                min="1"
                max="3600"
              />
              <div className="flex gap-2">
                <button
                  onClick={addZone}
                  className="flex-1 bg-green-600 hover:bg-green-700 px-3 py-2 rounded transition-colors"
                >
                  Agregar
                </button>
                <button
                  onClick={() => setIsAddingZone(false)}
                  className="px-3 py-2 bg-gray-600 hover:bg-gray-700 rounded transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setIsAddingZone(true)}
            className="mt-4 w-full flex items-center justify-center gap-2 p-3 bg-gray-700/50 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Agregar Nueva Zona
          </button>
        )}
      </div>

      {/* Información */}
      <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-1" />
          <div className="space-y-2 text-sm">
            <p className="font-medium text-blue-400">Información sobre temporizadores:</p>
            <ul className="space-y-1 text-gray-300">
              <li>• Los temporizadores definen cuánto tiempo puede estar abierta una puerta antes de activar la alarma</li>
              <li>• Cada zona puede tener su propio tiempo configurado según las necesidades operativas</li>
              <li>• El valor "default" se aplica a zonas no configuradas específicamente</li>
              <li>• Los perfiles permiten cambiar rápidamente entre configuraciones predefinidas</li>
              <li>• Tiempos recomendados: Entrada (15-30s), Carga (5-10min), Emergencia (5-10s)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Estadísticas de uso */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <h4 className="font-semibold mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-yellow-400" />
          Estadísticas de Alarmas (Últimas 24h)
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-700/30 rounded-lg">
            <div className="text-2xl font-bold text-yellow-400">
              {stats.false_alarms || 0}
            </div>
            <div className="text-sm text-gray-400">Falsas Alarmas</div>
            <div className="text-xs text-gray-500 mt-1">
              Cerradas antes del tiempo
            </div>
          </div>
          <div className="text-center p-4 bg-gray-700/30 rounded-lg">
            <div className="text-2xl font-bold text-red-400">
              {stats.real_alarms || 0}
            </div>
            <div className="text-sm text-gray-400">Alarmas Reales</div>
            <div className="text-xs text-gray-500 mt-1">
              Superaron el tiempo límite
            </div>
          </div>
          <div className="text-center p-4 bg-gray-700/30 rounded-lg">
            <div className="text-2xl font-bold text-blue-400">
              {stats.avg_open_time || '0'}s
            </div>
            <div className="text-sm text-gray-400">Tiempo Promedio</div>
            <div className="text-xs text-gray-500 mt-1">
              Duración apertura promedio
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}