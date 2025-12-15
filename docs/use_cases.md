# Casos de Uso del Microservicio de Métricas Mikrotik

Este documento describe los casos de uso principales para el microservicio de recolección de métricas.

## 1. Recolección Automática de Métricas (Background Worker)
**Actor**: Sistema (Collector Service)
**Descripción**: Un proceso en segundo plano se conecta al router Mikrotik cada 5 minutos (configurable), extrae estadísticas de todas las `Simple Queues` y las almacena en InfluxDB.
**Flujo**:
1. El servicio inicia (`lifespan` startup).
2. Se activa el loop del `CollectorService`.
3. Conexión asíncrona al Mikrotik.
4. Extracción de:
   - Upload/Download rate (bps)
   - Contadores de Bytes (Total volumen)
   - Contadores de Paquetes
   - Paquetes Descartados (Dropped)
5. Transformación de datos a puntos de InfluxDB con tags: `user_name`, `target_ip`, `plan_profile`.
6. Escritura en lote (Batch Write) a InfluxDB.

## 2. Visualización de Historial de Cliente
**Actor**: PHP Frontend (Portal Administrativo)
**Descripción**: El sistema legacy consulta la API para renderizar gráficos de consumo de un usuario específico.
**Endpoint**: `GET /api/v1/metrics/user/{username}/history?range=24h`
**Beneficio**: La consulta es instantánea ya que lee de InfluxDB, no satura al router Mikrotik.

## 3. Monitoreo de Salud de la Red
**Actor**: Dashboard de Monitoreo / NOC
**Descripción**: Verificar la carga total de la red en tiempo real.
**Endpoint**: `GET /api/v1/metrics/network/current_load`
**Resultado**: Devuelve la suma total de upload/download de todos los usuarios activos en los últimos 5 minutos.

## 4. Sincronización Manual
**Actor**: Soporte Técnico
**Descripción**: Un técnico realiza un cambio de plan y necesita ver el efecto inmediato sin esperar 5 minutos.
**Endpoint**: `POST /api/v1/metrics/sync/force`
**Resultado**: Dispara la recolección inmediatamente en background.

## 5. Health Check
**Actor**: Balanceador de Carga / Kubernetes / Sistema de Monitoreo
**Descripción**: Verificar que el servicio y sus dependencias (Mikrotik, InfluxDB) estén operativos.
**Endpoint**: `GET /api/v1/metrics/health`
