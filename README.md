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

## Despliegue en Portainer

Mencionas que estás usando Portainer.io. Aquí te explico la forma correcta de desplegar tu aplicación, y por qué **no es una buena práctica hacer `git pull` dentro del `Dockerfile`**.

> **¿Por qué no usar `git pull` en el `Dockerfile`?**
>
> 1.  **Builds no reproducibles:** El código fuente podría cambiar entre builds, incluso si el `Dockerfile` es idéntico, haciendo que la misma versión de la imagen tenga código diferente.
> 2.  **Cache de Docker ineficiente:** Docker no podría cachear las capas de manera efectiva, ralentizando los builds.
> 3.  **Riesgos de seguridad:** Necesitarías incluir credenciales de Git (tokens o claves SSH) en el proceso de build, lo cual es un riesgo de seguridad.

### Método 1: Despliegue Manual (Build > Push > Deploy)

Este es el flujo de trabajo más común y recomendado si no quieres conectar tu Git directamente a Portainer.

1.  **Construye la imagen de Docker:**

    En tu máquina local, asegúrate de tener el código más reciente y ejecuta:

    ```bash
    # Reemplaza 'tu-usuario' con tu usuario de Docker Hub u otro registro
    docker build -t tu-usuario/mikrotik-metrics:latest .
    ```

2.  **Sube la imagen a un registro de contenedores:**

    Necesitas un lugar para almacenar tu imagen, como Docker Hub, GitHub Container Registry, etc.

    ```bash
    # Inicia sesión en tu registro (ej. Docker Hub)
    docker login
    
    # Sube la imagen
    docker push tu-usuario/mikrotik-metrics:latest
    ```

3.  **Despliega en Portainer:**

    *   En Portainer, ve a **Containers** y haz clic en **+ Add container**.
    *   **Name:** Dale un nombre a tu contenedor (ej. `mikrotik-app`).
    *   **Image:** Escribe el nombre de la imagen que subiste (ej. `tu-usuario/mikrotik-metrics:latest`). Asegúrate de que Portainer tenga acceso a este registro.
    *   **Ports:** Mapea el puerto `8000` del contenedor al puerto que desees en tu host.
    *   **Env:** En la sección **Advanced container settings > Env**, agrega todas las variables de entorno que necesita tu aplicación (`INFLUXDB_URL`, `INFLUXDB_TOKEN`, etc.).
    *   Haz clic en **Deploy the container**.

### Método 2: Despliegue Automatizado con Git (Stacks de Portainer)

Este método es el que buscas para un despliegue basado en repositorio. Portainer se conectará a tu repositorio de Git y desplegará la aplicación usando el archivo `docker-compose.yml`.

1.  **Prepara tu Repositorio:**

    Asegúrate de que tu `docker-compose.yml` esté configurado para construir la imagen y que todas las variables de entorno estén listas para ser inyectadas por Portainer. El `docker-compose.yml` que te he proporcionado ya está casi listo para esto.

2.  **Crea un Stack en Portainer:**

    *   En Portainer, ve a **Stacks** y haz clic en **+ Add stack**.
    *   **Name:** Dale un nombre a tu stack (ej. `mikrotik-stack`).
    *   **Build method:** Selecciona **Git Repository**.
    *   **Repository URL:** Pega la URL de tu repositorio de GitHub: `https://github.com/yeiider/mikrotik-services.git`.
    *   **Compose path:** Asegúrate de que la ruta a tu `docker-compose.yml` sea correcta (normalmente `docker-compose.yml` si está en la raíz).
    *   **Environment variables:** Aquí es donde configuras las variables de entorno de forma segura. Haz clic en **Advanced mode** y pega el contenido de tu archivo `.env` o define las variables una por una. Estas variables sobreescribirán cualquier valor en el `.env` del repositorio.

3.  **Despliega el Stack:**

    *   Haz clic en **Deploy the stack**.
    *   Portainer clonará tu repositorio, usará `docker-compose` para construir la imagen de la aplicación (porque `build: .` está en el `docker-compose.yml`) y desplegará los servicios.

4.  **(Opcional) Configura Webhooks para Despliegue Automático:**

    *   En la configuración de tu Stack en Portainer, puedes encontrar una URL de **webhook**.
    *   Ve a tu repositorio de GitHub, a **Settings > Webhooks**, y agrega un nuevo webhook pegando la URL de Portainer.
    *   Ahora, cada vez que hagas `git push` a tu rama `main`, Portainer automáticamente se actualizará y desplegará la última versión de tu aplicación.
