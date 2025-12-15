# API Reference: Mikrotik Metrics Service

Base URL: `http://localhost:8000/api/v1`

## 1. Health & Status

### Check Service Health
Verifica la conectividad con componentes dependientes (InfluxDB y Routers).

- **Method**: `GET`
- **Endpoint**: `/metrics/health`
- **Response**:
  ```json
  {
    "status": "healthy",
    "components": {
      "influxdb": "connected",
      "routers": {
        "guachene": "connected",
        "nodo_norte": "disconnected"
      }
    }
  }
  ```

## 2. Metrics & Data

### Get User Usage History
Obtiene el historial de consumo de ancho de banda para un cliente específico.

- **Method**: `GET`
- **Endpoint**: `/metrics/user/{username}/history`
- **Query Params**:
  - `range` (opcional): Ventana de tiempo (ej: `1h`, `24h`, `7d`, `30d`). Default: `1h`.
- **Response**:
  ```json
  {
    "data": [
      {
        "time": "2025-12-12T20:00:00Z",
        "field": "upload_bps",
        "value": 1500000
      },
      {
        "time": "2025-12-12T20:00:00Z",
        "field": "download_bps",
        "value": 5000000
      }
    ]
  }
  ```

### Get Current Network Load
Obtiene la carga total agregada de la red (suma de todo el tráfico de usuarios) en los últimos 5 minutos.

- **Method**: `GET`
- **Endpoint**: `/metrics/network/current_load`
- **Response**:
  ```json
  {
    "current_load": {
      "upload_bps": 45000000,
      "download_bps": 120000000
    }
  }
  ```

## 3. Operations

### Force Manual Sync
Fuerza una ejecución inmediata del proceso de recolección de métricas en segundo plano. Útil después de cambios de configuración.

- **Method**: `POST`
- **Endpoint**: `/metrics/sync/force`
- **Response**:
  ```json
  {
    "message": "Recolección iniciada en segundo plano"
  }
  ```
