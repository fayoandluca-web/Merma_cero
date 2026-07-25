# start.ps1
# Script de inicializacion y ejecucion del Proyecto Merma Cero para Windows PowerShell

$OutputEncoding = [System.Text.Encoding]::ASCII

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " [Oraculo Merma Cero]: Inicializador de Entorno de Resiliencia" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan

# 1. Verificar si Python esta instalado en la maquina
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "[OK] Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Error: Python no esta instalado o no se encuentra en el PATH del sistema."
    Write-Host "Por favor instala Python 3.12+ para ejecutar este proyecto." -ForegroundColor Yellow
    Exit 1
}

# Determinar directorio base del script
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}
Set-Location $ScriptDir

# 2. Gestionar Entorno Virtual (.venv)
$VenvPath = Join-Path $ScriptDir ".venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "[INFO] No se encontro entorno virtual. Creando entorno virtual en $VenvPath..." -ForegroundColor Yellow
    & python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Fallo al crear el entorno virtual de Python."
        Exit 1
    }
    Write-Host "[OK] Entorno virtual creado exitosamente." -ForegroundColor Green
}

# 3. Activar Entorno Virtual
Write-Host "[INFO] Activando entorno virtual..." -ForegroundColor Yellow
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    # Cambiar politica de ejecucion local para permitir activar el entorno
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
    . $ActivateScript
} else {
    Write-Error "No se pudo encontrar el script de activacion de venv en $ActivateScript"
    Exit 1
}

# 4. Instalar/Actualizar Dependencias
Write-Host "[INFO] Validando e instalando dependencias desde requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Fallo al actualizar pip. Continuando con instalacion de paquetes..." -ForegroundColor Yellow
}
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Fallo al instalar las dependencias del proyecto."
    Exit 1
}
Write-Host "[OK] Dependencias sincronizadas correctamente." -ForegroundColor Green

# 5. Ejecutar la Aplicacion segun los parametros de entrada
$Mode = $args[0]

if ($Mode -eq "--test") {
    Write-Host "[INFO] Iniciando bateria de pruebas unitarias locales..." -ForegroundColor Cyan
    python main.py --test
} elseif ($Mode -eq "--cli") {
    Write-Host "[INFO] Iniciando simulador de interfaz conversacional CLI..." -ForegroundColor Cyan
    python main.py --cli
} else {
    Write-Host "[INFO] Levantando servidor API de produccion (FastAPI)..." -ForegroundColor Cyan
    python main.py
}
