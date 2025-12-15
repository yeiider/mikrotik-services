# Documentación de Nuevas APIs MikroTik

Esta documentación detalla los nuevos endpoints disponibles para obtener información avanzada de routers MikroTik.

## Base URL
`/api/v1/mikrotik`

## Autenticación
Todos los endpoints requieren un objeto JSON con las credenciales del router en el cuerpo de la petición.

**Estructura de Credenciales:**
```json
{
  "host": "192.168.88.1",
  "username": "admin",
  "password": "password",
  "port": 8728,
  "use_ssl": false
}
```

---

## 1. Recursos del Sistema
Obtiene información vital sobre el estado del hardware y software del router.

- **Endpoint:** `/system/resources`
- **Método:** `POST`
- **Uso:** Monitoreo de salud del dispositivo (CPU, Memoria, Disco).

**Ejemplo de Respuesta:**
```json
{
  "success": true,
  "data": {
    "uptime": "1w2d3h",
    "version": "7.10.2",
    "cpu_load": "15%",
    "free_memory": "25000000",
    "total_memory": "64000000",
    "free_hdd": "100000000",
    "total_hdd": "128000000",
    "board_name": "CHR",
    "model": "CHR"
  }
}
```

## 2. Estadísticas de Interfaces
Obtiene detalles de tráfico y estado de todas las interfaces de red.

- **Endpoint:** `/interfaces`
- **Método:** `POST`
- **Uso:** Análisis de tráfico, detección de errores en puertos, verificar estado de enlaces.

**Ejemplo de Respuesta:**
```json
{
  "success": true,
  "count": 2,
  "interfaces": [
    {
      "name": "ether1",
      "type": "ether",
      "mtu": "1500",
      "mac_address": "00:00:00:00:00:01",
      "running": true,
      "disabled": false,
      "tx_byte": 123456,
      "rx_byte": 654321
    }
  ]
}
```

## 3. Leases DHCP
Lista todos los dispositivos que han obtenido IP mediante DHCP.

- **Endpoint:** `/dhcp/leases`
- **Método:** `POST`
- **Uso:** Identificar dispositivos conectados, reservas de IP, auditar conexiones.

**Ejemplo de Respuesta:**
```json
{
  "success": true,
  "count": 1,
  "leases": [
    {
      "address": "192.168.88.10",
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "server": "dhcp1",
      "status": "bound",
      "host_name": "iPhone-User"
    }
  ]
}
```

## 4. Logs del Sistema
Obtiene los registros de eventos más recientes del router.

- **Endpoint:** `/logs`
- **Método:** `POST`
- **Uso:** Depuración de errores, auditoría de seguridad, monitoreo de cambios de configuración.

**Ejemplo de Respuesta:**
```json
{
  "success": true,
  "count": 50,
  "logs": [
    {
      "time": "jan/01/2024 10:00:00",
      "topics": "system,info",
      "message": "router rebooted"
    }
  ]
}
```
