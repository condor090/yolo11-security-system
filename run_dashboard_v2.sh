#!/bin/bash
cd /Users/Shared/yolo11_project
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
python3 -m streamlit run project_files/apps/security_dashboard_v2.py --server.port 8503 --server.headless true
