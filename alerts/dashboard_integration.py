#!/usr/bin/env python3
"""
Dashboard Integration Script - Integra el modelo con el sistema de alertas V3
Actualiza el dashboard para usar el sistema de temporizador y alarma sonora
"""

import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import asyncio
from datetime import datetime
import json
from pathlib import Path
import pygame
import threading
import time

# Importar el sistema de alertas V3
import sys
sys.path.append(str(Path(__file__).parent.parent))
from alerts.alert_manager_v3 import AlertManagerV3, process_frame_with_alerts


def initialize_session_state():
    """Inicializar variables de sesión de Streamlit"""
    if 'alert_manager' not in st.session_state:
        st.session_state.alert_manager = AlertManagerV3(enable_sound=True)
    
    if 'model' not in st.session_state:
        model_path = "runs/gates/gate_detector_v1/weights/best.pt"
        if Path(model_path).exists():
            st.session_state.model = YOLO(model_path)
            st.success(f"✅ Modelo cargado: {model_path}")
        else:
            st.error("❌ No se encontró el modelo entrenado")
            st.session_state.model = None
    
    if 'camera_location' not in st.session_state:
        st.session_state.camera_location = "main_entrance"
    
    if 'grace_periods' not in st.session_state:
        st.session_state.grace_periods = {
            "main_entrance": 60,
            "office_door": 45,
            "warehouse": 90,
            "emergency_exit": 10
        }


