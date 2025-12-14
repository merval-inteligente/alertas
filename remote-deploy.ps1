# Script PowerShell para desplegar en EC2 de forma remota
# Ejecuta comandos en la instancia EC2 sin sesión interactiva

$pemFile = "C:\Users\Nicolas\Desktop\labsuser.pem"
$ec2Host = "ec2-user@44.203.202.177"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Despliegue Remoto - Servicio de Alertas" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Comando más simple usando here-string
$script = "bash -c 'cd ~ && if [ -d alertas ]; then cd alertas && docker-compose down && git pull origin main; else git clone https://github.com/merval-inteligente/alertas.git && cd alertas; fi && docker-compose build --no-cache && docker-compose up -d && sleep 10 && docker ps && curl -s http://localhost:80/health'"

Write-Host "Ejecutando despliegue en EC2..." -ForegroundColor Yellow
Write-Host ""

# Ejecutar comandos remotamente
ssh -i $pemFile -o StrictHostKeyChecking=no $ec2Host $script

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Proceso completado" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Endpoints disponibles:" -ForegroundColor Cyan
Write-Host "  - Health: http://44.203.202.177/health"
Write-Host "  - Docs: http://44.203.202.177/docs"
Write-Host "  - News: http://44.203.202.177/news"
Write-Host "  - Tweets: http://44.203.202.177/tweets"
Write-Host "  - Alerts: http://44.203.202.177/alerts"
Write-Host ""
