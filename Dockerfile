FROM python:3.10-slim as builder
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=builder /root/.local /root/.local
COPY . .

# ESTA es la única línea necesaria para el archivo interno.
# NO agregues nada de /opt ni sudo aquí.
RUN echo "[]" > routers.json && chown app:app routers.json

ENV PATH=/root/.local/bin:$PATH
USER app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]