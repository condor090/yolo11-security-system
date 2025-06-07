// Configuración de Vehículos - Interfaz React
import React, { useState, useEffect } from 'react';
import { 
  Truck, Clock, AlertTriangle, Save, Plus, Edit2, Trash2, 
  Settings, ChevronDown, ChevronUp, Palette, Package,
  Snowflake, PiggyBank, Timer, Shield
} from 'lucide-react';
import toast from 'react-hot-toast';

const VehicleConfiguration = () => {
  const [vehicleTypes, setVehicleTypes] = useState([]);
  const [conflictRules, setConflictRules] = useState([]);
  const [systemSettings, setSystemSettings] = useState({});
  const [editingType, setEditingType] = useState(null);
  const [editingRule, setEditingRule] = useState(null);
  const [showNewType, setShowNewType] = useState(false);
  const [showNewRule, setShowNewRule] = useState(false);
  const [loading, setLoading] = useState(true);

  // Iconos disponibles
  const availableIcons = {
    truck: <Truck size={20} />,
    snowflake: <Snowflake size={20} />,
    'piggy-bank': <PiggyBank size={20} />,
    bacon: <Package size={20} />,
    'truck-loading': <Truck size={20} />,
    timer: <Timer size={20} />,
    shield: <Shield size={20} />
  };

  // Colores predefinidos
  const availableColors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
    '#6366F1', '#8B5CF6', '#EC4899', '#14B8A6'
  ];

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    try {
      setLoading(true);
      
      // Cargar tipos de vehículos
      const typesResponse = await fetch('/api/config/vehicles/types');
      const types = await typesResponse.json();
      setVehicleTypes(types);

      // Cargar reglas de conflicto
      const rulesResponse = await fetch('/api/config/vehicles/rules');
      const rules = await rulesResponse.json();
      setConflictRules(rules);

      // Cargar configuración general
      const settingsResponse = await fetch('/api/config/vehicles/settings');
      const settings = await settingsResponse.json();
      setSystemSettings(settings);

    } catch (error) {
      toast.error('Error cargando configuración');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Componente para editar tipo de vehículo
  const VehicleTypeForm = ({ type, onSave, onCancel }) => {
    const [formData, setFormData] = useState(type || {
      tipo: '',
      nombre_display: '',
      duracion_minutos: 60,
      prioridad: 3,
      hora_inicio: '',
      hora_fin: '',
      ventana_estricta: false,
      requisitos_especiales: [],
      color_ui: '#3B82F6',
      icono: 'truck',
      activo: true
    });

    const [newRequisito, setNewRequisito] = useState('');

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      try {
        const method = type ? 'PUT' : 'POST';
        const url = type 
          ? `/api/config/vehicles/types/${type.tipo}`
          : '/api/config/vehicles/types';
        
        const response = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });

        if (response.ok) {
          toast.success(type ? 'Tipo actualizado' : 'Tipo creado');
          onSave();
        } else {
          const error = await response.json();
          toast.error(error.detail || 'Error guardando');
        }
      } catch (error) {
        toast.error('Error de conexión');
      }
    };

    const addRequisito = () => {
      if (newRequisito.trim()) {
        setFormData({
          ...formData,
          requisitos_especiales: [...formData.requisitos_especiales, newRequisito.trim()]
        });
        setNewRequisito('');
      }
    };

    const removeRequisito = (index) => {
      setFormData({
        ...formData,
        requisitos_especiales: formData.requisitos_especiales.filter((_, i) => i !== index)
      });
    };

    return (
      <form onSubmit={handleSubmit} className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Identificador */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Identificador (no se puede cambiar)
            </label>
            <input
              type="text"
              value={formData.tipo}
              onChange={(e) => setFormData({...formData, tipo: e.target.value.toLowerCase().replace(/\s/g, '_')})}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              required
              disabled={!!type}
              placeholder="ej: nuevo_vehiculo"
            />
          </div>

          {/* Nombre para mostrar */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Nombre para mostrar
            </label>
            <input
              type="text"
              value={formData.nombre_display}
              onChange={(e) => setFormData({...formData, nombre_display: e.target.value})}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              required
              placeholder="ej: Nuevo Vehículo"
            />
          </div>

          {/* Duración */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Duración del lavado (minutos)
            </label>
            <input
              type="number"
              value={formData.duracion_minutos}
              onChange={(e) => setFormData({...formData, duracion_minutos: parseInt(e.target.value)})}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              required
              min="1"
              max="480"
            />
          </div>

          {/* Prioridad */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Prioridad (1=máxima, 10=mínima)
            </label>
            <select
              value={formData.prioridad}
              onChange={(e) => setFormData({...formData, prioridad: parseInt(e.target.value)})}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            >
              {[1,2,3,4,5,6,7,8,9,10].map(p => (
                <option key={p} value={p}>
                  {p} {p === 1 ? '(Máxima)' : p === 10 ? '(Mínima)' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Hora inicio */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Hora de inicio permitida
            </label>
            <input
              type="time"
              value={formData.hora_inicio}
              onChange={(e) => setFormData({...formData, hora_inicio: e.target.value})}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* Hora fin */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Hora de fin permitida
            </label>
            <input
              type="time"
              value={formData.hora_fin}
              onChange={(e) => setFormData({...formData, hora_fin: e.target.value})}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* Color */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Color en interfaz
            </label>
            <div className="flex gap-2">
              {availableColors.map(color => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setFormData({...formData, color_ui: color})}
                  className={`w-8 h-8 rounded border-2 ${
                    formData.color_ui === color ? 'border-white' : 'border-gray-600'
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          {/* Icono */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Icono
            </label>
            <div className="flex gap-2">
              {Object.entries(availableIcons).map(([key, icon]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setFormData({...formData, icono: key})}
                  className={`p-2 rounded border ${
                    formData.icono === key 
                      ? 'border-blue-500 bg-blue-500/20 text-blue-400' 
                      : 'border-gray-600 text-gray-400 hover:border-gray-500'
                  }`}
                >
                  {icon}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Ventana estricta */}
        <div className="mt-4">
          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              checked={formData.ventana_estricta}
              onChange={(e) => setFormData({...formData, ventana_estricta: e.target.checked})}
              className="mr-2"
            />
            <span className="text-sm">
              Ventana de tiempo estricta (debe llegar en el horario exacto)
            </span>
          </label>
        </div>

        {/* Requisitos especiales */}
        <div className="mt-4">
          <label className="block text-sm font-medium mb-1 text-gray-300">
            Requisitos especiales
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={newRequisito}
              onChange={(e) => setNewRequisito(e.target.value)}
              className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              placeholder="Agregar requisito..."
            />
            <button
              type="button"
              onClick={addRequisito}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              <Plus size={16} />
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.requisitos_especiales.map((req, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm flex items-center gap-1"
              >
                {req}
                <button
                  type="button"
                  onClick={() => removeRequisito(index)}
                  className="text-blue-300 hover:text-blue-200"
                >
                  <Trash2 size={14} />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Botones */}
        <div className="flex justify-end gap-2 mt-6">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-400 hover:text-gray-300"
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-2"
          >
            <Save size={16} />
            Guardar
          </button>
        </div>
      </form>
    );
  };

  // Componente para mostrar tipo de vehículo
  const VehicleTypeCard = ({ type }) => {
    const [expanded, setExpanded] = useState(false);

    const handleDelete = async () => {
      if (window.confirm(`¿Desactivar el tipo "${type.nombre_display}"?`)) {
        try {
          const response = await fetch(`/api/config/vehicles/types/${type.tipo}`, {
            method: 'DELETE'
          });
          
          if (response.ok) {
            toast.success('Tipo desactivado');
            loadConfiguration();
          }
        } catch (error) {
          toast.error('Error desactivando tipo');
        }
      }
    };

    return (
      <div className={`bg-gray-800 border border-gray-700 rounded-lg p-4 ${!type.activo ? 'opacity-50' : ''}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div 
              className="p-2 rounded"
              style={{ backgroundColor: type.color_ui + '20', color: type.color_ui }}
            >
              {availableIcons[type.icono] || <Truck size={20} />}
            </div>
            <div>
              <h3 className="font-semibold text-white">{type.nombre_display}</h3>
              <p className="text-sm text-gray-400">ID: {type.tipo}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1 hover:bg-gray-700 rounded text-gray-400"
            >
              {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
            <button
              onClick={() => setEditingType(type)}
              className="p-1 hover:bg-gray-700 rounded text-gray-400"
            >
              <Edit2 size={16} />
            </button>
            <button
              onClick={handleDelete}
              className="p-1 hover:bg-gray-700 rounded text-red-400"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>

        {expanded && (
          <div className="mt-4 pt-4 border-t border-gray-700 space-y-2 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-gray-400">Duración:</span>
                <span className="ml-2 font-medium text-white">{type.duracion_minutos} minutos</span>
              </div>
              <div>
                <span className="text-gray-400">Prioridad:</span>
                <span className="ml-2 font-medium text-white">{type.prioridad}</span>
              </div>
              <div>
                <span className="text-gray-400">Horario:</span>
                <span className="ml-2 font-medium text-white">
                  {type.hora_inicio && type.hora_fin 
                    ? `${type.hora_inicio} - ${type.hora_fin}`
                    : 'Sin restricción'}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Ventana estricta:</span>
                <span className="ml-2 font-medium text-white">
                  {type.ventana_estricta ? 'Sí' : 'No'}
                </span>
              </div>
            </div>
            
            {type.requisitos_especiales.length > 0 && (
              <div>
                <span className="text-gray-400">Requisitos especiales:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {type.requisitos_especiales.map((req, i) => (
                    <span key={i} className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">
                      {req}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  // Componente para reglas de conflicto
  const ConflictRuleForm = ({ rule, onSave, onCancel }) => {
    const [formData, setFormData] = useState(rule || {
      nombre: '',
      descripcion: '',
      vehiculo_afectado: '',
      condicion: {},
      accion: 'RECHAZAR',
      mensaje: '',
      nivel_alerta: 'medium',
      activa: true
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      try {
        const method = rule ? 'PUT' : 'POST';
        const url = rule 
          ? `/api/config/vehicles/rules/${rule.nombre}`
          : '/api/config/vehicles/rules';
        
        const response = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });

        if (response.ok) {
          toast.success(rule ? 'Regla actualizada' : 'Regla creada');
          onSave();
        } else {
          const error = await response.json();
          toast.error(error.detail || 'Error guardando');
        }
      } catch (error) {
        toast.error('Error de conexión');
      }
    };

    return (
      <form onSubmit={handleSubmit} className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Nombre de la regla (identificador único)
            </label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => setFormData({...formData, nombre: e.target.value.toLowerCase().replace(/\s/g, '_')})}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              required
              disabled={!!rule}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({...formData, descripcion: e.target.value})}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              rows="2"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-300">
                Vehículo afectado
              </label>
              <select
                value={formData.vehiculo_afectado}
                onChange={(e) => setFormData({...formData, vehiculo_afectado: e.target.value})}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                required
              >
                <option value="">Seleccionar...</option>
                <option value="*">Todos los vehículos</option>
                {vehicleTypes.filter(vt => vt.activo).map(vt => (
                  <option key={vt.tipo} value={vt.tipo}>
                    {vt.nombre_display}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-gray-300">
                Acción
              </label>
              <select
                value={formData.accion}
                onChange={(e) => setFormData({...formData, accion: e.target.value})}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="RECHAZAR">RECHAZAR - No permitir acceso</option>
                <option value="ALERTAR">ALERTAR - Permitir con alerta</option>
                <option value="PERMITIR_CON_ALERTA">PERMITIR CON ALERTA - Acceso con notificación</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-gray-300">
                Nivel de alerta
              </label>
              <select
                value={formData.nivel_alerta}
                onChange={(e) => setFormData({...formData, nivel_alerta: e.target.value})}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="low">Bajo</option>
                <option value="medium">Medio</option>
                <option value="high">Alto</option>
                <option value="critical">Crítico</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Mensaje para el operador
            </label>
            <textarea
              value={formData.mensaje}
              onChange={(e) => setFormData({...formData, mensaje: e.target.value})}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              rows="2"
              required
              placeholder="Mensaje claro explicando la decisión..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Condiciones (JSON)
            </label>
            <textarea
              value={JSON.stringify(formData.condicion, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  setFormData({...formData, condicion: parsed});
                } catch (error) {
                  // Permitir edición aunque no sea JSON válido aún
                }
              }}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white font-mono text-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none"
              rows="4"
              placeholder={`{
  "hora_llegada_despues": "07:00",
  "conflicto_con": "genetica"
}`}
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-400 hover:text-gray-300"
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-2"
          >
            <Save size={16} />
            Guardar
          </button>
        </div>
      </form>
    );
  };

  // Configuración general del sistema
  const SystemSettingsForm = () => {
    const [settings, setSettings] = useState({...systemSettings});
    const [saving, setSaving] = useState(false);
    
    // Sincronizar settings cuando systemSettings cambie
    useEffect(() => {
      setSettings({...systemSettings});
    }, [systemSettings]);

    const handleSave = async () => {
      setSaving(true);
      try {
        const response = await fetch('/api/config/vehicles/settings', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(settings)
        });

        if (response.ok) {
          toast.success('Configuración guardada');
          setSystemSettings(settings);
        } else {
          toast.error('Error guardando configuración');
        }
      } catch (error) {
        toast.error('Error de conexión');
      } finally {
        setSaving(false);
      }
    };

    return (
      <div className="bg-gray-800 rounded-lg shadow border border-gray-700 p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
          <Settings size={20} />
          Configuración General del Sistema
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Lavados simultáneos máximos
            </label>
            <input
              type="number"
              value={settings.max_lavados_simultaneos || 1}
              onChange={(e) => setSettings({
                ...settings, 
                max_lavados_simultaneos: parseInt(e.target.value)
              })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              min="1"
              max="10"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Tiempo buffer entre lavados (minutos)
            </label>
            <input
              type="number"
              value={settings.tiempo_buffer_minutos || 15}
              onChange={(e) => setSettings({
                ...settings, 
                tiempo_buffer_minutos: parseInt(e.target.value)
              })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              min="0"
              max="60"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Acción para vehículo desconocido
            </label>
            <select
              value={settings.accion_vehiculo_desconocido || 'RECHAZAR'}
              onChange={(e) => setSettings({
                ...settings, 
                accion_vehiculo_desconocido: e.target.value
              })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="RECHAZAR">RECHAZAR - No permitir acceso</option>
              <option value="ALERTAR">ALERTAR - Notificar supervisor</option>
              <option value="PERMITIR">PERMITIR - Acceso libre</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-300">
              Umbral de confianza detección (0-1)
            </label>
            <input
              type="number"
              value={settings.umbral_confianza_deteccion || 0.7}
              onChange={(e) => setSettings({
                ...settings, 
                umbral_confianza_deteccion: parseFloat(e.target.value)
              })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              min="0"
              max="1"
              step="0.1"
            />
          </div>
        </div>

        <div className="mt-4 space-y-2">
          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              checked={settings.capturar_foto_rechazos}
              onChange={(e) => setSettings({
                ...settings, 
                capturar_foto_rechazos: e.target.checked
              })}
              className="mr-2"
            />
            <span className="text-sm">Capturar foto de vehículos rechazados</span>
          </label>

          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              checked={settings.notificar_telegram}
              onChange={(e) => setSettings({
                ...settings, 
                notificar_telegram: e.target.checked
              })}
              className="mr-2"
            />
            <span className="text-sm">Enviar notificaciones por Telegram</span>
          </label>

          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              checked={settings.modo_debug}
              onChange={(e) => setSettings({
                ...settings, 
                modo_debug: e.target.checked
              })}
              className="mr-2"
            />
            <span className="text-sm">Modo debug (más información en logs)</span>
          </label>
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-2 disabled:opacity-50"
          >
            <Save size={16} />
            {saving ? 'Guardando...' : 'Guardar Cambios'}
          </button>
        </div>
      </div>
    );
  };

  // Funciones de exportación/importación
  const handleExport = async () => {
    try {
      const response = await fetch('/api/config/vehicles/export');
      const config = await response.json();
      
      const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `yomjai_vehicle_config_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      
      toast.success('Configuración exportada');
    } catch (error) {
      toast.error('Error exportando configuración');
    }
  };

  const handleImport = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const config = JSON.parse(text);
      
      if (window.confirm('¿Importar esta configuración? Esto sobrescribirá la configuración actual.')) {
        const response = await fetch('/api/config/vehicles/import', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config)
        });

        if (response.ok) {
          toast.success('Configuración importada');
          loadConfiguration();
        } else {
          const error = await response.json();
          toast.error(error.detail || 'Error importando');
        }
      }
    } catch (error) {
      toast.error('Archivo inválido');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Configuración de Vehículos</h1>
        <p className="text-gray-600">
          Configure tipos de vehículos, duraciones de lavado, horarios y reglas de conflicto
        </p>
      </div>

      {/* Botones de exportar/importar */}
      <div className="flex justify-end gap-2 mb-6">
        <button
          onClick={handleExport}
          className="px-4 py-2 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 flex items-center gap-2 text-gray-300"
        >
          <Package size={16} />
          Exportar
        </button>
        <label className="px-4 py-2 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 flex items-center gap-2 cursor-pointer text-gray-300">
          <Package size={16} />
          Importar
          <input
            type="file"
            accept=".json"
            onChange={handleImport}
            className="hidden"
          />
        </label>
      </div>

      {/* Tipos de vehículos */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Truck size={24} />
            Tipos de Vehículos ({vehicleTypes.length})
          </h2>
          <button
            onClick={() => setShowNewType(true)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-2"
          >
            <Plus size={16} />
            Nuevo Tipo
          </button>
        </div>

        {showNewType && (
          <div className="mb-4">
            <VehicleTypeForm
              onSave={() => {
                setShowNewType(false);
                loadConfiguration();
              }}
              onCancel={() => setShowNewType(false)}
            />
          </div>
        )}

        {editingType && (
          <div className="mb-4">
            <VehicleTypeForm
              type={editingType}
              onSave={() => {
                setEditingType(null);
                loadConfiguration();
              }}
              onCancel={() => setEditingType(null)}
            />
          </div>
        )}

        {!showNewType && !editingType && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {vehicleTypes.map(type => (
              <VehicleTypeCard key={type.tipo} type={type} />
            ))}
          </div>
        )}
      </div>

      {/* Reglas de conflicto */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <AlertTriangle size={24} />
            Reglas de Conflicto ({conflictRules.length})
          </h2>
          <button
            onClick={() => setShowNewRule(true)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-2"
          >
            <Plus size={16} />
            Nueva Regla
          </button>
        </div>

        {showNewRule && (
          <div className="mb-4">
            <ConflictRuleForm
              onSave={() => {
                setShowNewRule(false);
                loadConfiguration();
              }}
              onCancel={() => setShowNewRule(false)}
            />
          </div>
        )}

        {editingRule && (
          <div className="mb-4">
            <ConflictRuleForm
              rule={editingRule}
              onSave={() => {
                setEditingRule(null);
                loadConfiguration();
              }}
              onCancel={() => setEditingRule(null)}
            />
          </div>
        )}

        {!showNewRule && !editingRule && (
          <div className="space-y-4">
            {conflictRules.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                No hay reglas de conflicto configuradas
              </div>
            ) : (
              conflictRules.map(rule => (
                <div 
                  key={rule.nombre} 
                  className={`bg-gray-800 border border-gray-700 rounded-lg p-4 ${!rule.activa ? 'opacity-50' : ''}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-white">{rule.descripcion}</h3>
                      <p className="text-sm text-gray-400 mt-1">
                        Vehículo: {rule.vehiculo_afectado === '*' ? 'Todos' : rule.vehiculo_afectado}
                      </p>
                      <p className="text-sm mt-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          rule.accion === 'RECHAZAR' 
                            ? 'bg-red-500/20 text-red-400' 
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {rule.accion}
                        </span>
                        <span className={`ml-2 px-2 py-1 rounded text-xs ${
                          rule.nivel_alerta === 'critical' 
                            ? 'bg-red-500/20 text-red-400'
                            : rule.nivel_alerta === 'high'
                            ? 'bg-orange-500/20 text-orange-400'
                            : 'bg-blue-500/20 text-blue-400'
                        }`}>
                          Alerta: {rule.nivel_alerta}
                        </span>
                      </p>
                      <p className="text-sm text-gray-300 mt-2 italic">
                        "{rule.mensaje}"
                      </p>
                    </div>
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => {
                          console.log('Editando regla:', rule);
                          setEditingRule(rule);
                        }}
                        className="p-1 hover:bg-gray-700 rounded text-gray-400"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={async () => {
                          if (window.confirm('¿Desactivar esta regla?')) {
                            try {
                              await fetch(`/api/config/vehicles/rules/${rule.nombre}`, {
                                method: 'DELETE'
                              });
                              toast.success('Regla desactivada');
                              loadConfiguration();
                            } catch (error) {
                              toast.error('Error desactivando regla');
                            }
                          }
                        }}
                        className="p-1 hover:bg-gray-700 rounded text-red-400"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Configuración general */}
      <SystemSettingsForm />
    </div>
  );
};

export default VehicleConfiguration;
