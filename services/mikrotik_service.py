import routeros_api
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging
from models.mikrotik import QueueMetrics
from models.router_config import RouterConfig

# Configurar logger para ver errores reales en consola
logger = logging.getLogger(__name__)


class MikrotikService:
    def __init__(self):
        # 20 workers es bueno, pero cuidado si tienes muchos routers,
        # no satures la CPU del servidor donde corre Docker.
        self.executor = ThreadPoolExecutor(max_workers=20)

    def _parse_queue_to_metrics(self, queue_data: dict) -> Optional[QueueMetrics]:
        """Transforma datos crudos de Mikrotik a QueueMetrics"""
        try:
            name = queue_data.get('name')
            target = queue_data.get('target')

            # MikroTik devuelve strings tipo "1234/5678"
            bytes_str = queue_data.get('bytes', '0/0')
            packets_str = queue_data.get('packets', '0/0')
            dropped_str = queue_data.get('dropped', '0/0')
            rate_str = queue_data.get('rate', '0/0')  # Ojo: A veces MikroTik no envía 'rate' si es 0

            def split_pair(s):
                if not s: return 0, 0
                try:
                    parts = s.split('/')
                    return int(parts[0]), int(parts[1])
                except:
                    return 0, 0

            up_bytes, down_bytes = split_pair(bytes_str)
            up_packets, down_packets = split_pair(packets_str)
            up_dropped, down_dropped = split_pair(dropped_str)
            up_bps, down_bps = split_pair(rate_str)

            # Limpieza de IP (quitar máscara /32 si existe)
            target_ip = target.split('/')[0] if target else "unknown"

            return QueueMetrics(
                name=name,
                target_ip=target_ip,
                plan_profile="unknown",  # Podrías usar queue_data.get('comment') si ahí pones el plan
                upload_bps=up_bps,
                download_bps=down_bps,
                upload_bytes=up_bytes,  # InfluxDB calculará el consumo por hora con esto
                download_bytes=down_bytes,  # InfluxDB calculará el consumo por hora con esto
                packet_rate_upload=0,  # DEPRECADO: Usar contadores totales abajo
                packet_rate_download=0,  # DEPRECADO: Usar contadores totales abajo
                dropped_packets_upload=up_dropped,
                dropped_packets_download=down_dropped,

                # CAMPOS NUEVOS RECOMENDADOS (Asegúrate de agregarlos a tu modelo QueueMetrics)
                total_packets_upload=up_packets,  # Nuevo campo para calcular PPS en Influx
                total_packets_download=down_packets  # Nuevo campo para calcular PPS en Influx
            )
        except Exception as e:
            logger.error(f"Error parseando cola {queue_data.get('name', '?')}: {e}")
            return None

    def _fetch_queues_sync(self, router_config: RouterConfig) -> List[QueueMetrics]:
        """Sincrónico: Conecta y extrae colas"""
        connection = None
        metrics = []
        try:
            port = router_config.port
            # Ajuste automático de puerto SSL si es necesario
            if router_config.use_ssl and port == 8728:
                port = 8729

            connection = routeros_api.RouterOsApiPool(
                host=router_config.host,
                username=router_config.username,  # Asegúrate que tu modelo usa 'user' o 'username'
                password=router_config.password,
                port=port,
                use_ssl=router_config.use_ssl,
                plaintext_login=True  # Necesario para versiones nuevas de RouterOS (6.43+) sin SSL
            )

            api = connection.get_api()

            # Obtener recurso. IMPORTANTE: No hace la llamada a red todavía.
            queue_resource = api.get_resource('/queue/simple')

            # .get() hace el '/queue/simple/print'.
            # Para 5000 usuarios, esto es pesado.
            queues_data = queue_resource.get()

            for q in queues_data:
                m = self._parse_queue_to_metrics(q)
                if m:
                    metrics.append(m)

            return metrics

        except Exception as e:
            logger.error(f"Error conectando a router {router_config.alias} ({router_config.host}): {e}")
            # Retornamos lista vacía en lugar de romper todo el proceso,
            # así los otros routers sí se procesan.
            return []

        finally:
            if connection:
                connection.disconnect()

    async def get_all_queues_metrics(self, router_config: RouterConfig) -> List[QueueMetrics]:
        """Asíncrono: Wrapper para no bloquear el event loop"""
        loop = asyncio.get_running_loop()
        # Esto envía la tarea pesada al ThreadPool
        return await loop.run_in_executor(self.executor, self._fetch_queues_sync, router_config)


mikrotik_service = MikrotikService()