import React, { useState, useEffect } from 'react';
import { 
  Calendar, CheckCircle, Clock, Zap, Brain, MessageSquare, 
  Car, User, Bell, ChevronRight, Play, AlertCircle, Cpu, 
  Leaf, Video, Github, Cloud, Package, ArrowUp, ArrowDown, 
  TrendingUp, Shield, DollarSign, Lock, Unlock, Target,
  Rocket, Star, Award, Timer, Camera, Code, Server
} from 'lucide-react';

const Roadmap = () => {
  const [activeHito, setActiveHito] = useState(null);
  const [timeToNext, setTimeToNext] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 });
  const [savingsCounter, setSavingsCounter] = useState(24500);
  const [detectionCount, setDetectionCount] = useState(32847);
  const [progress, setProgress] = useState(25); // Progreso general del proyecto

  // Calcular tiempo hasta el próximo sábado con segundos
  useEffect(() => {
    const calculateTimeToSaturday = () => {
      const now = new Date();
      const nextSaturday = new Date();
      const daysUntilSaturday = (6 - now.getDay() + 7) % 7 || 7;
      nextSaturday.setDate(now.getDate() + daysUntilSaturday);
      nextSaturday.setHours(10, 0, 0, 0);

      const diff = nextSaturday - now;
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setTimeToNext({ days, hours, minutes, seconds });
    };

    calculateTimeToSaturday();
    const interval = setInterval(calculateTimeToSaturday, 1000); // Actualizar cada segundo
    return () => clearInterval(interval);
  }, []);

  // Animación de contadores - DESACTIVADO temporalmente para evitar parpadeo
  /*
  useEffect(() => {
    const interval = setInterval(() => {
      setSavingsCounter(prev => prev + Math.floor(Math.random() * 100));
      setDetectionCount(prev => prev + Math.floor(Math.random() * 10));
    }, 3000);
    return () => clearInterval(interval);
  }, []);
  */

  const hitos = [
    {
      id: 'fundacion',
      fecha: '25 Mayo 2025',
      titulo: 'Fundación YOMJAI',
      subtitulo: 'Creado por Virgilio IA',
      estado: 'completado',
      icon: Brain,
      color: 'emerald',
      progreso: 100,
      metricas: {
        codigo: '15,882 líneas',
        precision: '99.39%',
        tiempo: '6 semanas'
      },
      descripcion: 'Sistema completo desarrollado por IA, incluyendo modelo YOLO11 entrenado con 32,847 imágenes mexicanas.',
      logros: [
        'Modelo YOLO11 con 99.39% precisión',
        'Sistema de alertas inteligente',
        'Modo Eco revolucionario',
        'Video contextual automático'
      ]
    },
    {
      id: 'instalacion',
      fecha: '1 Junio 2025',
      titulo: 'Primera Instalación Real',
      subtitulo: 'Sitio activo 24/7',
      estado: 'proximo',
      icon: Camera,
      color: 'blue',
      progreso: 0,
      metricas: {
        camaras: '1 cámara',
        alertas: 'Telegram + Sonora',
        uptime: '99.9% objetivo'
      },
      descripcion: 'Instalación en sitio real con monitoreo de puerta principal, alertas en tiempo real.',
      objetivos: [
        'Monitoreo puerta principal',
        'Alertas Telegram instantáneas',
        'Alarma sonora local',
        'Dashboard remoto activo'
      ]
    },
    {
      id: 'multideteccion',
      fecha: '8 Junio 2025',
      titulo: 'Detección Multi-Clase',
      subtitulo: 'Personas + Vehículos',
      estado: 'futuro',
      icon: User,
      color: 'purple',
      progreso: 0,
      metricas: {
        clases: '3 tipos',
        precision: '>95%',
        fps: '30 real-time'
      },
      descripcion: 'Expansión a detección simultánea de personas y vehículos con conteo inteligente.',
      objetivos: [
        'Detección de personas',
        'Reconocimiento de vehículos',
        'Conteo automático',
        'Alertas diferenciadas'
      ]
    },
    {
      id: 'chatia',
      fecha: '15 Junio 2025',
      titulo: 'Chat IA Inteligente',
      subtitulo: 'Asistente via Telegram',
      estado: 'futuro',
      icon: MessageSquare,
      color: 'indigo',
      progreso: 0,
      metricas: {
        comandos: '20+',
        respuesta: '<2s',
        idiomas: 'ES/EN'
      },
      descripcion: 'Interfaz conversacional para consultas y control del sistema via Telegram.',
      objetivos: [
        'Consultas en lenguaje natural',
        'Reportes bajo demanda',
        'Control remoto completo',
        'Respuestas con contexto visual'
      ]
    },
    {
      id: 'cierre',
      fecha: '30 Junio 2025',
      titulo: 'Lanzamiento Comercial',
      subtitulo: 'YOMJAI v1.0 Final',
      estado: 'futuro',
      icon: Rocket,
      color: 'red',
      progreso: 0,
      metricas: {
        clientes: '10 pilotos',
        mrr: '$10K USD',
        nps: '>90'
      },
      descripcion: 'Sistema completo listo para comercialización con todos los features probados.',
      objetivos: [
        'Documentación completa',
        'Certificaciones listas',
        'Equipo de soporte',
        'Pipeline de ventas activo'
      ]
    }
  ];

  const MetricCard = ({ icon: Icon, value, label, trend }) => (
    <div className="bg-gray-800/50 backdrop-blur rounded-xl p-4 border border-gray-700/50">
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5 text-blue-400" />
        {trend && (
          <span className={`text-xs flex items-center gap-1 ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend > 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      <div className="text-2xl font-bold mb-1">{value}</div>
      <div className="text-xs text-gray-400">{label}</div>
    </div>
  );

  const HitoCard = ({ hito }) => {
    const isActive = activeHito?.id === hito.id;
    const colorClasses = {
      emerald: 'from-emerald-600/20 to-emerald-700/20 border-emerald-500/30',
      blue: 'from-blue-600/20 to-blue-700/20 border-blue-500/30',
      purple: 'from-purple-600/20 to-purple-700/20 border-purple-500/30',
      indigo: 'from-indigo-600/20 to-indigo-700/20 border-indigo-500/30',
      red: 'from-red-600/20 to-red-700/20 border-red-500/30'
    };
    
    const iconColorClasses = {
      emerald: 'text-emerald-400',
      blue: 'text-blue-400',
      purple: 'text-purple-400',
      indigo: 'text-indigo-400',
      red: 'text-red-400'
    };
    
    const bgColorClasses = {
      emerald: 'bg-emerald-500/20',
      blue: 'bg-blue-500/20',
      purple: 'bg-purple-500/20',
      indigo: 'bg-indigo-500/20',
      red: 'bg-red-500/20'
    };
    
    const progressColorClasses = {
      emerald: 'from-emerald-500 to-emerald-600',
      blue: 'from-blue-500 to-blue-600',
      purple: 'from-purple-500 to-purple-600',
      indigo: 'from-indigo-500 to-indigo-600',
      red: 'from-red-500 to-red-600'
    };
    
    const ringColorClasses = {
      emerald: 'ring-emerald-500',
      blue: 'ring-blue-500',
      purple: 'ring-purple-500',
      indigo: 'ring-indigo-500',
      red: 'ring-red-500'
    };

    return (
      <div
        onClick={() => setActiveHito(isActive ? null : hito)}
        className={`relative cursor-pointer bg-gradient-to-br ${colorClasses[hito.color]} 
                   rounded-xl border transition-all duration-300 overflow-hidden hover:transform hover:scale-105
                   ${isActive ? `ring-2 ring-offset-2 ring-offset-gray-900 ${ringColorClasses[hito.color]}` : ''}`}
      >
        {/* Efecto de partículas para hitos completados - DESACTIVADO temporalmente */}
        {false && hito.estado === 'completado' && (
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-yellow-400 rounded-full opacity-60"
                initial={{ 
                  x: Math.random() * 100 + '%',
                  y: '100%'
                }}
                animate={{ 
                  y: '-10%',
                  opacity: [0, 0.6, 0]
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  delay: i * 1.3,
                  ease: "easeOut"
                }}
              />
            ))}
          </div>
        )}

        <div className="relative p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-lg ${bgColorClasses[hito.color]}`}>
                <hito.icon className={`w-6 h-6 ${iconColorClasses[hito.color]}`} />
              </div>
              <div>
                <h3 className="font-bold text-lg">{hito.titulo}</h3>
                <p className="text-sm text-gray-400">{hito.subtitulo}</p>
              </div>
            </div>
            <span className={`px-2 py-1 text-xs rounded-full ${
              hito.estado === 'completado' ? 'bg-green-500/20 text-green-400' :
              hito.estado === 'proximo' ? 'bg-blue-500/20 text-blue-400' :
              'bg-gray-600/20 text-gray-400'
            }`}>
              {hito.estado === 'completado' ? '✓ Completado' :
               hito.estado === 'proximo' ? '⏳ Próximo' : '📅 Programado'}
            </span>
          </div>

          {/* Fecha */}
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
            <Calendar className="w-4 h-4" />
            <span>{hito.fecha}</span>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>Progreso</span>
              <span>{hito.progreso}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full bg-gradient-to-r ${progressColorClasses[hito.color]} transition-all duration-1000 ease-out`}
                style={{ width: `${hito.progreso}%` }}
              />
            </div>
          </div>

          {/* Métricas */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            {Object.entries(hito.metricas).map(([key, value]) => (
              <div key={key} className="text-center p-2 bg-gray-800/50 rounded-lg">
                <div className="text-sm font-semibold">{value}</div>
                <div className="text-xs text-gray-500 capitalize">{key}</div>
              </div>
            ))}
          </div>

          {/* Descripción */}
          <p className="text-sm text-gray-300 mb-4">{hito.descripcion}</p>

          {/* Expandible Content */}
          {isActive && (
            <div className="overflow-hidden">
              <div className="pt-4 border-t border-gray-700">
                <h4 className="font-semibold mb-3 text-sm">
                  {hito.estado === 'completado' ? 'Logros Alcanzados:' : 'Objetivos:'}
                </h4>
                <ul className="space-y-2">
                  {(hito.logros || hito.objetivos || []).map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm">
                      <CheckCircle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                        hito.estado === 'completado' ? 'text-green-400' : 'text-gray-500'
                      }`} />
                      <span className="text-gray-300">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Indicador de click */}
        <div className="absolute bottom-2 right-2">
          <ChevronRight className={`w-4 h-4 text-gray-500 transition-transform ${
            isActive ? 'rotate-90' : ''
          }`} />
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl p-8 border border-gray-700/50">
        {/* Animated background - optimizado */}
        <div className="absolute inset-0 overflow-hidden opacity-10">
          <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl" />
          <div className="absolute top-0 -right-4 w-72 h-72 bg-yellow-500 rounded-full mix-blend-multiply filter blur-xl" />
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl" />
        </div>

        <div className="relative z-10">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Roadmap YOMJAI 2025
          </h1>
          <p className="text-xl text-gray-300 mb-6">
            De la Visión a la Revolución - Cada sábado, más cerca del futuro
          </p>
          
          {/* Contador para próximo hito */}
          <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50 inline-block">
            <p className="text-sm text-gray-400 mb-2">Próximo hito en:</p>
            <div className="flex gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">{timeToNext.days}</div>
                <div className="text-xs text-gray-500">días</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">{timeToNext.hours}</div>
                <div className="text-xs text-gray-500">horas</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">{timeToNext.minutes}</div>
                <div className="text-xs text-gray-500">minutos</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">{timeToNext.seconds}</div>
                <div className="text-xs text-gray-500">segundos</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Métricas Clave */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          icon={Brain}
          value="100%"
          label="Desarrollado por IA"
          trend={100}
        />
        <MetricCard
          icon={Camera}
          value={detectionCount.toLocaleString()}
          label="Imágenes de Entrenamiento"
          trend={12}
        />
        <MetricCard
          icon={DollarSign}
          value={`$${savingsCounter.toLocaleString()}`}
          label="Ahorro Proyectado"
          trend={67.5}
        />
        <MetricCard
          icon={TrendingUp}
          value={`${progress}%`}
          label="Progreso Total"
        />
      </div>

      {/* Timeline Principal */}
      <div className="relative">
        {/* Línea de tiempo */}
        <div className="absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-gradient-to-b from-blue-500/50 via-purple-500/50 to-red-500/50 rounded-full" />
        
        {/* Hitos */}
        <div className="space-y-8">
          {hitos.map((hito, index) => (
            <div
              key={hito.id}
              className={`flex items-center gap-8 ${
                index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'
              }`}
            >
              {/* Card */}
              <div className="flex-1">
                <HitoCard hito={hito} />
              </div>
              
              {/* Punto en la línea */}
              <div className="relative">
                <div className={`w-6 h-6 rounded-full border-4 ${
                  hito.estado === 'completado' ? 'bg-green-500 border-green-400' :
                  hito.estado === 'proximo' ? 'bg-blue-500 border-blue-400' :
                  'bg-gray-600 border-gray-500'
                }`} />
              </div>
              
              {/* Espaciador */}
              <div className="flex-1" />
            </div>
          ))}
        </div>
      </div>

      {/* Sección de Impacto */}
      <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-xl p-8 border border-blue-500/30">
        <h2 className="text-2xl font-bold mb-6 text-center">
          Impacto Proyectado al Completar el Roadmap
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-4xl font-bold text-blue-400 mb-2">$5M</div>
            <div className="text-gray-400">Valoración Empresa</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-purple-400 mb-2">1,000+</div>
            <div className="text-gray-400">Clientes Potenciales</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-green-400 mb-2">$120K</div>
            <div className="text-gray-400">MRR Proyectado</div>
          </div>
        </div>
      </div>

      {/* CTA Final */}
      <div className="text-center">
        <button
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 
                     px-8 py-4 rounded-xl font-semibold text-lg inline-flex items-center gap-3
                     shadow-lg shadow-blue-500/25 transition-all hover:transform hover:scale-105"
        >
          <Rocket className="w-6 h-6" />
          Únete a la Revolución YOMJAI
        </button>
      </div>
    </div>
  );
};

export default Roadmap;