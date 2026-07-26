# Dockerfile para desplegar Merma Cero en la nube (Railway/Render/etc.)
FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc y habilitar buffering de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto dentro de la subcarpeta 'merma_cero' 
# para mantener la compatibilidad con las importaciones de Python.
COPY . merma_cero/

# Cambiar al directorio de ejecución del código
WORKDIR /app/merma_cero

# Exponer el puerto
EXPOSE 8000

# Ejecutar el servidor Uvicorn usando main.py
CMD ["python", "main.py"]
