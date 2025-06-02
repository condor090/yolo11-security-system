#!/bin/bash
# Script para diagnosticar y solucionar problemas de git push

echo "🔍 Diagnóstico de Git Push para YOMJAI v3.9.0"
echo "=============================================="

cd /Users/Shared/yolo11_project

echo -e "\n1. Verificando configuración de credenciales:"
git config --list | grep credential

echo -e "\n2. Estado del repositorio:"
git status -s

echo -e "\n3. Commits pendientes:"
git log origin/main..HEAD --oneline

echo -e "\n4. Intentando push con debug:"
GIT_CURL_VERBOSE=1 GIT_TRACE=1 git push origin main 2>&1 | head -20

echo -e "\n=============================================="
echo "💡 Si el push falla, intente:"
echo "   1. git config --global credential.helper osxkeychain"
echo "   2. git push origin main (ingrese credenciales cuando se solicite)"
echo "   3. Use un Personal Access Token si tiene 2FA activado"
