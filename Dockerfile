# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /code

COPY requirements.txt .

# CAMBIO IMPORTANTE:
# Instalamos en una carpeta temporal (/install) en lugar de --user (/root/.local)
# Esto prepara las librerías para ser movidas a una carpeta pública.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Final image
FROM python:3.10-slim

WORKDIR /app

# 1. Crear usuario
RUN addgroup --system app && adduser --system --ingroup app app

# 2. Copiar las librerías desde el builder a /usr/local
# /usr/local es accesible por todos los usuarios, solucionando el "Permission denied"
COPY --from=builder /install /usr/local

# 3. Copiar el código
COPY . .

# 4. Crear el archivo de routers interno (solución anterior)
RUN echo "[]" > routers.json && chown app:app routers.json

# 5. Cambiar al usuario limitado
USER app

EXPOSE 8000

# Ya no necesitamos configurar PATH extraño porque /usr/local/bin ya es estándar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]