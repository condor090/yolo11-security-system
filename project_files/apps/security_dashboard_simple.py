#!/usr/bin/env python3
"""
Dashboard de Seguridad Simplificado - Sin Plotly
Versión temporal mientras se resuelven las dependencias
"""

import streamlit as st
import cv2
import numpy as np
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Añadir ruta del proyecto
sys.path.append('/security_project')

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
            No