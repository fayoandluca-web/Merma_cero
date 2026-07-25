# trigger_alerts.ps1
# Script para disparar el envío de alertas climáticas automáticas a todos los vendedores

$Url = "http://127.0.0.1:8000/alerts/trigger"
Write-Host "Iniciando disparo de alertas automáticas de Merma Cero..." -ForegroundColor Cyan

try {
    $Response = Invoke-RestMethod -Uri $Url -Method Post -ContentType "application/json"
    Write-Host "¡Alertas procesadas con éxito por el servidor!" -ForegroundColor Green
    Write-Host "Alertas enviadas: $($Response.alerts_sent_count)" -ForegroundColor Yellow
    Write-Host "Destinatarios: $($Response.recipients -join ', ')" -ForegroundColor Gray
} catch {
    Write-Error "Fallo al conectar con el servidor de Merma Cero. Asegúrate de que el servidor esté corriendo en el puerto 8000."
}
