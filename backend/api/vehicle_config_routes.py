"""
Rutas API para configuración de vehículos
Sistema de configuración dinámica para tipos de vehículos y reglas
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
import os
from datetime import datetime

router = APIRouter(prefix="/api/config/vehicles", tags=["vehicle_config"])

# Ruta del archivo de configuración
CONFIG_FILE = "/Users/Shared/yolo11_project/backend/configs/vehicle_config_dynamic.json"

# Configuración por defecto si no existe el archivo
DEFAULT_CONFIG = {
    "vehicle_types": [
        {
            "tipo": "vimifos",
            "nombre_display": "Vimifos",
            "duracion_minutos": 120,
            "prioridad": 2,
            "hora_inicio": "05:30",
            "hora_fin": "07:00",
            "ventana_estricta": True,
            "requisitos_especiales": ["material_organico", "bioseguridad"],
            "color_ui": "#EF4444",
            "icono": "truck",
            "activo": True
        },
        {
            "tipo": "genetica",
            "nombre_display": "Genética",
            "duracion_minutos": 45,
            "prioridad": 1,
            "hora_inicio": "09:00",
            "hora_fin": "10:00",
            "ventana_estricta": True,
            "requisitos_especiales": ["temperatura_controlada", "urgente"],
            "color_ui": "#3B82F6",
            "icono": "snowflake",
            "activo": True
        },
        {
            "tipo": "jaula_lechonera",
            "nombre_display": "Jaula Lechonera",
            "duracion_minutos": 90,
            "prioridad": 3,
            "hora_inicio": "",
            "hora_fin": "",
            "ventana_estricta": False,
            "requisitos_especiales": ["desinfeccion_profunda"],
            "color_ui": "#10B981",
            "icono": "piggy-bank",
            "activo": True
        },
        {
            "tipo": "jaula_cerdos_engorda",
            "nombre_display": "Jaula Cerdos Engorda",
            "duracion_minutos": 75,
            "prioridad": 4,
            "hora_inicio": "",
            "hora_fin": "",
            "ventana_estricta": False,
            "requisitos_especiales": [],
            "color_ui": "#F59E0B",
            "icono": "bacon",
            "activo": True
        },
        {
            "tipo": "tractocamion",
            "nombre_display": "Tractocamión",
            "duracion_minutos": 60,
            "prioridad": 5,
            "hora_inicio": "",
            "hora_fin": "",
            "ventana_estricta": False,
            "requisitos_especiales": [],
            "color_ui": "#6366F1",
            "icono": "truck-loading",
            "activo": True
        }
    ],
    "conflict_rules": [
        {
            "nombre": "vimifos_tarde",
            "descripcion": "Vimifos no puede llegar después de las 7:00 AM",
            "vehiculo_afectado": "vimifos",
            "condicion": {
                "hora_llegada_despues": "07:00",
                "conflicto_con": "genetica"
            },
            "accion": "RECHAZAR",
            "mensaje": "Vimifos rechazado: Su lavado de 2h comprometería el horario de Genética (9am). Debe llegar entre 5:30-7:00am.",
            "nivel_alerta": "critical",
            "activa": True
        },
        {
            "nombre": "genetica_fuera_horario",
            "descripcion": "Genética debe llegar en su ventana de tiempo",
            "vehiculo_afectado": "genetica",
            "condicion": {
                "fuera_de_horario": True
            },
            "accion": "ALERTAR",
            "mensaje": "Genética fuera de horario: Material sensible a temperatura. Notificar a supervisor inmediatamente.",
            "nivel_alerta": "high",
            "activa": True
        }
    ],
    "system_settings": {
        "max_lavados_simultaneos": 1,
        "tiempo_buffer_minutos": 15,
        "accion_vehiculo_desconocido": "ALERTAR",
        "umbral_confianza_deteccion": 0.7,
        "capturar_foto_rechazos": True,
        "notificar_telegram": True,
        "modo_debug": False
    }
}

def load_config():
    """Carga la configuración desde el archivo o usa la predeterminada"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG

