# Flujo de Provisionamiento de Mikrotik

Este documento describe el flujo para amarrar una IP a una dirección MAC y asignar un Simple Queue para controlar el ancho de banda.

## Flujo Completo

El flujo ideal consiste en:
1. Identificar la MAC del cliente y la IP que se le desea asignar.
2. Definir el plan de ancho de banda (Create Simple Queue).
3. Ejecutar ambas operaciones en una sola transacción.

Para esto, se ha creado el endpoint `/api/v1/provision/simple-flow`.

### Endpoint: `/api/v1/provision/simple-flow`

Este endpoint orquesta ambos pasos:
1. **Bind DHCP Lease**: Busca si existe un lease con la MAC dada. Si existe, lo actualiza a estático con la IP dada. Si no, crea uno nuevo estático.
2. **Create Simple Queue**: Crea o actualiza una cola simple con el nombre dado y los límites de ancho de banda.

#### Ejemplo de Uso

**Método**: `POST`
**URL**: `http://localhost:8000/api/v1/provision/simple-flow`

**Body**:
```json
{
  "lease_request": {
    "mac_address": "00:11:22:33:44:55",
    "ip_address": "192.168.88.200",
    "server": "dhcp1",
    "comment": "Cliente Juan Perez",
    "credentials": {
      "host": "192.168.88.1",
      "username": "admin",
      "password": "password",
      "port": 8728,
      "use_ssl": false
    }
  },
  "queue_request": {
    "name": "Cliente-Juan-Perez",
    "target": "192.168.88.200",
    "max_limit": "10M/20M", 
    "comment": "Plan 20 Megas",
    "credentials": {
      "host": "192.168.88.1",
      "username": "admin",
      "password": "password",
      "port": 8728,
      "use_ssl": false
    }
  }
}
```

> **Nota**: `max_limit` es "upload/download".

## Endpoints Individuales

Si se desea ejecutar los pasos por separado:

### 1. Amarrar IP (Bind DHCP Lease)
**Endpoint**: `/api/v1/dhcp/bind`
**Body**: `BindDhcpLeaseRequest` (ver esquema en Swagger UI)

### 2. Crear Cola (Create Simple Queue)
**Endpoint**: `/api/v1/queues/create`
**Body**: `CreateSimpleQueueRequest` (ver esquema en Swagger UI)
