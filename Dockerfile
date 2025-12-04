# Dockerfile para el servicio de Alertas
# Python 3.11 con FastAPI y Uvicorn

FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Exponer puerto 80
EXPOSE 80

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1

# Comando para iniciar la aplicación
# Uvicorn escuchará en 0.0.0.0:80 para aceptar conexiones desde el ALB
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2"]
