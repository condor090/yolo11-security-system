#!/usr/bin/env python3
"""
Script para resetear completamente el sistema de alarmas
"""

import json
import os
from pathlib import Path

# Directorio base
base_dir = Path(__file__).parent

# Archivos a limpiar
files_to_clean = [
    "alerts/alert_state.json",
    "alerts/alert_state_v2.json",
    "alerts/door_timers.json",
    "alerts/active_timers.json"
]

for file_path in files_to_clean:
    full_path = base_dir / file_path
    if full_path.exists():
        print(f"Eliminando: {full_path}")
        full_path.unlink()
    else:
        print(f"No existe: {full_path}")

# Crear estado limpio
clean_state = {
    "alert_history": [],
    "cooldown_tracker": {},
    "monitored_doors": {},
    "statistics": {}
}

# Guardar estado limpio
state_files = [
    base_dir / "alerts/alert_state.json",
    base_dir / "alerts/alert_state_v2.json"
]

for state_file in state_files:
    state_file.parent.mkdir(exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump(clean_state, f, indent=2)
    print(f"Creado estado limpio: {state_file}")

print("\n✅ Sistema reseteado completamente")
print("🔄 Reinicia el backend para aplicar los cambios")
