import React, { useState, useEffect } from 'react';
import { 
  Send, MessageSquare, Save, RefreshCw, 
  Info, CheckCircle, AlertTriangle, Bell,
  Mail, Phone, Globe, Shield
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = 'http://localhost:8889';

export default function NotificationConfig() {
  const [config, setConfig] = useState({
    telegram: {
      enabled: false,
      bot_token: '',
      chat_id: '',
      send_alerts: true,
      send_images: true
    },
    email: {
      enabled: false,
      smtp_server: '',
      smtp_port: 587,
      username: '',
      password: '',
      recipients: []
    },
    webhook: {
      enabled: false,
      url: '',
      method: 'POST',
      headers: {}
    }
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isTestingTelegram, setIsTestingTelegram] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/config`);
      if (response.data.config) {
        setConfig(prev => ({
          ...prev,
          telegram: {
            enabled: false,
            bot_token: '',
            chat_id: '',
            send_alerts: true,
            send_images: true,
            ...response.data.config.telegram
          },
          email: response.data.config.email || prev.email,
          webhook: response.data.config.webhook || prev.webhook
        }));
      }
    } catch (error) {
      toast.error('Error cargando configuración de notificaciones');
    } finally {
      setIsLoading(false);
    }
  };

  const saveConfig = async () => {
    setIsSaving(true);
    try {
      // Solo enviar las configuraciones de notificaciones
      await axios.put(`${API_URL}/api/config`, {
        telegram: config.telegram,
        email: config.email,
        webhook: config.webhook
      });
      
      toast.success('Configuración de notificaciones guardada');
    } catch (error) {
      toast.error('Error guardando configuración');
    } finally {
      setIsSaving(false);
    }
  };

  const testTelegram = async () => {
    setIsTestingTelegram(true);
    try {
      await axios.post(`${API_URL}/api/telegram/test`, {
        bot_token: config.telegram.bot_token,
        chat_id: config.telegram.chat_id
      });
      toast.success('✅ Mensaje de prueba enviado a Telegram');
    } catch (error) {
      toast.error('❌ Error al enviar mensaje de prueba');
    } finally {
      setIsTestingTelegram(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Bell className="w-6 h-6 text-blue-400" />
          Configuración de Notificaciones
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

      {/* Telegram Configuration */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <Send className="w-5 h-5 text-blue-400" />
          Telegram
        </h3>

        <div className="space-y-4">
          {/* Enable Telegram */}
          <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg">
            <div className="flex items-center gap-3">
              <MessageSquare className="w-5 h-5 text-gray-400" />
              <div>
                <p className="font-medium">Notificaciones por Telegram</p>
                <p className="text-sm text-gray-400">Enviar alertas instantáneas a un grupo o chat</p>
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
                <label className="text-sm font-medium mb-2 block">Bot Token</label>
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
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-sm focus:border-blue-500 focus:outline-none font-mono"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Obtén el token desde @BotFather en Telegram
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
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-sm focus:border-blue-500 focus:outline-none font-mono"
                />
                <p className="text-xs text-gray-500 mt-2">
                  ID del grupo o chat donde enviar las alertas (incluye el - si es grupo)
                </p>
              </div>

              {/* Notification Options */}
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                  <div>
                    <label className="text-sm font-medium">Enviar alertas de texto</label>
                    <p className="text-xs text-gray-400 mt-1">Notificaciones instantáneas cuando se detecte una puerta abierta</p>
                  </div>
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
                  <div>
                    <label className="text-sm font-medium">Enviar imágenes con detecciones</label>
                    <p className="text-xs text-gray-400 mt-1">Incluir captura con bounding boxes en las alertas</p>
                  </div>
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

              {/* Test Button */}
              <button
                onClick={testTelegram}
                disabled={isTestingTelegram || !config.telegram.bot_token || !config.telegram.chat_id}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-4 py-2 rounded-lg transition-colors"
              >
                {isTestingTelegram ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Enviando...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Enviar Mensaje de Prueba
                  </>
                )}
              </button>

              {/* Help Section */}
              <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                <h4 className="font-medium text-blue-400 mb-2 flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  Cómo configurar Telegram
                </h4>
                <ol className="text-sm text-gray-300 space-y-2 list-decimal list-inside">
                  <li>Busca @BotFather en Telegram</li>
                  <li>Envía /newbot y sigue las instrucciones</li>
                  <li>Copia el token que te proporcione</li>
                  <li>Agrega el bot a tu grupo o canal</li>
                  <li>Obtén el Chat ID enviando un mensaje al bot @userinfobot</li>
                </ol>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Email Configuration (Future) */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50 opacity-50">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <Mail className="w-5 h-5 text-gray-400" />
          Email (Próximamente)
        </h3>
        
        <div className="text-center py-8 text-gray-500">
          <Mail className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>Las notificaciones por email estarán disponibles pronto</p>
        </div>
      </div>

      {/* Webhook Configuration (Future) */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50 opacity-50">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <Globe className="w-5 h-5 text-gray-400" />
          Webhook (Próximamente)
        </h3>
        
        <div className="text-center py-8 text-gray-500">
          <Globe className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>La integración con webhooks externos estará disponible pronto</p>
        </div>
      </div>

      {/* Status Overview */}
      <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5 text-blue-400" />
          Estado de las Notificaciones
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className={`p-4 rounded-lg border ${
            config.telegram.enabled 
              ? 'bg-green-900/20 border-green-500/30' 
              : 'bg-gray-700/30 border-gray-600/30'
          }`}>
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Telegram</span>
              <div className={`w-2 h-2 rounded-full ${
                config.telegram.enabled ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
              }`} />
            </div>
            <p className="text-sm text-gray-400">
              {config.telegram.enabled ? 'Configurado y activo' : 'No configurado'}
            </p>
          </div>
          
          <div className="p-4 rounded-lg border bg-gray-700/30 border-gray-600/30">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Email</span>
              <div className="w-2 h-2 rounded-full bg-gray-500" />
            </div>
            <p className="text-sm text-gray-400">
              Próximamente
            </p>
          </div>
          
          <div className="p-4 rounded-lg border bg-gray-700/30 border-gray-600/30">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Webhook</span>
              <div className="w-2 h-2 rounded-full bg-gray-500" />
            </div>
            <p className="text-sm text-gray-400">
              Próximamente
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}