#!/usr/bin/env python3
"""
Dashboard de Seguridad V2 - Con Sistema de Temporizadores
Integra el nuevo AlertManager con temporizadores configurables
"""

import streamlit as st
import cv2
import numpy as np
import time
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from ultralytics import YOLO
from PIL import Image
import sys
import asyncio
import pygame

# Añadir ruta para importar AlertManager V2
sys.path.append(str(Path(__file__).parent.parent.parent))
from alerts.alert_manager_v2 import AlertManager, DoorTimer

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Seguridad YOLO11 - V2",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
<style>
    .timer-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .timer-progress {
        background-color: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 10px 0;
    }
    .timer-fill {
        background-color: #ffd700;
        height: 100%;
        transition: width 0.5s ease;
    }
    .alarm-active {
        animation: pulse 1s infinite;
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-card {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4444;
    }
    .success-card {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #44ff44;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_security_detector():
    """Cargar detector de seguridad (cached)"""
    try:
        model_path = Path(__file__).parent.parent.parent / 'runs' / 'gates' / 'gate_detector_v1' / 'weights' / 'best.pt'
        
        if not model_path.exists():
            st.error(f"Modelo no encontrado en: {model_path}")
            return None
            
        model = YOLO(str(model_path))
        return model
    except Exception as e:
        st.error(f"Error cargando detector: {e}")
        return None

@st.cache_resource
def load_alert_manager_v2():
    """Cargar el gestor de alertas V2 con temporizadores"""
    try:
        config_path = Path(__file__).parent.parent.parent / 'alerts' / 'alert_config_v2.json'
        return AlertManager(str(config_path))
    except Exception as e:
        st.error(f"Error cargando gestor de alertas V2: {e}")
        return None

def display_timer_card(timer_info: dict):
    """Mostrar tarjeta de temporizador activo"""
    door_id = timer_info['door_id']
    time_elapsed = timer_info['time_elapsed']
    time_remaining = timer_info['time_remaining']
    delay_seconds = timer_info['delay_seconds']
    progress_percent = timer_info['progress_percent']
    alarm_triggered = timer_info['alarm_triggered']
    
    # Clase CSS según estado
    card_class = "timer-card alarm-active" if alarm_triggered else "timer-card"
    
    # Formato de tiempo
    elapsed_str = f"{int(time_elapsed)}s"
    remaining_str = f"{int(time_remaining)}s" if time_remaining > 0 else "¡TIEMPO!"
    
    # HTML para la tarjeta
    timer_html = f"""
    <div class="{card_class}">
        <h3>🚪 {door_id}</h3>
        <p>Tiempo transcurrido: <strong>{elapsed_str}</strong> / {delay_seconds}s</p>
        <p>{"🚨 ALARMA ACTIVA" if alarm_triggered else f"Tiempo restante: {remaining_str}"}</p>
        <div class="timer-progress">
            <div class="timer-fill" style="width: {min(100, progress_percent)}%"></div>
        </div>
        <p style="font-size: 0.9em; opacity: 0.8;">Cámara: {timer_info['camera_id']}</p>
    </div>
    """
    
    st.markdown(timer_html, unsafe_allow_html=True)

def display_timer_controls(alert_manager: AlertManager):
    """Mostrar controles para gestionar temporizadores y alarmas"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔕 Detener Todas las Alarmas", type="primary", use_container_width=True):
            alert_manager.stop_all_alarms()
            st.success("Todas las alarmas detenidas")
    
    with col2:
        # Selector de puerta para reconocer
        active_timers = alert_manager.get_active_timers()
        if active_timers:
            door_ids = [t['door_id'] for t in active_timers if t['alarm_triggered']]
            if door_ids:
                selected_door = st.selectbox("Reconocer alarma de:", door_ids)
                if st.button("✅ Reconocer", use_container_width=True):
                    alert_manager.acknowledge_alarm(selected_door)
                    st.success(f"Alarma de {selected_door} reconocida")
    
    with col3:
        # Control de sonido
        sound_enabled = alert_manager.config.get('sound_enabled', True)
        new_sound_state = st.checkbox("🔊 Sonido habilitado", value=sound_enabled)
        if new_sound_state != sound_enabled:
            alert_manager.config['sound_enabled'] = new_sound_state
            alert_manager.save_config()

def display_timer_configuration(alert_manager: AlertManager):
    """Mostrar y editar configuración de temporizadores"""
    st.subheader("⏱️ Configuración de Temporizadores")
    
    # Configuración actual
    timer_delays = alert_manager.config.get('timer_delays', {})
    
    # Tabs para diferentes configuraciones
    tab1, tab2, tab3 = st.tabs(["⏰ Delays por Zona", "👁️ Perfiles de Tiempo", "🔧 Avanzado"])
    
    with tab1:
        st.markdown("### Configurar delays por zona/cámara")
        
        # Editor de delays
        col1, col2 = st.columns(2)
        
        with col1:
            zone_name = st.text_input("Nombre de zona/cámara", placeholder="ej: entrance, cam1")
            delay_value = st.number_input("Delay (segundos)", min_value=1, max_value=3600, value=30)
            
            if st.button("➕ Agregar/Actualizar"):
                if zone_name:
                    timer_delays[zone_name] = delay_value
                    alert_manager.config['timer_delays'] = timer_delays
                    alert_manager.save_config()
                    st.success(f"Configuración guardada: {zone_name} = {delay_value}s")
        
        with col2:
            st.markdown("### Configuraciones actuales")
            delays_df = pd.DataFrame(
                [(k, f"{v}s") for k, v in timer_delays.items()],
                columns=["Zona/Cámara", "Delay"]
            )
            st.dataframe(delays_df, use_container_width=True)
    
    with tab2:
        st.markdown("### Perfiles de tiempo predefinidos")
        
        profiles = alert_manager.config.get('timer_profiles', {})
        selected_profile = st.selectbox(
            "Seleccionar perfil",
            options=list(profiles.keys()),
            format_func=lambda x: f"{x} - {profiles[x].get('description', '')}"
        )
        
        if selected_profile and st.button("🔄 Aplicar Perfil"):
            # Aplicar delays del perfil seleccionado
            profile_delays = profiles[selected_profile].get('delays', {})
            alert_manager.config['timer_delays'].update(profile_delays)
            alert_manager.save_config()
            st.success(f"Perfil '{selected_profile}' aplicado")
    
    with tab3:
        st.markdown("### Configuración avanzada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            units = st.radio(
                "Unidad de tiempo",
                ["seconds", "minutes"],
                index=0 if alert_manager.config.get('timer_units') == 'seconds' else 1
            )
            alert_manager.config['timer_units'] = units
        
        with col2:
            visual_alerts = st.checkbox(
                "Alertas visuales",
                value=alert_manager.config.get('visual_alerts', True)
            )
            alert_manager.config['visual_alerts'] = visual_alerts
        
        if st.button("💾 Guardar configuración avanzada"):
            alert_manager.save_config()
            st.success("Configuración guardada")

async def process_image_with_timers(model, image, alert_manager, camera_id="default"):
    """Procesar imagen y actualizar temporizadores"""
    # Detectar con YOLO
    results = model.predict(image, conf=0.5, iou=0.5, verbose=False)
    
    # Extraer detecciones
    detections = []
    if len(results) > 0 and results[0].boxes is not None:
        for i, box in enumerate(results[0].boxes):
            detection = {
                'class_name': model.names[int(box.cls)],
                'confidence': float(box.conf),
                'bbox': {
                    'x1': int(box.xyxy[0][0]),
                    'y1': int(box.xyxy[0][1]),
                    'x2': int(box.xyxy[0][2]),
                    'y2': int(box.xyxy[0][3])
                },
                'door_id': f"{camera_id}_door_{i}"
            }
            detections.append(detection)
    
    # Procesar con sistema de temporizadores
    await alert_manager.process_detection(detections, camera_id)
    
    # Obtener imagen anotada
    annotated_frame = results[0].plot()
    
    return annotated_frame, detections

def main():
    """Función principal del dashboard V2"""
    
    # Header
    st.title("🛡️ Sistema de Seguridad YOLO11 V2 - Con Temporizadores")
    st.markdown("*Sistema inteligente con delays configurables antes de activar alarmas*")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuración")
    
    # Modo de operación
    mode = st.sidebar.selectbox(
        "Modo de Operación",
        ["🚨 Monitor de Alertas", "📸 Análisis de Imagen", "⏱️ Configurar Temporizadores", "📊 Estadísticas"]
    )
    
    # Cargar modelo y gestor de alertas
    model = load_security_detector()
    alert_manager = load_alert_manager_v2()
    
    if model is None:
        st.error("No se pudo cargar el modelo de detección")
        st.stop()
    
    if alert_manager is None:
        st.error("No se pudo cargar el gestor de alertas V2")
        st.stop()
    
    # Mostrar información
    st.sidebar.success("✅ Modelo cargado")
    st.sidebar.success("✅ Sistema de alertas V2 activo")
    
    if mode == "🚨 Monitor de Alertas":
        st.header("Monitor de Alertas en Tiempo Real")
        
        # Controles principales
        display_timer_controls(alert_manager)
        
        # Divisor
        st.markdown("---")
        
        # Layout de dos columnas
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("⏱️ Temporizadores Activos")
            
            # Auto-refresh
            refresh_rate = st.slider("Frecuencia de actualización (segundos)", 1, 10, 2)
            
            # Contenedor para temporizadores
            timer_container = st.container()
            
            # Loop de actualización
            while True:
                with timer_container:
                    active_timers = alert_manager.get_active_timers()
                    
                    if active_timers:
                        for timer in active_timers:
                            display_timer_card(timer)
                    else:
                        st.info("No hay puertas abiertas detectadas")
                
                # Esperar antes de actualizar
                time.sleep(refresh_rate)
                timer_container.empty()
        
        with col2:
            st.subheader("📊 Resumen")
            
            # Métricas
            active_timers = alert_manager.get_active_timers()
            active_alarms = sum(1 for t in active_timers if t['alarm_triggered'])
            
            st.metric("Puertas Abiertas", len(active_timers))
            st.metric("Alarmas Activas", active_alarms)
            
            # Estado del sistema
            if active_alarms > 0:
                st.error("🚨 SISTEMA EN ALERTA")
            elif len(active_timers) > 0:
                st.warning("⚠️ Monitoreando puertas abiertas")
            else:
                st.success("✅ Sistema normal")
    
    elif mode == "📸 Análisis de Imagen":
        st.header("Análisis de Imagen con Temporizadores")
        
        # Selector de cámara simulada
        camera_id = st.sidebar.selectbox(
            "Cámara simulada",
            ["cam1", "cam2", "cam3", "entrance", "loading"],
            help="Cada cámara puede tener diferentes delays configurados"
        )
        
        # Mostrar delay configurado
        delay = alert_manager.get_timer_delay("default", camera_id)
        st.sidebar.info(f"Delay para {camera_id}: {delay} segundos")
        
        # Subir imagen
        uploaded_file = st.file_uploader(
            "Subir Imagen",
            type=['jpg', 'jpeg', 'png', 'bmp']
        )
        
        if uploaded_file is not None:
            # Procesar imagen
            with st.spinner("Analizando imagen..."):
                image = Image.open(uploaded_file)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                annotated_image, detections = loop.run_until_complete(
                    process_image_with_timers(model, image, alert_manager, camera_id)
                )
                loop.close()
            
            # Mostrar resultados
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Imagen Original")
                st.image(image, use_column_width=True)
            
            with col2:
                st.subheader("Detecciones")
                st.image(annotated_image, use_column_width=True)
            
            # Información de puertas detectadas
            open_doors = [d for d in detections if d['class_name'] == 'gate_open']
            if open_doors:
                st.warning(f"""
                ⚠️ **{len(open_doors)} puerta(s) abierta(s) detectada(s)**
                
                Temporizador iniciado con delay de {delay} segundos.
                La alarma se activará si la puerta permanece abierta.
                """)
            else:
                st.success("✅ Todas las puertas están cerradas")
    
    elif mode == "⏱️ Configurar Temporizadores":
        st.header("Configuración de Temporizadores")
        display_timer_configuration(alert_manager)
    
    elif mode == "📊 Estadísticas":
        st.header("Estadísticas del Sistema")
        
        # Estadísticas de alertas
        stats = alert_manager.get_alert_statistics(hours=24)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Alertas (24h)", stats['total_alerts'])
        with col2:
            timers_active = len(alert_manager.get_active_timers())
            st.metric("Temporizadores Activos", timers_active)
        with col3:
            st.metric("Confianza Promedio", f"{stats['average_confidence']:.1%}")
        
        # Configuración actual de delays
        st.subheader("⏰ Configuración Actual de Delays")
        delays_df = pd.DataFrame(
            [(k, v) for k, v in alert_manager.config['timer_delays'].items()],
            columns=["Zona/Cámara", "Delay (segundos)"]
        )
        
        fig = px.bar(
            delays_df,
            x="Zona/Cámara",
            y="Delay (segundos)",
            title="Delays Configurados por Zona"
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
