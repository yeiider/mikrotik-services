# Guía de Despliegue con Docker

Esta guía explica cómo construir la imagen personalizada, subirla a Docker Hub y desplegarla en un servidor cloud.

## Requisitos Previos
1.  **Docker** y **Docker Compose** instalados.
2.  Cuenta en [Docker Hub](https://hub.docker.com/).
3.  Servidor Cloud (VPS) con Docker instalado.

## 1. Construcción y Ejecución Local

Para probar todo localmente:

```bash
# Construir la imagen y levantar servicios
docker-compose up -d --build
```

Esto iniciará:
- **API**: Puerto 8000
- **InfluxDB**: Puerto 8086

Visita `http://localhost:8000/api/v1/metrics/health` para verificar.

## 2. Subir Imagen a Docker Hub

Para facilitar el despliegue en un servidor, subimos la imagen a un registro público.

1.  **Login en Docker Hub**:
    ```bash
    docker login
    ```

2.  **Etiquetar la Imagen**:
    Reemplaza `tu_usuario` con tu username de Docker Hub.
    ```bash
    docker tag mikrotik-metrics:latest tu_usuario/mikrotik-metrics:v1
    ```

3.  **Subir la Imagen**:
    ```bash
    docker push tu_usuario/mikrotik-metrics:v1
    ```

## 3. Despliegue en Servidor Cloud

En tu servidor remoto:

1.  **Copiar Archivos**:
    Copia `docker-compose.yml`, `routers.json` y `.env` al servidor.

2.  **Configurar Variables**:
    Edita `.env` y `routers.json` con los datos de producción.

3.  **Ajustar docker-compose.yml**:
    Edita el servicio `mikrotik-app` para usar tu imagen remota en lugar de `build: .`
    ```yaml
    services:
      mikrotik-app:
        image: tu_usuario/mikrotik-metrics:v1  # <--- CAMBIO AQUÍ
        # build: .  <--- COMENTAR ESTO
        ...
    ```

4.  **Iniciar Servicios**:
    ```bash
    docker-compose up -d
    ```

## 4. Configuración de InfluxDB
El `docker-compose.yml` ya inicializa InfluxDB con los valores definidos en las variables de entorno `DOCKER_INFLUXDB_INIT_...`.
No necesitas pasos extras si usas el volumen `influxdb2-data`.
