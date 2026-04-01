# Usar una imagen oficial de Python ligera
FROM python:3.12-slim

# 1. Variables de entorno de Python
# Evita que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python haga buffer en stdout/stderr (útil para ver logs en tiempo real)
ENV PYTHONUNBUFFERED=1

# 2. Establecer el directorio de trabajo
WORKDIR /app

# 3. Instalar dependencias del sistema necesarias (ej. para compilar psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copiar el código del proyecto
COPY . /app/

# 6. Crear un usuario sin privilegios root y cambiar la propiedad de los archivos
RUN adduser --disabled-password --no-create-home appuser && \
    chown -R appuser:appuser /app

# Cambiar al usuario no-root
USER appuser

# 7. Exponer el puerto
EXPOSE 8000

# 8. Comando por defecto (modo desarrollo)
# Nota: En producción usaremos Gunicorn en lugar de runserver
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]