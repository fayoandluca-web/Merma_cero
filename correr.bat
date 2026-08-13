@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo    Iniciando Pipeline de Control del Proyecto Merma Cero
echo =====================================================================

:: 1. Verificar Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    pause
    exit /b 1
)

:: 2. Crear y activar entorno virtual si no existe
if not exist ".venv" (
    echo [*] Creando entorno virtual .venv...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo activar el entorno virtual .venv.
    pause
    exit /b 1
)

:: 3. Instalar/Actualizar dependencias
echo [*] Instalando dependencias desde requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la instalacion de dependencias de Python.
    pause
    exit /b 1
)

:: 4. Generar index.html
echo [*] Compilando e indexando frontend estatico index.html...
python exportar_web.py

:: 5. Lanzar servidor FastAPI
echo =====================================================================
echo    Lanzando Servidor FastAPI en http://localhost:8000
echo    La documentacion interactiva estara disponible en /docs
echo =====================================================================

start "" "http://localhost:8000/docs"
python cli.py servidor

pause
