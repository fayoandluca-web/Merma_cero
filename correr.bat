@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo =====================================================================
echo    🔮 Iniciando Pipeline de Control del Proyecto Merma Cero
echo =====================================================================

:: 1. Verificar Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado o no se encuentra en el PATH.
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
    echo [ERROR] Falló la instalación de dependencias de Python.
    pause
    exit /b 1
)

:: 4. Verificar Node.js (requerido para pruebas de paridad)
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARN] Node.js no está instalado. No se podrán correr pruebas de paridad.
)

:: 5. Ejecutar Pruebas Unitarias
echo [*] Ejecutando batería de pruebas unitarias y de integración...
python -m unittest test_merma_cero.py
if %errorlevel% neq 0 (
    echo [ERROR] Las pruebas unitarias fallaron. Abortando lanzamiento.
    pause
    exit /b 1
)
echo [OK] Pruebas unitarias aprobadas.

:: 6. Ejecutar Pruebas de Paridad si Node.js está disponible
where node >nul 2>nul
if %errorlevel% eq 0 (
    echo [*] Ejecutando pruebas de paridad matemática (Python vs JS)...
    python test_paridad.py
    if !errorlevel! neq 0 (
        echo [ERROR] Fallaron las pruebas de paridad matemática.
        pause
        exit /b 1
    )
    echo [OK] Paridad matemática garantizada al 100%%.
)

:: 7. Generar index.html
echo [*] Compilando e indexando frontend estático index.html...
python exportar_web.py

:: 8. Lanzar servidor FastAPI
echo =====================================================================
echo    🚀 Lanzando Servidor FastAPI en http://localhost:8000
echo    La documentación interactiva estará disponible en /docs
echo =====================================================================

start "" "http://localhost:8000/docs"
python cli.py servidor

pause
