#!/bin/bash
# Script de despliegue para el servicio de Alertas en EC2
# Ejecutar este script en la instancia EC2 después de conectarse por SSH

set -e  # Detener si hay errores

echo "============================================"
echo "  Despliegue del Servicio de Alertas"
echo "============================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variables
REPO_URL="https://github.com/merval-inteligente/alertas.git"
APP_DIR="$HOME/alertas"
BRANCH="main"

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 1. Verificar y detener contenedores existentes
echo "Paso 1: Verificando contenedores Docker existentes..."
if docker ps -q > /dev/null 2>&1; then
    RUNNING_CONTAINERS=$(docker ps -q)
    if [ ! -z "$RUNNING_CONTAINERS" ]; then
        print_warning "Deteniendo contenedores en ejecución..."
        docker stop $RUNNING_CONTAINERS
        print_status "Contenedores detenidos"
    else
        print_status "No hay contenedores en ejecución"
    fi
else
    print_status "Docker está listo"
fi

# 2. Limpiar contenedores y volúmenes antiguos
echo ""
echo "Paso 2: Limpiando recursos Docker antiguos..."
docker container prune -f > /dev/null 2>&1 || true
print_status "Contenedores antiguos eliminados"

# 3. Preparar directorio de la aplicación
echo ""
echo "Paso 3: Preparando directorio de la aplicación..."
if [ -d "$APP_DIR" ]; then
    print_warning "Directorio existente encontrado, actualizando..."
    cd "$APP_DIR"
    
    # Detener servicios si están corriendo
    if [ -f "docker-compose.yml" ]; then
        docker-compose down > /dev/null 2>&1 || true
    fi
    
    # Actualizar repositorio
    git fetch origin
    git reset --hard origin/$BRANCH
    git pull origin $BRANCH
    print_status "Repositorio actualizado"
else
    print_warning "Clonando repositorio por primera vez..."
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
    print_status "Repositorio clonado"
fi

# 4. Verificar archivo .env
echo ""
echo "Paso 4: Verificando configuración..."
if [ ! -f ".env" ]; then
    print_error "ERROR: Archivo .env no encontrado"
    print_warning "Por favor, crea el archivo .env con las variables necesarias:"
    echo ""
    cat .env.example 2>/dev/null || echo "MONGODB_URI=mongodb://usuario:password@host:27017/"
    echo ""
    exit 1
fi
print_status "Archivo .env encontrado"

# 5. Construir imagen Docker
echo ""
echo "Paso 5: Construyendo imagen Docker..."
docker-compose build --no-cache
print_status "Imagen construida exitosamente"

# 6. Levantar servicio
echo ""
echo "Paso 6: Levantando servicio..."
docker-compose up -d
print_status "Servicio iniciado"

# 7. Esperar a que el servicio esté listo
echo ""
echo "Paso 7: Esperando a que el servicio esté listo..."
sleep 10

# 8. Verificar estado del servicio
echo ""
echo "Paso 8: Verificando estado del servicio..."
if docker ps | grep -q alertas-service; then
    print_status "Contenedor alertas-service está corriendo"
    
    # Verificar endpoint de health
    echo ""
    echo "Verificando endpoint /health..."
    sleep 5
    
    HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80/health || echo "000")
    
    if [ "$HEALTH_CHECK" = "200" ]; then
        print_status "Health check exitoso (HTTP 200)"
    else
        print_warning "Health check retornó código: $HEALTH_CHECK"
        echo "Puede que el servicio necesite más tiempo para iniciar..."
    fi
else
    print_error "ERROR: El contenedor no está corriendo"
    echo ""
    echo "Logs del contenedor:"
    docker-compose logs --tail=50
    exit 1
fi

# 9. Mostrar información del servicio
echo ""
echo "============================================"
echo "  ✓ Despliegue Completado"
echo "============================================"
echo ""
echo "Información del servicio:"
echo "  - Contenedor: alertas-service"
echo "  - Puerto: 80"
echo "  - IP Privada: 172.31.20.50"
echo "  - IP Pública: 34.229.85.176"
echo ""
echo "Endpoints disponibles:"
echo "  - Health Check: http://34.229.85.176/health"
echo "  - Documentación: http://34.229.85.176/docs"
echo "  - News: http://34.229.85.176/news"
echo "  - Tweets: http://34.229.85.176/tweets"
echo "  - Alerts: http://34.229.85.176/alerts"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: docker-compose logs -f"
echo "  - Ver estado: docker-compose ps"
echo "  - Reiniciar: docker-compose restart"
echo "  - Detener: docker-compose down"
echo ""
