# Usamos Python 3.12 Slim para mantener la imagen ligera
FROM python:3.12-slim

# Evita que Python genere archivos .pyc y buffer de salida
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema mínimas (si se necesitan)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar caché de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/ ./src/
# (Opcional) Copiar docs o scripts si son necesarios en runtime, pero para el ETL solo necesitamos src

# Usuario no-root por seguridad
RUN useradd -m appuser
USER appuser

# Comando de ejecución
CMD ["python", "-m", "src.main"]
