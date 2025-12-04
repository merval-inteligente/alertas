# 🚀 Guía de Despliegue - Servicio de Alertas en EC2

## 📋 Información de la Instancia

- **IP Pública:** 34.229.85.176
- **IP Privada:** 172.31.20.50
- **Puerto:** 80
- **Comando SSH:** `ssh -i labsuser.pem ec2-user@34.229.85.176`

## 🎯 Arquitectura del Servicio

- **Framework:** FastAPI
- **Runtime:** Python 3.11
- **Puerto:** 80 (expuesto al ALB)
- **Contenedor:** Docker + Docker Compose
- **Base de datos:** MongoDB (externa)

## 📝 Pasos de Despliegue

### Opción 1: Despliegue Automático (Recomendado)

#### 1. Conectarse a la instancia EC2

Desde tu terminal local (PowerShell en Windows):

```powershell
cd C:\Users\Nicolas\Desktop
ssh -i labsuser.pem ec2-user@34.229.85.176
```

#### 2. Ejecutar el script de despliegue

Una vez conectado a la instancia EC2:

```bash
# Descargar el script de despliegue
curl -O https://raw.githubusercontent.com/merval-inteligente/alertas/main/deploy.sh

# Dar permisos de ejecución
chmod +x deploy.sh

# Ejecutar el despliegue
./deploy.sh
```

El script automáticamente:
- ✅ Verifica y detiene contenedores existentes
- ✅ Clona/actualiza el repositorio
- ✅ Verifica el archivo .env
- ✅ Construye la imagen Docker
- ✅ Levanta el servicio
- ✅ Verifica el health check

---

### Opción 2: Despliegue Manual

#### 1. Conectarse a la instancia

```powershell
ssh -i labsuser.pem ec2-user@34.229.85.176
```

#### 2. Verificar contenedores existentes

```bash
docker ps
```

Si hay contenedores corriendo:

```bash
docker stop $(docker ps -q)
docker container prune -f
```

#### 3. Clonar o actualizar el repositorio

**Si es la primera vez:**
```bash
cd ~
git clone https://github.com/merval-inteligente/alertas.git
cd alertas
```

**Si ya existe el repositorio:**
```bash
cd ~/alertas
docker-compose down
git pull origin main
```

#### 4. Configurar variables de entorno

El archivo `.env` debe contener:

```env
MONGODB_URI=mongodb://usuario:password@host:27017/
DATABASE_NAME=alertas_db
DB_PORT=27017
```

**Verificar que existe:**
```bash
ls -la .env
cat .env  # Ver contenido (sin mostrar passwords en pantalla real)
```

**Si no existe, crearlo:**
```bash
nano .env
# Pegar las variables y guardar (Ctrl+X, Y, Enter)
```

#### 5. Construir y levantar el servicio

```bash
# Construir la imagen
docker-compose build --no-cache

# Levantar el servicio
docker-compose up -d

# Ver logs
docker-compose logs -f
```

#### 6. Verificar el servicio

```bash
# Ver contenedores corriendo
docker ps

# Verificar health check
curl http://localhost:80/health

# Verificar endpoints
curl http://localhost:80/docs
curl http://localhost:80/news
```

---

## 🔍 Verificación de Endpoints

### Desde la instancia EC2:

```bash
# Health check
curl http://localhost:80/health

# Noticias
curl http://localhost:80/news

# Tweets
curl http://localhost:80/tweets

# Alertas
curl http://localhost:80/alerts
```

### Desde tu navegador local:

- Health Check: http://34.229.85.176/health
- Documentación interactiva: http://34.229.85.176/docs
- Noticias: http://34.229.85.176/news
- Tweets: http://34.229.85.176/tweets
- Alertas: http://34.229.85.176/alerts

---

## 🛠️ Comandos Útiles

### Docker Compose

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver estado de servicios
docker-compose ps

# Reiniciar servicio
docker-compose restart

# Detener servicio
docker-compose down

# Reconstruir y reiniciar
docker-compose up -d --build
```

### Docker

```bash
# Ver contenedores corriendo
docker ps

# Ver todos los contenedores (incluyendo detenidos)
docker ps -a

# Ver logs de un contenedor
docker logs alertas-service

# Entrar al contenedor
docker exec -it alertas-service /bin/bash

# Ver uso de recursos
docker stats
```

### Git

```bash
# Actualizar código
git pull origin main

# Ver estado
git status

# Ver commits recientes
git log --oneline -10
```

---

## 🔧 Troubleshooting

### El servicio no inicia

```bash
# Ver logs detallados
docker-compose logs

# Verificar variables de entorno
cat .env

# Reconstruir sin caché
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Error de conexión a MongoDB

```bash
# Verificar que MONGODB_URI esté correcto en .env
cat .env | grep MONGODB_URI

# Probar conexión desde el contenedor
docker exec -it alertas-service python -c "from config import settings; print(settings.mongodb_uri)"
```

### Puerto 80 ocupado

```bash
# Ver qué proceso usa el puerto 80
sudo netstat -tulpn | grep :80

# O usar lsof
sudo lsof -i :80

# Detener proceso que usa el puerto
sudo kill -9 <PID>
```

### Contenedor se detiene inmediatamente

```bash
# Ver logs del contenedor
docker logs alertas-service

# Ver últimos logs antes de detenerse
docker-compose logs --tail=100
```

---

## 📊 Health Check del ALB

El ALB está configurado para verificar:
- **Endpoint:** `/health`
- **Puerto:** 80
- **Respuesta esperada:** HTTP 200

```json
{
  "status": "healthy",
  "database": "connected",
  "message": "API funcionando correctamente"
}
```

---

## 🔄 Actualización del Servicio

Para actualizar el servicio con nuevos cambios:

```bash
cd ~/alertas
docker-compose down
git pull origin main
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f
```

---

## 📁 Estructura del Proyecto

```
alertas/
├── main.py                 # Aplicación FastAPI
├── config.py              # Configuración y settings
├── database.py            # Conexión a MongoDB
├── models.py              # Modelos Pydantic
├── services.py            # Lógica de negocio
├── alert_utils.py         # Utilidades para alertas
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Imagen Docker
├── docker-compose.yml    # Orquestación Docker
├── .env                  # Variables de entorno (NO en git)
├── .env.example         # Ejemplo de variables
└── deploy.sh            # Script de despliegue
```

---

## ⚠️ Notas Importantes

1. **Puerto 80 requiere permisos root:** Docker Compose lo maneja automáticamente
2. **Archivo .env NO está en Git:** Debe crearse manualmente en la instancia
3. **MONGODB_URI debe ser accesible:** Verificar conexión de red
4. **El servicio debe escuchar en 0.0.0.0:** Ya configurado en el Dockerfile
5. **Health check del ALB:** El endpoint `/health` debe responder HTTP 200

---

## 📞 Soporte

Si encuentras problemas:

1. Verificar logs: `docker-compose logs -f`
2. Verificar variables de entorno: `cat .env`
3. Verificar conectividad a MongoDB
4. Verificar que el puerto 80 esté libre
5. Revisar security groups del ALB y la instancia EC2

---

✅ **¡Despliegue completado exitosamente!**
