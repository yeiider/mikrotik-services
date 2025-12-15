# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Final image
FROM python:3.10-slim

WORKDIR /app

# 1. Crear el usuario del sistema
RUN addgroup --system app && adduser --system --ingroup app app

# 2. Copiar dependencias compiladas
COPY --from=builder /root/.local /root/.local

# 3. Copiar el código de la aplicación
COPY . .

RUN rm -rf /opt/routers.json
# 4. SOLUCIÓN DEL ERROR:
# Creamos el archivo routers.json COMO ROOT y le damos permiso al usuario 'app'
# Esto evita el error de "Permission denied" y caracteres extraños
RUN echo "[]" > routers.json && chown app:app routers.json

RUN chmod 666 /opt/routers.json
# 5. Configurar el PATH
ENV PATH=/root/.local/bin:$PATH

# 6. Cambiar al usuario limitado (Hacemos esto AL FINAL)
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]