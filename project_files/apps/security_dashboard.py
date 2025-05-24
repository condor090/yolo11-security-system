#!/usr/bin/env python3
"""
Dashboard de Seguridad - Interfaz Web con Streamlit
Monitoreo en tiempo real del sistema de seguridad YOLO11
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
import sys

# Añadir ruta del proyecto
sys.path.append('/security_project')
from scripts.security_system import SecurityDetector

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Seguridad YOLO11",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
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
        detector = SecurityDetector(
            model_path='/security_project/models/security_model_best.pt',
            config_path='/security_project/configs/security_dataset.yaml'
        )
        return detector
    except Exception as e:
        st.error(f"Error cargando detector: {e}")
        return None

def display_metrics(detection_stats: dict, system_state: dict):
    """Mostrar métricas principales"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🚪 Estado de Reja",
            value=system_state.get('gate_status', 'unknown').replace('_', ' ').title(),
            delta=None
        )
    
    with col2:
        persons_count = len(system_state.get('persons_detected', []))
        st.metric(
            label="👥 Personas Detectadas",
            value=persons_count,
            delta=None
        )
    
    with col3:
        vehicles_count = len(system_state.get('vehicles_detected', []))
        st.metric(
            label="🚗 Vehículos Detectados",
            value=vehicles_count,
            delta=None
        )
    
    with col4:
        alerts_count = len(system_state.get('alerts', []))
        st.metric(
            label="⚠️ Alertas Activas",
            value=alerts_count,
            delta=None
        )

def display_alerts(system_state: dict):
    """Mostrar alertas del sistema"""
    alerts = system_state.get('alerts', [])
    
    if alerts:
        st.subheader("🚨 Alertas del Sistema")
        
        for alert in alerts[-5:]:  # Mostrar últimas 5 alertas
            alert_time = datetime.fromisoformat(alert['timestamp']).strftime('%H:%M:%S')
            
            if alert['type'] == 'unauthorized_person':
                st.markdown(f"""
                <div class="alert-card">
                    <strong>⚠️ PERSONA NO AUTORIZADA</strong><br>
                    Tiempo: {alert_time}<br>
                    Cantidad: {alert['count']} persona(s)<br>
                    Ubicaciones detectadas: {len(alert['locations'])}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-card">
            <strong>✅ Sistema Normal</strong><br>
            No hay alertas activas en este momento.
        </div>
        """, unsafe_allow_html=True)

