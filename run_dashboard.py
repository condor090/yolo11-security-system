#!/usr/bin/env python3
"""
Script para ejecutar el dashboard de seguridad localmente
"""

import os
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Cambiar al directorio del proyecto
os.chdir(project_root)

# Ejecutar streamlit
os.system("streamlit run project_files/apps/security_dashboard.py")