def draw_detections_on_frame(frame, detections, monitoring_status):
    """Dibujar detecciones y estado de monitoreo en el frame"""
    annotated_frame = frame.copy()
    
    # Dibujar cajas de detección
    for det in detections:
        bbox = det['bbox']
        confidence = det['confidence']
        class_name = det['class_name']
        
        # Color según el tipo
        color = (0, 0, 255) if class_name == 'gate_open' else (0, 255, 0)
        
        # Dibujar caja
        cv2.rectangle(annotated_frame, 
                     (bbox['x1'], bbox['y1']), 
                     (bbox['x2'], bbox['y2']), 
                     color, 2)
        
        # Etiqueta
        label = f"{class_name} {confidence:.2f}"
        cv2.putText(annotated_frame, label, 
                   (bbox['x1'], bbox['y1'] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # Mostrar información de monitoreo
    if monitoring_status['monitored_doors'] > 0:
        y_offset = 30
        for door in monitoring_status['doors']:
            text = f"⏱️ Puerta monitoreada: {door['remaining_grace']}s restantes"
            color = (0, 165, 255)  # Naranja
            
            if door['remaining_grace'] <= 10:
                color = (0, 0, 255)  # Rojo
                text = f"⚠️ ALERTA INMINENTE: {door['remaining_grace']}s"
            
            cv2.putText(annotated_frame, text,
                       (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30
    
    return annotated_frame


def main():
    st.set_page_config(
        page_title="YOLO11 Security - Sistema de Alertas V3",
        page_icon="🚨",
        layout="wide"
    )
    
    # Inicializar estado
    initialize_session_state()
    
    # Header
    st.title("🚨 Sistema de Seguridad YOLO11 - Alertas con Temporizador")
    st.markdown("**Versión 3.0** - Con alarma sonora y periodo de gracia configurable")
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selección de ubicación
        location = st.selectbox(
            "📍 Ubicación de Cámara",
            options=list(st.session_state.grace_periods.keys()),
            index=0
        )
        st.session_state.camera_location = location
        
        # Configuración de periodo de gracia
        st.subheader("⏱️ Periodo de Gracia")
        current_grace = st.session_state.grace_periods[location]
        
        new_grace = st.slider(
            f"Segundos para {location}",
            min_value=5,
            max_value=300,
            value=current_grace,
            step=5,
            help="Tiempo antes de activar la alarma"
        )
        
        if new_grace != current_grace:
            st.session_state.grace_periods[location] = new_grace
            st.session_state.alert_manager.update_grace_period(location, new_grace)
            st.success(f"✅ Actualizado a {new_grace}s")
        
        # Control de sonido
        st.subheader("🔊 Control de Sonido")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔇 Silenciar Todo"):
                st.session_state.alert_manager.mute_all_alarms()
                st.info("Alarmas silenciadas")
        
        with col2:
            if st.button("🔊 Test Sonido"):
                st.session_state.alert_manager.test_alarm_system()
        
        # Estado del sistema
        st.subheader("📊 Estado del Sistema")
        system_status = st.session_state.alert_manager.get_system_status()
        
        st.metric("Puertas Monitoreadas", 
                 system_status['monitoring']['monitored_doors'])
        
        if system_status['sound_alarms']:
            st.warning(f"🔊 {len(system_status['sound_alarms'])} alarmas activas")
    
    # Área principal
    if st.session_state.model is None:
        st.error("❌ Modelo no disponible. Verifica la ruta del modelo.")
        return
    
    # Tabs para diferentes modos
    tab1, tab2, tab3, tab4 = st.tabs(["📸 Imagen", "📹 Video", "📊 Dashboard", "📜 Historial"])
    
    with tab1:
        st.header("Análisis de Imagen Individual")
        
        uploaded_file = st.file_uploader("Sube una imagen", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            # Leer imagen
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Procesar con alertas
            if st.button("🔍 Analizar Imagen"):
                with st.spinner("Procesando..."):
                    # Ejecutar detección y alertas
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    detections, alert_result = loop.run_until_complete(
                        process_frame_with_alerts(
                            image,
                            st.session_state.model,
                            st.session_state.alert_manager,
                            st.session_state.camera_location
                        )
                    )
                    
                    # Mostrar resultados
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Imagen Original")
                        st.image(image_rgb)
                    
                    with col2:
                        st.subheader("Detecciones")
                        monitoring_status = st.session_state.alert_manager.get_monitoring_status()
                        annotated = draw_detections_on_frame(image_rgb, detections, monitoring_status)
                        st.image(annotated)
                    
                    # Mostrar estado de alertas
                    st.subheader("🚨 Estado de Alertas")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Nuevos Monitoreos", alert_result.get('new_monitors', 0))
                    with col2:
                        st.metric("Alertas Creadas", alert_result.get('alerts_created', 0))
                    with col3:
                        st.metric("Puertas Cerradas", alert_result.get('doors_closed', 0))
                    
                    # Detalles de monitoreo
                    if monitoring_status['monitored_doors'] > 0:
                        st.warning("⏱️ **Puertas en Monitoreo:**")
                        for door in monitoring_status['doors']:
                            remaining = door['remaining_grace']
                            progress = 1 - (remaining / st.session_state.grace_periods[location])
                            
                            st.progress(progress)
                            st.write(f"ID: {door['id'][:8]}... | "
                                   f"Tiempo: {door['monitoring_time']}s | "
                                   f"Restante: {remaining}s | "
                                   f"Confianza: {door['last_confidence']:.2%}")
    
    with tab2:
        st.header("Análisis de Video en Tiempo Real")
        
        video_source = st.selectbox(
            "Selecciona fuente de video",
            ["Webcam (0)", "Archivo de Video", "Stream RTSP"]
        )
        
        if video_source == "Archivo de Video":
            video_file = st.file_uploader("Sube un video", type=['mp4', 'avi', 'mov'])
            if video_file is not None:
                # Guardar temporalmente
                temp_path = Path("temp_video.mp4")
                with open(temp_path, "wb") as f:
                    f.write(video_file.read())
                video_path = str(temp_path)
            else:
                video_path = None
        elif video_source == "Webcam (0)":
            video_path = 0
        else:
            video_path = st.text_input("URL del stream RTSP")
        
        if video_path is not None and st.button("▶️ Iniciar Análisis"):
            stframe = st.empty()
            stop_button = st.button("⏹️ Detener")
            
            cap = cv2.VideoCapture(video_path)
            
            while cap.isOpened() and not stop_button:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Procesar frame
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                detections, alert_result = loop.run_until_complete(
                    process_frame_with_alerts(
                        frame,
                        st.session_state.model,
                        st.session_state.alert_manager,
                        st.session_state.camera_location
                    )
                )
                
                # Dibujar y mostrar
                monitoring_status = st.session_state.alert_manager.get_monitoring_status()
                annotated = draw_detections_on_frame(frame, detections, monitoring_status)
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                
                stframe.image(annotated_rgb, channels="RGB", use_column_width=True)
            
            cap.release()
    
    with tab3:
        st.header("📊 Dashboard en Tiempo Real")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        monitoring = system_status['monitoring']
        stats = system_status['statistics']
        
        with col1:
            st.metric("🚪 Puertas Monitoreadas", monitoring['monitored_doors'])
        with col2:
            st.metric("🔊 Alarmas Activas", len(system_status['sound_alarms']))
        with col3:
            st.metric("📊 Alertas (24h)", stats.get('total_alerts', 0))
        with col4:
            st.metric("⏱️ Tiempo Promedio", 
                     f"{stats.get('response_times', {}).get('average_seconds', 0):.1f}s")
        
        # Gráfico de actividad
        if st.button("🔄 Actualizar Dashboard"):
            st.rerun()
        
        # Lista de puertas monitoreadas
        if monitoring['monitored_doors'] > 0:
            st.subheader("🚪 Puertas en Monitoreo")
            
            for door in monitoring['doors']:
                with st.expander(f"Puerta {door['id'][:8]}..."):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Ubicación:** {door['location']}")
                        st.write(f"**Tiempo monitoreado:** {door['monitoring_time']}s")
                        st.write(f"**Detecciones:** {door['detection_count']}")
                    with col2:
                        st.write(f"**Periodo de gracia:** {remaining}s restantes")
                        st.write(f"**Última confianza:** {door['last_confidence']:.2%}")
                        
                        # Barra de progreso
                        progress = door['monitoring_time'] / (door['monitoring_time'] + door['remaining_grace'])
                        st.progress(progress)
    
    with tab4:
        st.header("📜 Historial de Alertas")
        
        # Aquí podrías mostrar el historial de alertas desde la base de datos
        st.info("Funcionalidad en desarrollo - Se mostrará el historial de alertas")


if __name__ == "__main__":
    # Configurar asyncio para Windows si es necesario
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    main()
