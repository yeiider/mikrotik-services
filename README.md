# Mikrotik Metrics Service

Este proyecto es un microservicio de alto rendimiento para recolectar y exponer métricas de routers MikroTik.

## Características

*   Recolecta métricas de múltiples routers MikroTik.
*   Almacena las métricas en InfluxDB.
*   Expone un endpoint de API para consultar las métricas.
*   Seguridad mediante token y lista de IPs permitidas.

## Cómo ejecutar la aplicación

### 1. Usando Docker Compose (Recomendado para desarrollo)

Para levantar la aplicación junto con la base de datos InfluxDB, puedes usar Docker Compose.

**Pre-requisitos:**

*   Docker y Docker Compose instalados.

**Pasos:**

1.  **Clona el repositorio:**

    ```bash
    git clone https://github.com/yeiider/mikrotik-services.git
    cd mikrotik-services
    ```

2.  **Configura las variables de entorno:**

    Crea un archivo `.env` a partir del ejemplo `.env.example` y ajústalo a tus necesidades.

    ```bash
    cp .env.example .env
    ```

    Asegúrate de configurar las siguientes variables en tu archivo `.env`:

    ```
    INFLUXDB_URL=http://localhost:8086
    INFLUXDB_TOKEN=my-super-secret-auth-token
    INFLUXDB_ORG=ispgo
    INFLUXDB_BUCKET=mikrotik_metrics
    SECURITY_TOKEN=your-secret-token
    ALLOWED_IPS=127.0.0.1,192.168.1.100
    ENABLE_TOKEN_CHECK=True
    ENABLE_IP_CHECK=True
    ```

3.  **Configura tus routers:**

    Edita el archivo `routers.json` para agregar la información de tus routers MikroTik.

4.  **Levanta los servicios:**

    ```bash
    docker-compose up --build
    ```

    Esto construirá la imagen de la aplicación y levantará los contenedores de la aplicación y de InfluxDB.

### 2. Usando Docker (Para producción)

Para un despliegue en producción, puedes construir y ejecutar la imagen de Docker directamente.

1.  **Construye la imagen:**

    ```bash
    docker build -t mikrotik-metrics:latest .
    ```

2.  **Ejecuta el contenedor:**

    Puedes pasar las variables de entorno directamente en el comando `docker run`.

    ```bash
    docker run -d \
      -p 8000:8000 \
      --name mikrotik-app \
      -e INFLUXDB_URL=<URL_de_tu_InfluxDB> \
      -e INFLUXDB_TOKEN=<tu_token_de_InfluxDB> \
      -e INFLUXDB_ORG=<tu_org_de_InfluxDB> \
      -e INFLUXDB_BUCKET=<tu_bucket_de_InfluxDB> \
      -e SECURITY_TOKEN=<tu_token_de_seguridad> \
      -e ALLOWED_IPS="<ip1>,<ip2>" \
      -e ENABLE_TOKEN_CHECK=True \
      -e ENABLE_IP_CHECK=True \
      mikrotik-metrics:latest
    ```

    **Nota:** Asegúrate de reemplazar los valores entre `<...>` con tu configuración real.

## Despliegue en un Repositorio

El `Dockerfile` proporcionado está optimizado para producción. Al hacer push a tu repositorio de Git, puedes configurar un pipeline de CI/CD (como GitHub Actions) para que automáticamente construya la imagen de Docker y la despliegue en tu proveedor de nube (AWS, Google Cloud, etc.) o en tu propio servidor.

El pipeline de CI/CD se encargaría de:

1.  Hacer checkout del código.
2.  Construir la imagen de Docker.
3.  Hacer push de la imagen a un registro de contenedores (como Docker Hub, ECR, GCR).
4.  Desplegar la nueva imagen en tu entorno de producción, inyectando las variables de entorno de producción de forma segura (por ejemplo, usando secrets de tu proveedor de nube).