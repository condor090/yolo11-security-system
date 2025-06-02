import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Camera, Plus, Edit2, Trash2, Save, X, 
  Wifi, WifiOff, Settings, Eye, EyeOff,
  AlertCircle, CheckCircle, RefreshCw, Copy,
  Search, Loader, Network, Info
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = 'http://localhost:8889';

export default function CameraConfig() {
  const [cameras, setCameras] = useState({});
  const [isAddingCamera, setIsAddingCamera] = useState(false);
  const [editingCamera, setEditingCamera] = useState(null);
  const [testingCamera, setTestingCamera] = useState(null);
  const [showPasswords, setShowPasswords] = useState({});
  const [isScanning, setIsScanning] = useState(false);
  const [scanResults, setScanResults] = useState([]);
  const [showScanResults, setShowScanResults] = useState(false);
  
  // Form data para nueva cámara o edición
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    ip: '',
    username: 'admin',
    password: '',
    rtsp_port: 554,
    channel: 1,
    stream: 'main',
    zone_id: '',
    enabled: true
  });

  // Zonas predefinidas
  const predefinedZones = [
    { id: 'door_1', name: 'Puerta Principal', delay: 30 },
    { id: 'door_2', name: 'Puerta Secundaria', delay: 30 },
    { id: 'entrance', name: 'Entrada', delay: 15 },
    { id: 'loading', name: 'Zona de Carga', delay: 300 },
    { id: 'emergency', name: 'Salida de Emergencia', delay: 5 },
    { id: 'warehouse', name: 'Almacén', delay: 60 },
    { id: 'office', name: 'Oficina', delay: 45 },
    { id: 'parking', name: 'Estacionamiento', delay: 120 }
  ];

  // Cargar cámaras al montar
  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/cameras`);
      setCameras(response.data.cameras || {});
    } catch (error) {
      toast.error('Error cargando cámaras');
      console.error(error);
    }
  };

  // Función para escanear la red
  const scanNetwork = async () => {
    setIsScanning(true);
    setScanResults([]);
    setShowScanResults(true);
    
    try {
      const response = await axios.post(`${API_URL}/api/cameras/scan`);
      setScanResults(response.data.cameras || []);
      
      if (response.data.cameras.length === 0) {
        toast.error('No se encontraron cámaras en la red');
      } else {
        toast.success(`${response.data.cameras.length} cámara(s) encontrada(s)`);
      }
    } catch (error) {
      toast.error('Error escaneando la red');
      console.error(error);
    } finally {
      setIsScanning(false);
    }
  };

  // Usar cámara encontrada en el formulario
  const useScanResult = (camera) => {
    setFormData({
      ...formData,
      ip: camera.ip,
      rtsp_port: camera.rtsp_port || 554,
      name: camera.name || `Cámara ${camera.ip}`,
      id: generateCameraId()
    });
    setShowScanResults(false);
    setIsAddingCamera(true);
    toast.success('Datos cargados en el formulario');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingCamera) {
        // Actualizar cámara existente
        await axios.put(`${API_URL}/api/cameras/${editingCamera}`, formData);
        toast.success('Cámara actualizada');
      } else {
        // Agregar nueva cámara
        await axios.post(`${API_URL}/api/cameras`, formData);
        toast.success('Cámara agregada');
      }
      
      // Recargar lista después de un breve delay para dar tiempo al backend
      setTimeout(() => {
        loadCameras();
      }, 500);
      
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error guardando cámara');
    }
  };

  const handleDelete = async (cameraId) => {
    if (window.confirm('¿Eliminar esta cámara?')) {
      try {
        await axios.delete(`${API_URL}/api/cameras/${cameraId}`);
        toast.success('Cámara eliminada');
        loadCameras();
      } catch (error) {
        toast.error('Error eliminando cámara');
      }
    }
  };

  const handleTest = async (cameraId) => {
    setTestingCamera(cameraId);
    try {
      const response = await axios.post(`${API_URL}/api/cameras/${cameraId}/test`);
      if (response.data.success) {
        toast.success('Conexión exitosa');
      } else {
        toast.error(response.data.message || 'No se pudo conectar');
      }
    } catch (error) {
      toast.error('Error probando conexión');
    } finally {
      setTestingCamera(null);
    }
  };

  const startEdit = async (cameraId) => {
    try {
      // Obtener datos completos de la cámara desde el backend
      const response = await axios.get(`${API_URL}/api/cameras/${cameraId}`);
      const cameraData = response.data;
      
      setFormData({
        id: cameraData.id || cameraId,
        name: cameraData.name || '',
        ip: cameraData.ip || '',
        username: cameraData.username || 'admin',
        password: cameraData.password || '',
        rtsp_port: cameraData.rtsp_port || 554,
        channel: cameraData.channel || 1,
        stream: cameraData.stream || 'main',
        zone_id: cameraData.zone_id || '',
        enabled: cameraData.enabled !== false
      });
      setEditingCamera(cameraId);
      setIsAddingCamera(true);
    } catch (error) {
      // Si falla, usar los datos locales
      const camera = cameras[cameraId];
      if (camera) {
        setFormData({
          id: cameraId,
          name: camera.name || '',
          ip: camera.ip || '',
          username: camera.username || 'admin',
          password: '', // Por seguridad, no se muestra en el frontend
          rtsp_port: camera.rtsp_port || 554,
          channel: camera.channel || 1,
          stream: camera.stream || 'main',
          zone_id: camera.zone_id || '',
          enabled: camera.enabled !== false
        });
        setEditingCamera(cameraId);
        setIsAddingCamera(true);
      }
      toast.error('Usando datos locales. La contraseña debe ingresarse nuevamente.');
    }
  };

  const resetForm = () => {
    setFormData({
      id: '',
      name: '',
      ip: '',
      username: 'admin',
      password: '',
      rtsp_port: 554,
      channel: 1,
      stream: 'main',
      zone_id: '',
      enabled: true
    });
    setEditingCamera(null);
    setIsAddingCamera(false);
  };

  const generateCameraId = () => {
    const count = Object.keys(cameras).length;
    return `cam_${String(count + 1).padStart(3, '0')}`;
  };

  const copyRtspUrl = (camera) => {
    const streamType = camera.stream === 'main' ? '0' : '1';
    const url = `rtsp://${camera.username}:${camera.password}@${camera.ip}:${camera.rtsp_port}/Streaming/Channels/${camera.channel}0${streamType}`;
    navigator.clipboard.writeText(url);
    toast.success('URL RTSP copiada');
  };

  const handleReconnect = async (cameraId) => {
    try {
      toast.loading(`Reconectando cámara ${cameraId}...`, { id: `reconnect-${cameraId}` });
      
      const response = await axios.post(`${API_URL}/api/cameras/${cameraId}/reconnect`);
      
      if (response.data.success) {
        toast.success(response.data.message, { id: `reconnect-${cameraId}` });
        // Recargar estado después de un momento
        setTimeout(() => {
          loadCameras();
        }, 1000);
      } else {
        toast.error(response.data.message || 'No se pudo reconectar', { id: `reconnect-${cameraId}` });
      }
    } catch (error) {
      toast.error('Error reconectando cámara', { id: `reconnect-${cameraId}` });
      console.error(error);
    }
  };

  const togglePassword = (cameraId) => {
    setShowPasswords(prev => ({ ...prev, [cameraId]: !prev[cameraId] }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Camera className="w-6 h-6 text-blue-400" />
          Configuración de Cámaras
        </h2>
        
        <div className="flex gap-3">
          <button
            onClick={scanNetwork}
            disabled={isScanning}
            className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:cursor-not-allowed px-4 py-2 rounded-lg transition-colors"
          >
            {isScanning ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Escaneando...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Buscar Cámaras
              </>
            )}
          </button>
          
          <button
            onClick={() => {
              setFormData({ ...formData, id: generateCameraId() });
              setIsAddingCamera(true);
            }}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Agregar Manual
          </button>
        </div>
      </div>

      {/* Panel de resultados del escaneo */}
      <AnimatePresence>
        {showScanResults && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-6"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Network className="w-5 h-5 text-purple-400" />
                Cámaras Encontradas en la Red
              </h3>
              <button
                onClick={() => setShowScanResults(false)}
                className="p-1 hover:bg-gray-700 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {isScanning ? (
              <div className="text-center py-8">
                <Loader className="w-12 h-12 animate-spin mx-auto text-purple-400 mb-4" />
                <p className="text-gray-400">Escaneando red local...</p>
                <p className="text-sm text-gray-500 mt-2">Esto puede tomar 1-2 minutos</p>
              </div>
            ) : scanResults.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {scanResults.map((camera, idx) => (
                  <div key={idx} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <p className="font-medium flex items-center gap-2">
                          {camera.confirmed_hikvision ? (
                            <CheckCircle className="w-4 h-4 text-green-400" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-yellow-400" />
                          )}
                          {camera.ip}
                        </p>
                        <p className="text-sm text-gray-400">
                          {camera.confirmed_hikvision ? 'Hikvision confirmado' : 'Cámara IP genérica'}
                        </p>
                      </div>
                      <button
                        onClick={() => useScanResult(camera)}
                        className="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded text-sm transition-colors"
                      >
                        Usar
                      </button>
                    </div>
                    
                    <div className="space-y-1 text-sm">
                      <p className="text-gray-400">
                        RTSP: Puerto {camera.rtsp_port || 554} {camera.rtsp_open ? '✅' : '❌'}
                      </p>
                      {camera.http_port && (
                        <p className="text-gray-400">
                          HTTP: Puerto {camera.http_port} ✅
                        </p>
                      )}
                      {camera.model && (
                        <p className="text-gray-400">
                          Modelo: {camera.model}
                        </p>
                      )}
                    </div>

                    {camera.http_port && (
                      <a
                        href={`http://${camera.ip}:${camera.http_port}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 mt-2"
                      >
                        Abrir interfaz web →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <WifiOff className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No se encontraron cámaras en la red</p>
                <p className="text-sm mt-2">Verifica que las cámaras estén encendidas y en la misma red</p>
              </div>
            )}

            {!isScanning && scanResults.length === 0 && (
              <div className="mt-4 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                <p className="text-sm text-blue-400 flex items-start gap-2">
                  <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>
                    El escáner busca dispositivos con puerto RTSP (554) abierto. 
                    Asegúrate de que las cámaras estén en la misma red y no haya firewall bloqueando.
                  </span>
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Lista de cámaras */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {Object.entries(cameras).map(([camId, camera]) => (
          <motion.div
            key={camId}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gray-800/50 backdrop-blur rounded-xl p-5 border border-gray-700/50"
          >
            {/* Header de la cámara */}
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  {camera.connected ? (
                    <Wifi className="w-5 h-5 text-green-400" />
                  ) : (
                    <WifiOff className="w-5 h-5 text-red-400" />
                  )}
                  {camera.name}
                </h3>
                <p className="text-sm text-gray-400">ID: {camId}</p>
              </div>
              
              <div className="flex items-center gap-2">
                {camera.enabled && !camera.connected && (
                  <button
                    onClick={() => handleReconnect(camId)}
                    className="p-2 hover:bg-gray-700 rounded transition-colors text-yellow-400"
                    title="Reconectar cámara"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                )}
                
                <button
                  onClick={() => handleTest(camId)}
                  className="p-2 hover:bg-gray-700 rounded transition-colors"
                  title="Probar conexión"
                  disabled={testingCamera === camId}
                >
                  {testingCamera === camId ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Wifi className="w-4 h-4" />
                  )}
                </button>
                
                <button
                  onClick={() => startEdit(camId)}
                  className="p-2 hover:bg-gray-700 rounded transition-colors"
                  title="Editar"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                
                <button
                  onClick={() => handleDelete(camId)}
                  className="p-2 hover:bg-gray-700 rounded transition-colors text-red-400"
                  title="Eliminar"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Detalles de la cámara */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">IP:</span>
                <span className="font-mono">{camera.ip}:{camera.rtsp_port}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-400">Usuario:</span>
                <span>{camera.username}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Contraseña:</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono">
                    {showPasswords[camId] ? camera.password : '••••••••'}
                  </span>
                  <button
                    onClick={() => togglePassword(camId)}
                    className="p-1 hover:bg-gray-700 rounded"
                  >
                    {showPasswords[camId] ? (
                      <EyeOff className="w-3 h-3" />
                    ) : (
                      <Eye className="w-3 h-3" />
                    )}
                  </button>
                </div>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-400">Canal/Stream:</span>
                <span>{camera.channel} / {camera.stream}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-400">Zona:</span>
                <span className="text-blue-400">
                  {predefinedZones.find(z => z.id === camera.zone_id)?.name || camera.zone_id || 'Sin asignar'}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-400">Estado:</span>
                <span className={camera.enabled ? 'text-green-400' : 'text-gray-500'}>
                  {camera.enabled ? 'Habilitada' : 'Deshabilitada'}
                </span>
              </div>
            </div>

            {/* Acciones adicionales */}
            <div className="mt-4 pt-4 border-t border-gray-700/50">
              <button
                onClick={() => copyRtspUrl(camera)}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-gray-700/50 hover:bg-gray-700 rounded transition-colors text-sm"
              >
                <Copy className="w-4 h-4" />
                Copiar URL RTSP
              </button>
            </div>

            {/* Estado de conexión */}
            {camera.connected !== undefined && (
              <div className={`mt-3 p-3 rounded-lg text-sm ${
                camera.connected 
                  ? 'bg-green-900/30 border border-green-500/30 text-green-400' 
                  : 'bg-red-900/30 border border-red-500/30 text-red-400'
              }`}>
                <div className="flex items-center gap-2">
                  {camera.connected ? (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      <span>Conectada • FPS: {camera.fps || 0}</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-4 h-4" />
                      <span>Sin conexión • Errores: {camera.errors || 0}</span>
                    </>
                  )}
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Formulario de agregar/editar */}
      <AnimatePresence>
        {isAddingCamera && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              className="bg-gray-900 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Camera className="w-5 h-5 text-blue-400" />
                {editingCamera ? 'Editar Cámara' : 'Nueva Cámara'}
              </h3>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* ID y Nombre */}
                  <div>
                    <label className="block text-sm font-medium mb-1">ID de Cámara</label>
                    <input
                      type="text"
                      value={formData.id}
                      onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
                      placeholder="cam_001"
                      required
                      disabled={editingCamera}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Nombre</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
                      placeholder="Entrada Principal"
                      required
                    />
                  </div>

                  {/* IP y Puerto */}
                  <div>
                    <label className="block text-sm font-medium mb-1">Dirección IP</label>
                    <input
                      type="text"
                      value={formData.ip}
                      onChange={(e) => setFormData({ ...formData, ip: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
                      placeholder="192.168.1.100"
                      pattern="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Puerto RTSP</label>
                    <input
                      type="number"
                      value={formData.rtsp_port}
                      onChange={(e) => setFormData({ ...formData, rtsp_port: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
                      placeholder="554"
                      required
                    />
                  </div>

                  {/* Usuario y Contraseña */}
                  <div>
                    <label className="block text-sm font-medium mb-1">Usuario</label>
                    <input
                      type="text"
                      value={formData.username}
                      onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
                      placeholder="admin"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Contraseña {editingCamera && <span className="text-xs text-gray-400">(dejar vacío para mantener actual)</span>}
                    </label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
                      placeholder="••••••••"
                      required={!editingCamera}
                    />
                  </div>

                  {/* Canal y Stream */}
                  <div>
                    <label className="block text-sm font-medium mb-1">Canal</label>
                    <input
                      type="number"
                      value={formData.channel}
                      onChange={(e) => setFormData({ ...formData, channel: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
                      min="1"
                      max="8"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Calidad Stream</label>
                    <select
                      value={formData.stream}
                      onChange={(e) => setFormData({ ...formData, stream: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
                    >
                      <option value="main">Principal (Alta calidad)</option>
                      <option value="sub">Secundario (Baja calidad)</option>
                    </select>
                  </div>

                  {/* Zona */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium mb-1">Zona Asignada</label>
                    <select
                      value={formData.zone_id}
                      onChange={(e) => setFormData({ ...formData, zone_id: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
                      required
                    >
                      <option value="">Seleccionar zona...</option>
                      {predefinedZones.map(zone => (
                        <option key={zone.id} value={zone.id}>
                          {zone.name} (Delay: {zone.delay}s)
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Habilitada */}
                  <div className="md:col-span-2">
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.enabled}
                        onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium">Cámara habilitada</span>
                    </label>
                  </div>
                </div>

                {/* URL RTSP Preview */}
                <div className="p-4 bg-gray-800/50 rounded-lg">
                  <p className="text-sm text-gray-400 mb-2">URL RTSP generada:</p>
                  <code className="text-xs text-blue-400 break-all">
                    rtsp://{formData.username}:****@{formData.ip}:{formData.rtsp_port}/Streaming/Channels/{formData.channel}0{formData.stream === 'main' ? '0' : '1'}
                  </code>
                </div>

                {/* Botones */}
                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={resetForm}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors flex items-center gap-2"
                  >
                    <X className="w-4 h-4" />
                    Cancelar
                  </button>
                  
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center gap-2"
                  >
                    <Save className="w-4 h-4" />
                    {editingCamera ? 'Guardar Cambios' : 'Agregar Cámara'}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Instrucciones */}
      {Object.keys(cameras).length === 0 && !showScanResults && (
        <div className="text-center py-12">
          <Camera className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No hay cámaras configuradas</h3>
          <p className="text-gray-400 mb-6">Comienza buscando cámaras en tu red o agregando una manualmente</p>
          
          <div className="max-w-2xl mx-auto bg-gray-800/50 rounded-lg p-6 text-left">
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <Settings className="w-5 h-5 text-blue-400" />
              Configuración típica para Hikvision
            </h4>
            <div className="space-y-2 text-sm text-gray-400">
              <p>• <strong>IP:</strong> Dirección IP de la cámara (ej: 192.168.1.100)</p>
              <p>• <strong>Puerto:</strong> 554 (puerto RTSP estándar)</p>
              <p>• <strong>Usuario:</strong> admin (usuario por defecto)</p>
              <p>• <strong>Canal:</strong> 1 para cámara principal, 2-8 para adicionales</p>
              <p>• <strong>Stream:</strong> main para alta calidad, sub para menor ancho de banda</p>
              <p>• <strong>Zona:</strong> Asigna cada cámara a una zona con su delay específico</p>
            </div>
            
            <div className="mt-4 p-3 bg-purple-900/20 border border-purple-500/30 rounded-lg">
              <p className="text-sm text-purple-400">
                💡 <strong>Tip:</strong> Usa el botón "Buscar Cámaras" para encontrar automáticamente 
                las cámaras Hikvision en tu red local.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}