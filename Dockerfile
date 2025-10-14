# Dockerfile para producción Django + PostgreSQL
FROM python:3.12-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear directorio de la app
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el código fuente
COPY . .

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Puerto expuesto
EXPOSE 8000

# Comando de inicio (gunicorn recomendado para producción)
CMD ["gunicorn", "torneos_app.wsgi:application", "--bind", "0.0.0.0:8000"]
