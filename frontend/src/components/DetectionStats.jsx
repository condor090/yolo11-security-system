import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Lock, Unlock, TrendingUp, Clock } from 'lucide-react';

export default function DetectionStats({ detections = [], className = "" }) {
  const openGates = detections.filter(d => d.class_name === 'gate_open').length;
  const closedGates = detections.filter(d => d.class_name === 'gate_closed').length;
  const avgConfidence = detections.length > 0
    ? detections.reduce((acc, d) => acc + d.confidence, 0) / detections.length
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gray-800/50 backdrop-blur rounded-lg p-4 border border-gray-700/50 ${className}`}
    >
      <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
        <Shield className="w-4 h-4 text-blue-400" />
        Detecciones en Tiempo Real
      </h3>

      <div className="grid grid-cols-3 gap-3">
        {/* Puertas Abiertas */}
        <div className={`text-center p-3 rounded-lg ${
          openGates > 0 ? 'bg-red-900/30 border border-red-500/30' : 'bg-gray-700/30'
        }`}>
          <Unlock className={`w-6 h-6 mx-auto mb-1 ${
            openGates > 0 ? 'text-red-400' : 'text-gray-500'
          }`} />
          <div className="text-2xl font-bold">{openGates}</div>
          <div className="text-xs text-gray-400">Abiertas</div>
        </div>

        {/* Puertas Cerradas */}
        <div className="text-center p-3 rounded-lg bg-green-900/30 border border-green-500/30">
          <Lock className="w-6 h-6 mx-auto mb-1 text-green-400" />
          <div className="text-2xl font-bold text-green-400">{closedGates}</div>
          <div className="text-xs text-gray-400">Cerradas</div>
        </div>

        {/* Confianza Promedio */}
        <div className="text-center p-3 rounded-lg bg-blue-900/30 border border-blue-500/30">
          <TrendingUp className="w-6 h-6 mx-auto mb-1 text-blue-400" />
          <div className="text-2xl font-bold text-blue-400">
            {Math.round(avgConfidence * 100)}%
          </div>
          <div className="text-xs text-gray-400">Confianza</div>
        </div>
      </div>

      {/* Lista de detecciones */}
      {detections.length > 0 && (
        <div className="mt-4 space-y-2">
          <div className="text-xs text-gray-400 uppercase tracking-wide">
            Últimas Detecciones
          </div>
          {detections.slice(0, 3).map((det, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className={`flex items-center justify-between p-2 rounded ${
                det.class_name === 'gate_open'
                  ? 'bg-red-900/20 border border-red-500/30'
                  : 'bg-green-900/20 border border-green-500/30'
              }`}
            >
              <div className="flex items-center gap-2">
                {det.class_name === 'gate_open' ? (
                  <Unlock className="w-4 h-4 text-red-400" />
                ) : (
                  <Lock className="w-4 h-4 text-green-400" />
                )}
                <span className="text-sm">
                  {det.class_name.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              <span className="text-sm font-mono">
                {(det.confidence * 100).toFixed(1)}%
              </span>
            </motion.div>
          ))}
        </div>
      )}

      {detections.length === 0 && (
        <div className="mt-4 text-center text-gray-500 text-sm">
          <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
          Esperando detecciones...
        </div>
      )}
    </motion.div>
  );
}