def save_config(config):
    """Guarda la configuración en el archivo"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# ENDPOINTS PARA TIPOS DE VEHÍCULOS

@router.get("/types")
async def get_vehicle_types():
    """Obtiene todos los tipos de vehículos"""
    config = load_config()
    return config.get("vehicle_types", [])

@router.post("/types")
async def create_vehicle_type(vehicle_type: Dict[str, Any]):
    """Crea un nuevo tipo de vehículo"""
    config = load_config()
    
    # Verificar que no exista
    existing = [vt for vt in config["vehicle_types"] if vt["tipo"] == vehicle_type["tipo"]]
    if existing:
        raise HTTPException(status_code=400, detail="El tipo de vehículo ya existe")
    
    config["vehicle_types"].append(vehicle_type)
    save_config(config)
    return {"message": "Tipo de vehículo creado exitosamente"}

@router.put("/types/{tipo}")
async def update_vehicle_type(tipo: str, vehicle_type: Dict[str, Any]):
    """Actualiza un tipo de vehículo existente"""
    config = load_config()
    
    # Buscar y actualizar
    found = False
    for i, vt in enumerate(config["vehicle_types"]):
        if vt["tipo"] == tipo:
            config["vehicle_types"][i] = vehicle_type
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Tipo de vehículo no encontrado")
    
    save_config(config)
    return {"message": "Tipo de vehículo actualizado exitosamente"}

@router.delete("/types/{tipo}")
async def delete_vehicle_type(tipo: str):
    """Desactiva un tipo de vehículo"""
    config = load_config()
    
    # Buscar y desactivar (no eliminar)
    found = False
    for vt in config["vehicle_types"]:
        if vt["tipo"] == tipo:
            vt["activo"] = False
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Tipo de vehículo no encontrado")
    
    save_config(config)
    return {"message": "Tipo de vehículo desactivado exitosamente"}

# ENDPOINTS PARA REGLAS DE CONFLICTO

@router.get("/rules")
async def get_conflict_rules():
    """Obtiene todas las reglas de conflicto"""
    config = load_config()
    return config.get("conflict_rules", [])

@router.post("/rules")
async def create_conflict_rule(rule: Dict[str, Any]):
    """Crea una nueva regla de conflicto"""
    config = load_config()
    
    # Verificar que no exista
    existing = [r for r in config["conflict_rules"] if r["nombre"] == rule["nombre"]]
    if existing:
        raise HTTPException(status_code=400, detail="La regla ya existe")
    
    config["conflict_rules"].append(rule)
    save_config(config)
    return {"message": "Regla de conflicto creada exitosamente"}

@router.put("/rules/{nombre}")
async def update_conflict_rule(nombre: str, rule: Dict[str, Any]):
    """Actualiza una regla de conflicto existente"""
    config = load_config()
    
    # Buscar y actualizar
    found = False
    for i, r in enumerate(config["conflict_rules"]):
        if r["nombre"] == nombre:
            config["conflict_rules"][i] = rule
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    
    save_config(config)
    return {"message": "Regla actualizada exitosamente"}

@router.delete("/rules/{nombre}")
async def delete_conflict_rule(nombre: str):
    """Desactiva una regla de conflicto"""
    config = load_config()
    
    # Buscar y desactivar
    found = False
    for r in config["conflict_rules"]:
        if r["nombre"] == nombre:
            r["activa"] = False
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    
    save_config(config)
    return {"message": "Regla desactivada exitosamente"}

# ENDPOINTS PARA CONFIGURACIÓN DEL SISTEMA

@router.get("/settings")
async def get_system_settings():
    """Obtiene la configuración general del sistema"""
    config = load_config()
    return config.get("system_settings", {})

@router.put("/settings")
async def update_system_settings(settings: Dict[str, Any]):
    """Actualiza la configuración general del sistema"""
    config = load_config()
    config["system_settings"] = settings
    save_config(config)
    return {"message": "Configuración actualizada exitosamente"}

# ENDPOINTS ADICIONALES

@router.get("/export")
async def export_configuration():
    """Exporta toda la configuración"""
    config = load_config()
    config["exported_at"] = datetime.now().isoformat()
    config["version"] = "1.0"
    return config

@router.post("/import")
async def import_configuration(imported_config: Dict[str, Any]):
    """Importa una configuración completa"""
    # Validar estructura básica
    required_keys = ["vehicle_types", "conflict_rules", "system_settings"]
    for key in required_keys:
        if key not in imported_config:
            raise HTTPException(status_code=400, detail=f"Falta la clave requerida: {key}")
    
    # Guardar respaldo de la configuración actual
    current_config = load_config()
    backup_file = CONFIG_FILE.replace(".json", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(current_config, f, indent=2, ensure_ascii=False)
    
    # Importar nueva configuración
    save_config(imported_config)
    return {"message": "Configuración importada exitosamente", "backup": backup_file}
