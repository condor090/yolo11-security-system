import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertCircle, CheckCircle, Clock, Camera, Settings, Activity,
  Shield, Eye, Gauge, Bell, ChevronDown, Info, Play, Pause,
  RefreshCw, Download, Upload, Zap, TrendingUp, Lock, Unlock,
  Video, EyeOff
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import axios from 'axios';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import VideoContext from './components/VideoContext';
import CameraConfig from './components/CameraConfig';
import TimerConfig from './components/TimerConfig';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const API_URL = 'http://localhost:8889';
const WS_URL = 'ws://localhost:8889/ws';

function App() {
  // Estados principales
  const [activeTab, setActiveTab] = useState('dashboard');
  const [configTab, setConfigTab] = useState('cameras');
  const [timers, setTimers] = useState([]);
  const [alarmActive, setAlarmActive] = useState(false);
  const [detections, setDetections] = useState([]);
  const [stats, setStats] = useState({});
  const [config, setConfig] = useState({});
  const [uploadedImage, setUploadedImage] = useState(null);
  const [detectedImage, setDetectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Estados de configuración
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.65);
  const [analysisMode, setAnalysisMode] = useState('balanced');
  const [isMonitoring, setIsMonitoring] = useState(true);
  
  // Estados para video
  const [selectedTimer, setSelectedTimer] = useState(null);
  const [showDirectView, setShowDirectView] = useState(false);
  const [cameras, setCameras] = useState({});
  
  // Referencias
  const wsRef = useRef(null);
  const fileInputRef = useRef(null);

  // Modos de análisis
  const analysisModes = {
    balanced: { name: 'Balanceado', icon: '🎯', threshold: 0.65 },
    highSecurity: { name: 'Alta Seguridad', icon: '🛡️', threshold: 0.75 },
    highSensitivity: { name: 'Alta Sensibilidad', icon: '🔍', threshold: 0.50 }
  };

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        console.log('WebSocket conectado');
        toast.success('Sistema conectado', {
          icon: '🟢',
          style: {
            borderRadius: '10px',
            background: '#1f2937',
            color: '#fff',
          }
        });
      };
      
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('Error de conexión', {
          style: {
            borderRadius: '10px',
            background: '#991b1b',
            color: '#fff',
          }
        });
      };
      
      ws.onclose = () => {
        console.log('WebSocket desconectado');
        setTimeout(connectWebSocket, 3000);
      };
      
      wsRef.current = ws;
    };
    
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Manejar mensajes WebSocket
  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'timer_update':
        setTimers(message.data.timers);
        setAlarmActive(message.data.alarm_active);
        break;
      case 'detection':
        setDetections(message.data.detections);
        if (message.data.detections.some(d => d.class_name === 'gate_open')) {
          toast('🚪 Puerta abierta detectada', {
            duration: 4000,
            style: {
              borderRadius: '10px',
              background: '#dc2626',
              color: '#fff',
            }
          });
        }
        break;
      default:
        console.log('Mensaje no manejado:', message);
    }
  };

  // Cargar configuración inicial
  useEffect(() => {
    loadConfig();
    loadStats();
    loadCameras();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/config`);
      setConfig(response.data.config);
    } catch (error) {
      console.error('Error cargando config:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/statistics`);
      setStats(response.data.statistics);
    } catch (error) {
      console.error('Error cargando stats:', error);
    }
  };

  const loadCameras = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/cameras`);
      setCameras(response.data.cameras);
    } catch (error) {
      console.error('Error cargando cámaras:', error);
    }
  };

  // Cambiar modo de análisis
  const handleAnalysisModeChange = (mode) => {
    setAnalysisMode(mode);
    setConfidenceThreshold(analysisModes[mode].threshold);
  };

  // Subir imagen para análisis
  const handleImageUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Mostrar imagen original mientras se procesa
    const reader = new FileReader();
    reader.onloadend = () => {
      setUploadedImage(reader.result);
    };
    reader.readAsDataURL(file);
    
    setIsAnalyzing(true);
    
    try {
      const response = await axios.post(`${API_URL}/api/detect`, formData, {
        params: { confidence: confidenceThreshold }
      });
      if (response.data.success) {
        setDetectedImage(response.data.image);
        setDetections(response.data.detections);
        toast.success('Análisis completado', {
          icon: '✅',
          style: {
            borderRadius: '10px',
            background: '#065f46',
            color: '#fff',
          }
        });
      }
    } catch (error) {
      toast.error('Error en el análisis');
      console.error(error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Detener todas las alarmas
  const stopAllAlarms = async () => {
    try {
      await axios.post(`${API_URL}/api/alarms/stop-all`);
      toast.success('Alarmas detenidas');
    } catch (error) {
      toast.error('Error deteniendo alarmas');
    }
  };

  // Reconocer alarma específica
  const acknowledgeAlarm = async (doorId) => {
    try {
      await axios.post(`${API_URL}/api/timers/acknowledge/${doorId}`);
    } catch (error) {
      toast.error('Error reconociendo alarma');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <Toaster position="top-right" />
      
      {/* Header Profesional */}
      <header className="bg-black/50 backdrop-blur-lg border-b border-gray-700/50 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <Shield className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h1 className="text-xl font-bold">YOLO11 Security System</h1>
                  <p className="text-xs text-gray-400">Sistema Profesional de Seguridad</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              {/* Estado del Sistema */}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-1 bg-gray-800 rounded-full">
                  <div className={`w-2 h-2 rounded-full ${alarmActive ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`} />
                  <span className="text-sm">{alarmActive ? 'Alarma Activa' : 'Sistema Normal'}</span>
                </div>
                
                {/* Monitor Toggle */}
                <button
                  onClick={() => setIsMonitoring(!isMonitoring)}
                  className={`p-2 rounded-lg transition-all ${
                    isMonitoring 
                      ? 'bg-green-500/20 text-green-400' 
                      : 'bg-gray-700 text-gray-400'
                  }`}
                >
                  {isMonitoring ? <Eye className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              
              {/* Info del Sistema */}
              <div className="text-sm text-gray-400">
                <span>v3.0.0</span>
                <span className="mx-2">•</span>
                <span>Modelo: 99.39% mAP50</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Mejorada */}
      <nav className="bg-gray-800/50 backdrop-blur border-b border-gray-700/50">
        <div className="container mx-auto px-4">
          <div className="flex space-x-1">
            {[
              { id: 'dashboard', name: 'Dashboard', icon: Gauge },
              { id: 'monitor', name: 'Monitor', icon: Activity },
              { id: 'analyze', name: 'Análisis', icon: Camera },
              { id: 'config', name: 'Configuración', icon: Settings },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 transition-all ${
                  activeTab === tab.id
                    ? 'bg-blue-500/20 text-blue-400 border-b-2 border-blue-400'
                    : 'hover:bg-gray-700/50 text-gray-400'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.name}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* KPIs Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-br from-blue-600/20 to-blue-700/20 p-6 rounded-xl border border-blue-500/30"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-blue-400 text-sm font-medium">Detecciones 24h</p>
                    <p className="text-3xl font-bold mt-2">{stats.total_alerts || 0}</p>
                    <p className="text-xs text-gray-400 mt-1">+12% vs ayer</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-blue-400 opacity-50" />
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-gradient-to-br from-green-600/20 to-green-700/20 p-6 rounded-xl border border-green-500/30"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-green-400 text-sm font-medium">Estado Actual</p>
                    <p className="text-3xl font-bold mt-2">{timers.length}</p>
                    <p className="text-xs text-gray-400 mt-1">Puertas abiertas</p>
                  </div>
                  <Lock className="w-8 h-8 text-green-400 opacity-50" />
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-gradient-to-br from-purple-600/20 to-purple-700/20 p-6 rounded-xl border border-purple-500/30"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-purple-400 text-sm font-medium">Precisión</p>
                    <p className="text-3xl font-bold mt-2">
                      {((stats.average_confidence || 0.85) * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-gray-400 mt-1">Promedio del día</p>
                  </div>
                  <Zap className="w-8 h-8 text-purple-400 opacity-50" />
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className={`bg-gradient-to-br p-6 rounded-xl border ${
                  alarmActive 
                    ? 'from-red-600/20 to-red-700/20 border-red-500/30' 
                    : 'from-gray-600/20 to-gray-700/20 border-gray-500/30'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className={`text-sm font-medium ${alarmActive ? 'text-red-400' : 'text-gray-400'}`}>
                      Alertas Activas
                    </p>
                    <p className="text-3xl font-bold mt-2">
                      {timers.filter(t => t.alarm_triggered).length}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {alarmActive ? 'Requiere atención' : 'Todo normal'}
                    </p>
                  </div>
                  <Bell className={`w-8 h-8 opacity-50 ${alarmActive ? 'text-red-400' : 'text-gray-400'}`} />
                </div>
              </motion.div>
            </div>

            {/* Gráficos */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Actividad por Hora */}
              <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-400" />
                  Actividad por Hora
                </h3>
                <div className="h-64">
                  <Line
                    data={{
                      labels: Array.from({length: 24}, (_, i) => `${i}:00`),
                      datasets: [{
                        label: 'Detecciones',
                        data: Array.from({length: 24}, () => Math.floor(Math.random() * 10)),
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                      }]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { display: false },
                      },
                      scales: {
                        x: { 
                          grid: { color: 'rgba(255, 255, 255, 0.1)' },
                          ticks: { color: 'rgba(255, 255, 255, 0.5)' }
                        },
                        y: { 
                          grid: { color: 'rgba(255, 255, 255, 0.1)' },
                          ticks: { color: 'rgba(255, 255, 255, 0.5)' }
                        }
                      }
                    }}
                  />
                </div>
              </div>

              {/* Distribución de Alertas */}
              <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-blue-400" />
                  Distribución de Alertas
                </h3>
                <div className="h-64 flex items-center justify-center">
                  <Doughnut
                    data={{
                      labels: ['Puertas Abiertas', 'Falsas Alarmas', 'Resueltas'],
                      datasets: [{
                        data: [30, 10, 60],
                        backgroundColor: [
                          'rgba(239, 68, 68, 0.8)',
                          'rgba(245, 158, 11, 0.8)',
                          'rgba(34, 197, 94, 0.8)',
                        ],
                        borderColor: [
                          'rgba(239, 68, 68, 1)',
                          'rgba(245, 158, 11, 1)',
                          'rgba(34, 197, 94, 1)',
                        ],
                        borderWidth: 2,
                      }]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'right',
                          labels: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            padding: 20,
                          }
                        }
                      }
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Eventos Recientes */}
            <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-400" />
                Eventos Recientes
              </h3>
              <div className="space-y-3">
                {[
                  { time: '12:45', event: 'Puerta principal abierta', type: 'warning' },
                  { time: '12:30', event: 'Alarma reconocida - Zona 2', type: 'info' },
                  { time: '11:55', event: 'Sistema reiniciado', type: 'success' },
                  { time: '11:20', event: 'Detección múltiple en entrada', type: 'error' },
                ].map((event, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-400">{event.time}</span>
                      <span className="text-sm">{event.event}</span>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      event.type === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                      event.type === 'error' ? 'bg-red-500/20 text-red-400' :
                      event.type === 'success' ? 'bg-green-500/20 text-green-400' :
                      'bg-blue-500/20 text-blue-400'
                    }`}>
                      {event.type}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Monitor Tab */}
        {activeTab === 'monitor' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Activity className="w-6 h-6 text-blue-400" />
                Monitor en Tiempo Real
              </h2>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowDirectView(!showDirectView)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                    showDirectView 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {showDirectView ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  {showDirectView ? 'Ocultar Vista Directa' : 'Vista Directa'}
                </button>
                
                <button
                  onClick={() => setIsMonitoring(!isMonitoring)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                    isMonitoring 
                      ? 'bg-green-500 text-white' 
                      : 'bg-gray-700 text-gray-300'
                  }`}
                >
                  {isMonitoring ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  {isMonitoring ? 'Pausar' : 'Reanudar'}
                </button>
                
                <button
                  onClick={stopAllAlarms}
                  className="flex items-center gap-2 bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition-colors"
                >
                  <Bell className="w-4 h-4" />
                  Detener Alarmas
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <AnimatePresence>
                {timers.map((timer) => (
                  <motion.div
                    key={timer.door_id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className={`relative overflow-hidden rounded-xl border ${
                      timer.alarm_triggered
                        ? 'bg-red-900/30 border-red-500/50 animate-pulse'
                        : 'bg-gray-800/50 border-gray-700/50'
                    } backdrop-blur`}
                  >
                    {/* Header */}
                    <div className="p-4 border-b border-gray-700/50">
                      <div className="flex justify-between items-center">
                        <h3 className="font-semibold flex items-center gap-2">
                          {timer.alarm_triggered ? (
                            <Unlock className="w-4 h-4 text-red-400" />
                          ) : (
                            <Lock className="w-4 h-4 text-green-400" />
                          )}
                          {timer.door_id}
                        </h3>
                        <span className="text-xs text-gray-400">
                          Cámara: {timer.camera_id}
                        </span>
                      </div>
                    </div>
                    
                    {/* Body */}
                    <div className="p-4 space-y-3">
                      {/* Tiempo */}
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Tiempo abierto:</span>
                        <span className="font-mono font-semibold">
                          {Math.floor(timer.time_elapsed / 60)}:{String(Math.floor(timer.time_elapsed % 60)).padStart(2, '0')}
                        </span>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs text-gray-400">
                          <span>Progreso</span>
                          <span>{Math.round(timer.progress_percent)}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                          <motion.div
                            className={`h-full rounded-full ${
                              timer.alarm_triggered 
                                ? 'bg-gradient-to-r from-red-500 to-red-600' 
                                : 'bg-gradient-to-r from-blue-500 to-blue-600'
                            }`}
                            initial={{ width: 0 }}
                            animate={{ width: `${Math.min(timer.progress_percent, 100)}%` }}
                            transition={{ duration: 0.5 }}
                          />
                        </div>
                      </div>
                      
                      {/* Estado */}
                      <div className={`text-center py-2 rounded-lg ${
                        timer.alarm_triggered 
                          ? 'bg-red-500/20 text-red-400' 
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {timer.alarm_triggered ? (
                          <span className="flex items-center justify-center gap-2">
                            <AlertCircle className="w-4 h-4" />
                            ALARMA ACTIVA
                          </span>
                        ) : (
                          <span>Alarma en: {Math.floor(timer.time_remaining)}s</span>
                        )}
                      </div>
                      
                      {/* Acciones */}
                      <div className="space-y-2">
                        {timer.has_camera && (
                          <button
                            onClick={() => setSelectedTimer(timer)}
                            className="w-full bg-gray-700 hover:bg-gray-600 py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
                          >
                            <Video className="w-4 h-4" />
                            Ver Video Contextual
                          </button>
                        )}
                        
                        {timer.alarm_triggered && (
                          <button
                            onClick={() => acknowledgeAlarm(timer.door_id)}
                            className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
                          >
                            <CheckCircle className="w-4 h-4" />
                            Reconocer
                          </button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {timers.length === 0 && !showDirectView && (
                <div className="col-span-full text-center py-16">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-full mb-4">
                    <CheckCircle className="w-8 h-8 text-green-400" />
                  </div>
                  <p className="text-xl font-semibold mb-2">Sistema Seguro</p>
                  <p className="text-gray-400">No hay puertas abiertas detectadas</p>
                </div>
              )}
            </div>

            {/* Video Context Modal para timer seleccionado */}
            {selectedTimer && (
              <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div className="max-w-4xl w-full">
                  <VideoContext 
                    timer={selectedTimer} 
                    onClose={() => setSelectedTimer(null)} 
                  />
                </div>
              </div>
            )}

            {/* Vista Directa - Grid de Cámaras */}
            {showDirectView && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6"
              >
                <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Video className="w-5 h-5 text-blue-400" />
                    Vista Directa - Todas las Cámaras
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(cameras).map(([camId, camera]) => (
                      <div 
                        key={camId}
                        className="bg-gray-900 rounded-lg overflow-hidden border border-gray-700 hover:border-blue-500/50 transition-all cursor-pointer"
                        onClick={() => {
                          // TODO: Abrir cámara en fullscreen
                          toast.info(`Cámara ${camera.name} - Fullscreen no implementado aún`);
                        }}
                      >
                        <div className="p-3 bg-gray-800 border-b border-gray-700">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-sm">{camera.name}</span>
                            <div className="flex items-center gap-2">
                              {camera.connected ? (
                                <div className="flex items-center gap-1">
                                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                  <span className="text-xs text-green-400">EN VIVO</span>
                                </div>
                              ) : (
                                <div className="flex items-center gap-1">
                                  <div className="w-2 h-2 bg-red-500 rounded-full" />
                                  <span className="text-xs text-red-400">OFFLINE</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div className="relative aspect-video bg-black">
                          {camera.connected ? (
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="text-center">
                                <Camera className="w-12 h-12 text-gray-600 mb-2" />
                                <p className="text-sm text-gray-500">Stream no implementado</p>
                                <p className="text-xs text-gray-600 mt-1">FPS: {camera.fps || 0}</p>
                              </div>
                            </div>
                          ) : (
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="text-center">
                                <AlertCircle className="w-8 h-8 text-red-500 mb-2" />
                                <p className="text-sm text-red-400">Sin conexión</p>
                              </div>
                            </div>
                          )}
                        </div>
                        
                        <div className="p-3 bg-gray-800 border-t border-gray-700">
                          <div className="flex items-center justify-between text-xs text-gray-400">
                            <span>ID: {camId}</span>
                            <span>Errores: {camera.errors || 0}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {Object.keys(cameras).length === 0 && (
                    <div className="text-center py-8">
                      <Camera className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                      <p className="text-gray-400">No hay cámaras configuradas</p>
                      <p className="text-sm text-gray-500 mt-2">
                        Configure cámaras en el archivo camera_config.json
                      </p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        )}

        {/* Analyze Tab */}
        {activeTab === 'analyze' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Panel de Control Izquierdo */}
            <div className="lg:col-span-1 space-y-4">
              {/* Niveles de Confianza */}
              <div className="bg-gray-800/50 backdrop-blur rounded-xl p-4 border border-gray-700/50">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <Gauge className="w-5 h-5 text-blue-400" />
                  Niveles de Confianza
                </h3>
                
                <div className="space-y-3">
                  {[
                    { level: '> 75%', label: 'Alta confianza', color: 'bg-green-500' },
                    { level: '65-75%', label: 'Confianza media', color: 'bg-yellow-500' },
                    { level: '50-65%', label: 'Baja confianza', color: 'bg-red-500' },
                    { level: '< 50%', label: 'No detectado', color: 'bg-gray-600' },
                  ].map((item) => (
                    <div key={item.level} className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded-full ${item.color}`} />
                      <div className="text-sm">
                        <span className="font-medium">{item.level}:</span>
                        <span className="text-gray-400 ml-1">{item.label}</span>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Slider de Umbral */}
                <div className="mt-6">
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium">Umbral de Confianza</label>
                    <span className="text-sm text-blue-400 font-semibold">
                      {Math.round(confidenceThreshold * 100)}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={confidenceThreshold * 100}
                    onChange={(e) => setConfidenceThreshold(e.target.value / 100)}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0.10</span>
                    <span>1.00</span>
                  </div>
                </div>
              </div>

              {/* Modo de Análisis */}
              <div className="bg-gray-800/50 backdrop-blur rounded-xl p-4 border border-gray-700/50">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <Settings className="w-5 h-5 text-blue-400" />
                  Modo de Análisis
                </h3>
                
                <div className="space-y-2">
                  {Object.entries(analysisModes).map(([key, mode]) => (
                    <button
                      key={key}
                      onClick={() => handleAnalysisModeChange(key)}
                      className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all ${
                        analysisMode === key
                          ? 'bg-blue-500/20 border border-blue-500/50'
                          : 'bg-gray-700/30 border border-transparent hover:bg-gray-700/50'
                      }`}
                    >
                      <span className="text-xl">{mode.icon}</span>
                      <div className="text-left">
                        <div className="font-medium">{mode.name}</div>
                        <div className="text-xs text-gray-400">
                          Umbral: {Math.round(mode.threshold * 100)}%
                        </div>
                      </div>
                      {analysisMode === key && (
                        <CheckCircle className="w-4 h-4 text-blue-400 ml-auto" />
                      )}
                    </button>
                  ))}
                </div>
                
                <div className="mt-4 p-3 bg-blue-500/10 rounded-lg border border-blue-500/30">
                  <p className="text-sm text-blue-400">
                    <Info className="w-4 h-4 inline mr-1" />
                    Umbral actual: {Math.round(confidenceThreshold * 100)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Área Principal de Análisis */}
            <div className="lg:col-span-3 space-y-6">
              {!uploadedImage && (
                <div
                  className="border-2 border-dashed border-gray-600 rounded-xl p-16 text-center cursor-pointer hover:border-blue-500/50 hover:bg-blue-500/5 transition-all"
                  onClick={() => fileInputRef.current?.click()}
                  onDrop={(e) => {
                    e.preventDefault();
                    const file = e.dataTransfer.files[0];
                    if (file) handleImageUpload(file);
                  }}
                  onDragOver={(e) => e.preventDefault()}
                >
                  <Camera className="w-20 h-20 mx-auto mb-4 text-gray-500" />
                  <h3 className="text-xl font-semibold mb-2">Cargar Imagen para Análisis</h3>
                  <p className="text-gray-400 mb-4">
                    Arrastra una imagen aquí o haz clic para seleccionar
                  </p>
                  <p className="text-sm text-gray-500">
                    Formatos soportados: JPG, PNG, BMP • Tamaño máximo: 10MB
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleImageUpload(file);
                    }}
                  />
                </div>
              )}

              {uploadedImage && (
                <>
                  {/* Imágenes lado a lado */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="bg-gray-800/50 backdrop-blur rounded-xl p-4 border border-gray-700/50">
                      <h3 className="text-lg font-semibold mb-4 text-center">Imagen Original</h3>
                      <img 
                        src={uploadedImage} 
                        alt="Original" 
                        className="w-full rounded-lg"
                      />
                    </div>

                    <div className="bg-gray-800/50 backdrop-blur rounded-xl p-4 border border-gray-700/50">
                      <h3 className="text-lg font-semibold mb-4 text-center">Análisis de Detecciones</h3>
                      {isAnalyzing ? (
                        <div className="flex items-center justify-center h-64">
                          <div className="relative">
                            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <Shield className="w-6 h-6 text-blue-500" />
                            </div>
                          </div>
                        </div>
                      ) : detectedImage ? (
                        <img 
                          src={detectedImage} 
                          alt="Detecciones" 
                          className="w-full rounded-lg"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-64 text-gray-500">
                          Esperando análisis...
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Resultados del Análisis */}
                  {detections.length > 0 && !isAnalyzing && (
                    <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
                      <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                        <Activity className="w-6 h-6 text-blue-400" />
                        Resultados del Análisis
                      </h3>
                      
                      {/* Métricas */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <div className="text-center p-4 bg-gray-700/30 rounded-lg">
                          <div className="text-3xl font-bold text-red-400">
                            {detections.filter(d => d.class_name === 'gate_open').length}
                          </div>
                          <div className="text-sm text-gray-400 mt-1">Puertas Abiertas</div>
                        </div>
                        <div className="text-center p-4 bg-gray-700/30 rounded-lg">
                          <div className="text-3xl font-bold text-green-400">
                            {detections.filter(d => d.class_name === 'gate_closed').length}
                          </div>
                          <div className="text-sm text-gray-400 mt-1">Puertas Cerradas</div>
                        </div>
                        <div className="text-center p-4 bg-gray-700/30 rounded-lg">
                          <div className="text-3xl font-bold text-blue-400">
                            {detections.length}
                          </div>
                          <div className="text-sm text-gray-400 mt-1">Total Detecciones</div>
                        </div>
                        <div className="text-center p-4 bg-gray-700/30 rounded-lg">
                          <div className="text-3xl font-bold text-purple-400">
                            {detections.length > 0 
                              ? Math.round(detections.reduce((acc, d) => acc + d.confidence, 0) / detections.length * 100)
                              : 0}%
                          </div>
                          <div className="text-sm text-gray-400 mt-1">Confianza Promedio</div>
                        </div>
                      </div>

                      {/* Estado de Seguridad */}
                      {detections.some(d => d.class_name === 'gate_open') ? (
                        <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 mb-6">
                          <div className="flex items-start gap-3">
                            <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                              <h4 className="font-semibold text-red-400">ALERTA DE SEGURIDAD</h4>
                              <p className="text-sm mt-1">
                                Se detectaron {detections.filter(d => d.class_name === 'gate_open').length} puerta(s) 
                                abierta(s) en la imagen analizada.
                              </p>
                              <p className="text-sm text-gray-400 mt-2">
                                Tiempo de análisis: {new Date().toLocaleTimeString()} • 
                                Modo: {analysisModes[analysisMode].name}
                              </p>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-green-900/30 border border-green-500/50 rounded-lg p-4 mb-6">
                          <div className="flex items-start gap-3">
                            <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                              <h4 className="font-semibold text-green-400">ESTADO SEGURO</h4>
                              <p className="text-sm mt-1">
                                Todas las puertas detectadas están cerradas.
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Tabla de Detecciones */}
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-gray-700">
                              <th className="text-left p-3 text-sm font-medium text-gray-400">ID</th>
                              <th className="text-left p-3 text-sm font-medium text-gray-400">Tipo</th>
                              <th className="text-left p-3 text-sm font-medium text-gray-400">Confianza</th>
                              <th className="text-left p-3 text-sm font-medium text-gray-400">Posición</th>
                              <th className="text-left p-3 text-sm font-medium text-gray-400">Estado</th>
                            </tr>
                          </thead>
                          <tbody>
                            {detections.map((det, idx) => (
                              <tr key={idx} className="border-b border-gray-700/50 hover:bg-gray-700/20">
                                <td className="p-3 text-sm">#{idx + 1}</td>
                                <td className="p-3">
                                  <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${
                                    det.class_name === 'gate_open' 
                                      ? 'bg-red-500/20 text-red-400' 
                                      : 'bg-green-500/20 text-green-400'
                                  }`}>
                                    {det.class_name === 'gate_open' ? (
                                      <Unlock className="w-3 h-3" />
                                    ) : (
                                      <Lock className="w-3 h-3" />
                                    )}
                                    {det.class_name.replace('_', ' ').toUpperCase()}
                                  </span>
                                </td>
                                <td className="p-3">
                                  <div className="flex items-center gap-3">
                                    <div className="flex-1 bg-gray-700 rounded-full h-2 overflow-hidden">
                                      <div 
                                        className={`h-full transition-all ${
                                          det.confidence > 0.75 ? 'bg-green-500' :
                                          det.confidence > 0.65 ? 'bg-yellow-500' : 
                                          det.confidence > 0.5 ? 'bg-red-500' : 'bg-gray-500'
                                        }`}
                                        style={{ width: `${det.confidence * 100}%` }}
                                      />
                                    </div>
                                    <span className="text-sm font-mono">
                                      {(det.confidence * 100).toFixed(1)}%
                                    </span>
                                  </div>
                                </td>
                                <td className="p-3 text-sm text-gray-400 font-mono">
                                  ({det.bbox.x1}, {det.bbox.y1})
                                </td>
                                <td className="p-3">
                                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${
                                    det.confidence > confidenceThreshold
                                      ? 'bg-blue-500/20 text-blue-400'
                                      : 'bg-gray-600/20 text-gray-400'
                                  }`}>
                                    {det.confidence > confidenceThreshold ? 'Válido' : 'Descartado'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Acciones */}
                  <div className="flex gap-4">
                    <button
                      onClick={() => {
                        setUploadedImage(null);
                        setDetectedImage(null);
                        setDetections([]);
                      }}
                      className="flex-1 bg-gray-700 hover:bg-gray-600 py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      <RefreshCw className="w-5 h-5" />
                      Nueva Imagen
                    </button>
                    
                    {detectedImage && (
                      <button
                        onClick={() => {
                          const link = document.createElement('a');
                          link.href = detectedImage;
                          link.download = `analisis_${Date.now()}.jpg`;
                          link.click();
                        }}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
                      >
                        <Download className="w-5 h-5" />
                        Descargar Resultado
                      </button>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Config Tab */}
        {activeTab === 'config' && (
          <div className="max-w-6xl mx-auto space-y-6">
            {/* Tabs de configuración */}
            <div className="flex gap-4 border-b border-gray-700">
              <button
                onClick={() => setConfigTab('cameras')}
                className={`pb-3 px-1 transition-all ${
                  configTab === 'cameras'
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                Cámaras
              </button>
              <button
                onClick={() => setConfigTab('timers')}
                className={`pb-3 px-1 transition-all ${
                  configTab === 'timers'
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                Temporizadores
              </button>
              <button
                onClick={() => setConfigTab('notifications')}
                className={`pb-3 px-1 transition-all ${
                  configTab === 'notifications'
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                Notificaciones
              </button>
            </div>

            {/* Contenido de las tabs */}
            {configTab === 'cameras' && <CameraConfig />}
            
            {configTab === 'timers' && <TimerConfig />}
            
            {configTab === 'notifications' && (
              <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
                <h3 className="text-lg font-semibold mb-4">Notificaciones</h3>
                <div className="space-y-4">
                  {[
                    { name: 'Alertas Sonoras', enabled: true },
                    { name: 'Notificaciones Push', enabled: false },
                    { name: 'Email', enabled: false },
                    { name: 'Telegram', enabled: true },
                  ].map((item) => (
                    <div key={item.name} className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                      <span className="font-medium">{item.name}</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" defaultChecked={item.enabled} className="sr-only peer" />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-gray-800 py-6">
        <div className="container mx-auto px-4 text-center text-sm text-gray-500">
          <p>YOLO11 Security System v3.0.0 • Modelo: 99.39% mAP50 • © 2025</p>
        </div>
      </footer>

      {/* Estilos personalizados para el slider */}
      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
        }
        
        .slider::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
          border: none;
        }
      `}</style>
    </div>
  );
}

export default App;