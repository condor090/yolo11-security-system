import React, { useState, useEffect } from 'react';
import { 
  Clock, Search, Camera, AlertCircle, Info, CheckCircle,
  Filter, X, ChevronDown, Calendar, Image as ImageIcon
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';

const EventsViewer = () => {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [dateFilter, setDateFilter] = useState('today');
  
  // Tipos de eventos para filtrado
  const eventTypes = {
    all: { label: 'Todos', icon: null },
    door_open: { label: 'Puertas Abiertas', icon: '🚪', color: 'text-red-400' },
    door_close: { label: 'Puertas Cerradas', icon: '🔒', color: 'text-green-400' },
    alarm: { label: 'Alarmas', icon: '🚨', color: 'text-yellow-400' },
    detection: { label: 'Detecciones', icon: '👁️', color: 'text-blue-400' },
    system: { label: 'Sistema', icon: '⚙️', color: 'text-gray-400' }
  };

  useEffect(() => {
    loadEvents();
    // Recargar eventos cada 30 segundos
    const interval = setInterval(loadEvents, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    filterEvents();
  }, [events, searchTerm, filterType, dateFilter]);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/events/recent', {
        params: { limit: 100 }
      });
      setEvents(response.data.events || []);
    } catch (error) {
      console.error('Error cargando eventos:', error);
      toast.error('Error al cargar eventos');
    } finally {
      setLoading(false);
    }
  };

  const filterEvents = () => {
    let filtered = [...events];

    // Filtrar por búsqueda
    if (searchTerm) {
      filtered = filtered.filter(event => 
        event.event.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (event.description && event.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (event.zone_id && event.zone_id.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Filtrar por tipo
    if (filterType !== 'all') {
      filtered = filtered.filter(event => event.event_type === filterType);
    }

    // Filtrar por fecha
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    
    switch (dateFilter) {
      case 'today':
        filtered = filtered.filter(event => event.date === today);
        break;
      case 'week':
        const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(event => 
          new Date(event.datetime) >= weekAgo
        );
        break;
      case 'month':
        const monthAgo = new Date(now - 30 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(event => 
          new Date(event.datetime) >= monthAgo
        );
        break;
    }

    setFilteredEvents(filtered);
  };

  const getEventIcon = (event) => {
    const typeConfig = eventTypes[event.event_type];
    if (typeConfig && typeConfig.icon) {
      return <span className="text-lg">{typeConfig.icon}</span>;
    }
    
    // Iconos por severidad si no hay tipo específico
    switch (event.type) {
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      default:
        return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  const getSeverityBadge = (type) => {
    const badges = {
      info: 'bg-blue-500/20 text-blue-400',
      warning: 'bg-yellow-500/20 text-yellow-400',
      error: 'bg-red-500/20 text-red-400',
      success: 'bg-green-500/20 text-green-400'
    };
    return badges[type] || badges.info;
  };

  return (
    <div className="space-y-6">
      {/* Header con búsqueda y filtros */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" />
            Eventos del Sistema
          </h3>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${
              showFilters ? 'bg-blue-500/20 text-blue-400' : 'bg-gray-700 text-gray-400'
            }`}
          >
            <Filter className="w-4 h-4" />
            Filtros
            <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Barra de búsqueda */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar eventos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Filtros expandibles */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-700">
                {/* Filtro por tipo */}
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Tipo de Evento
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(eventTypes).map(([key, config]) => (
                      <button
                        key={key}
                        onClick={() => setFilterType(key)}
                        className={`px-3 py-2 rounded-lg text-sm transition-all flex items-center gap-2 ${
                          filterType === key
                            ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        {config.icon && <span>{config.icon}</span>}
                        {config.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Filtro por fecha */}
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Período
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { value: 'today', label: 'Hoy' },
                      { value: 'week', label: 'Semana' },
                      { value: 'month', label: 'Mes' }
                    ].map(option => (
                      <button
                        key={option.value}
                        onClick={() => setDateFilter(option.value)}
                        className={`px-3 py-2 rounded-lg text-sm transition-all ${
                          dateFilter === option.value
                            ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Lista de eventos */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl border border-gray-700/50 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-gray-400 mt-4">Cargando eventos...</p>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="p-8 text-center">
            <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No se encontraron eventos</p>
            {searchTerm && (
              <p className="text-sm text-gray-500 mt-2">
                Intenta con otros términos de búsqueda
              </p>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-700">
            {filteredEvents.map((event) => (
              <motion.div
                key={event.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-4 hover:bg-gray-700/30 transition-colors cursor-pointer"
                onClick={() => setSelectedEvent(event)}
              >
                <div className="flex items-start gap-4">
                  {/* Icono del evento */}
                  <div className="flex-shrink-0 mt-1">
                    {getEventIcon(event)}
                  </div>

                  {/* Contenido del evento */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h4 className="font-medium text-white truncate">
                          {event.event}
                        </h4>
                        {event.description && (
                          <p className="text-sm text-gray-400 mt-1">
                            {event.description}
                          </p>
                        )}
                        <div className="flex items-center gap-4 mt-2">
                          <span className="text-xs text-gray-500">
                            {event.time} • {event.date}
                          </span>
                          {event.zone_id && (
                            <span className="text-xs text-gray-500">
                              Zona: {event.zone_id}
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {/* Indicador de imagen */}
                        {event.has_image && (
                          <div className="p-1 bg-blue-500/20 rounded">
                            <Camera className="w-4 h-4 text-blue-400" />
                          </div>
                        )}
                        
                        {/* Badge de severidad */}
                        <span className={`px-2 py-1 text-xs rounded-full ${getSeverityBadge(event.type)}`}>
                          {event.type}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Modal de detalle del evento */}
      <AnimatePresence>
        {selectedEvent && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
            >
              {/* Header del modal */}
              <div className="p-6 border-b border-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {getEventIcon(selectedEvent)}
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        {selectedEvent.event}
                      </h3>
                      <p className="text-sm text-gray-400 mt-1">
                        {selectedEvent.datetime && new Date(selectedEvent.datetime).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedEvent(null)}
                    className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Contenido del modal */}
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {/* Imagen del evento si existe */}
                {selectedEvent.thumbnail && (
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-400 mb-3">Captura del Evento</h4>
                    <div className="bg-black rounded-lg overflow-hidden">
                      <img 
                        src={`data:image/jpeg;base64,${selectedEvent.thumbnail}`}
                        alt="Captura del evento"
                        className="w-full"
                      />
                    </div>
                  </div>
                )}

                {/* Detalles del evento */}
                <div className="space-y-4">
                  {selectedEvent.description && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-400 mb-1">Descripción</h4>
                      <p className="text-white">{selectedEvent.description}</p>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-400 mb-1">Tipo de Evento</h4>
                      <p className="text-white flex items-center gap-2">
                        {eventTypes[selectedEvent.event_type]?.icon}
                        {eventTypes[selectedEvent.event_type]?.label || selectedEvent.event_type}
                      </p>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-400 mb-1">Severidad</h4>
                      <span className={`inline-flex px-2 py-1 text-sm rounded-full ${getSeverityBadge(selectedEvent.type)}`}>
                        {selectedEvent.type}
                      </span>
                    </div>

                    {selectedEvent.zone_id && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-400 mb-1">Zona</h4>
                        <p className="text-white">{selectedEvent.zone_id}</p>
                      </div>
                    )}

                    <div>
                      <h4 className="text-sm font-medium text-gray-400 mb-1">ID del Evento</h4>
                      <p className="text-white font-mono">#{selectedEvent.id}</p>
                    </div>
                  </div>

                  {/* Metadata adicional */}
                  {selectedEvent.metadata && Object.keys(selectedEvent.metadata).length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-400 mb-2">Información Adicional</h4>
                      <div className="bg-gray-900 rounded-lg p-3">
                        <pre className="text-sm text-gray-300 overflow-x-auto">
                          {JSON.stringify(selectedEvent.metadata, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Footer del modal */}
              <div className="p-6 border-t border-gray-700">
                <div className="flex justify-end gap-3">
                  {selectedEvent.image_path && (
                    <button
                      onClick={() => {
                        // Aquí podrías implementar descarga de imagen completa
                        toast.success('Función de descarga en desarrollo');
                      }}
                      className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors flex items-center gap-2"
                    >
                      <ImageIcon className="w-4 h-4" />
                      Ver Imagen Completa
                    </button>
                  )}
                  <button
                    onClick={() => setSelectedEvent(null)}
                    className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EventsViewer;