def display_detections_table(detections: list):
    """Mostrar tabla de detecciones"""
    if not detections:
        st.info("No hay detecciones en el frame actual")
        return
    
    # Preparar datos para la tabla
    table_data = []
    for det in detections:
        table_data.append({
            'Clase': det['class_name'].replace('_', ' ').title(),
            'Confianza': f"{det['confidence']:.2f}",
            'Centro X': det['center']['x'],
            'Centro Y': det['center']['y'],
            'Área': (det['bbox']['x2'] - det['bbox']['x1']) * (det['bbox']['y2'] - det['bbox']['y1'])
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)

def create_detection_chart(detection_stats: dict):
    """Crear gráfico de estadísticas de detección"""
    stats_data = {
        'Métrica': ['Total Detecciones', 'Cambios de Reja', 'Alertas No Autorizadas', 'Detecciones de Vehículos'],
        'Valor': [
            detection_stats.get('total_detections', 0),
            detection_stats.get('gate_status_changes', 0),
            detection_stats.get('unauthorized_alerts', 0),
            detection_stats.get('vehicle_detections', 0)
        ]
    }
    
    fig = px.bar(
        x=stats_data['Valor'],
        y=stats_data['Métrica'],
        orientation='h',
        title="Estadísticas del Sistema",
        labels={'x': 'Cantidad', 'y': 'Tipo de Evento'}
    )
    
    fig.update_layout(height=400)
    return fig

def process_uploaded_image(detector, uploaded_file):
    """Procesar imagen subida"""
    # Leer imagen
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    
    # Procesar con detector
    results = detector.detect_frame(image, confidence=0.6)
    
    # Dibujar detecciones
    image_with_detections = detector.draw_detections(image, results)
    
    # Convertir BGR a RGB para Streamlit
    image_rgb = cv2.cvtColor(image_with_detections, cv2.COLOR_BGR2RGB)
    
    return image_rgb, results

def main():
    """Función principal del dashboard"""
    
    # Header
    st.title("🛡️ Sistema de Seguridad YOLO11")
    st.markdown("*Detección inteligente de rejas, personas autorizadas y vehículos*")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuración")
    
    # Modo de operación
    mode = st.sidebar.selectbox(
        "Modo de Operación",
        ["📊 Dashboard en Vivo", "📸 Análisis de Imagen", "📈 Estadísticas Históricas"]
    )
    
    # Cargar detector
    detector = load_security_detector()
    
    if detector is None:
        st.error("No se pudo cargar el detector de seguridad")
        st.stop()
    
    if mode == "📊 Dashboard en Vivo":
        st.header("Monitoreo en Tiempo Real")
        
        # Configuración de cámara
        camera_source = st.sidebar.selectbox(
            "Fuente de Video",
            ["Webcam (0)", "Cámara IP", "Archivo de Video"]
        )
        
        confidence_threshold = st.sidebar.slider(
            "Umbral de Confianza",
            min_value=0.1,
            max_value=1.0,
            value=0.6,
            step=0.05
        )
        
        # Placeholder para video en vivo
        video_placeholder = st.empty()
        metrics_placeholder = st.empty()
        alerts_placeholder = st.empty()
        
        # Botones de control
        col1, col2, col3 = st.columns(3)
        with col1:
            start_btn = st.button("▶️ Iniciar", key="start")
        with col2:
            stop_btn = st.button("⏹️ Detener", key="stop")
        with col3:
            snapshot_btn = st.button("📸 Captura", key="snapshot")
        
        if start_btn:
            st.session_state.running = True
        if stop_btn:
            st.session_state.running = False
        
        # Simulación de datos en vivo (reemplazar con video real)
        if st.session_state.get('running', False):
            # Aquí iría la lógica de video en tiempo real
            st.info("Modo en vivo no implementado completamente. Use 'Análisis de Imagen' para probar funcionalidad.")
    
    elif mode == "📸 Análisis de Imagen":
        st.header("Análisis de Imagen")
        
        # Configuración
        confidence_threshold = st.sidebar.slider(
            "Umbral de Confianza",
            min_value=0.1,
            max_value=1.0,
            value=0.6,
            step=0.05
        )
        
        # Subir imagen
        uploaded_file = st.file_uploader(
            "Subir Imagen",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            help="Sube una imagen para analizar con el sistema de seguridad"
        )
        
        if uploaded_file is not None:
            # Procesar imagen
            with st.spinner("Analizando imagen..."):
                image_rgb, results = process_uploaded_image(detector, uploaded_file)
            
            # Mostrar resultados
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Imagen Original")
                # Mostrar imagen original
                file_bytes = np.asarray(bytearray(uploaded_file.getvalue()), dtype=np.uint8)
                original_image = cv2.imdecode(file_bytes, 1)
                original_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
                st.image(original_rgb, caption="Imagen Original", use_column_width=True)
            
            with col2:
                st.subheader("Detecciones")
                st.image(image_rgb, caption="Imagen con Detecciones", use_column_width=True)
            
            # Métricas
            st.subheader("📊 Métricas de Detección")
            if 'system_state' in results and 'stats' in results:
                display_metrics(results['stats'], results['system_state'])
            
            # Alertas
            st.subheader("🚨 Alertas")
            if 'system_state' in results:
                display_alerts(results['system_state'])
            
            # Tabla de detecciones
            st.subheader("📋 Detalle de Detecciones")
            if 'detections' in results:
                display_detections_table(results['detections'])
            
            # Gráfico de estadísticas
            if 'stats' in results:
                st.subheader("📈 Estadísticas")
                chart = create_detection_chart(results['stats'])
                st.plotly_chart(chart, use_container_width=True)
    
    elif mode == "📈 Estadísticas Históricas":
        st.header("Estadísticas Históricas")
        
        # Aquí iría la lógica para mostrar estadísticas históricas
        st.info("Funcionalidad de estadísticas históricas en desarrollo")
        
        # Ejemplo de gráficos
        st.subheader("Detecciones por Hora (Ejemplo)")
        
        # Datos de ejemplo
        hours = list(range(24))
        detections = np.random.poisson(5, 24)
        
        fig = px.line(
            x=hours,
            y=detections,
            title="Detecciones por Hora del Día",
            labels={'x': 'Hora', 'y': 'Número de Detecciones'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        Sistema de Seguridad YOLO11 v1.0 | 
        Detección de Rejas, Personas y Vehículos
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
