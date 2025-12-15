import asyncio
import logging
import json
import os
from typing import List
from datetime import datetime
from app.services.mikrotik_service import mikrotik_service
from app.core.database import influx_db
from app.models.influx import InfluxPoint
from app.core.config import settings
from app.models.router_config import RouterConfig

logger = logging.getLogger(__name__)

class CollectorService:
    def __init__(self):
        self.is_running = False
        self._task = None
        
    def get_router_inventory(self) -> List[RouterConfig]:
        """Carga el inventario de routers desde JSON o ENV"""
        inventory = []
        try:
            # 1. Try ENV variable
            if settings.ROUTERS_JSON_ENV:
                data = json.loads(settings.ROUTERS_JSON_ENV)
                for item in data:
                    inventory.append(RouterConfig(**item))
                return inventory
            
            # 2. Try JSON file
            if os.path.exists(settings.ROUTERS_JSON_PATH):
                with open(settings.ROUTERS_JSON_PATH, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        inventory.append(RouterConfig(**item))
                return inventory
                
        except Exception as e:
            logger.error(f"Error cargando inventario de routers: {e}")
            
        return inventory

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Collector Service Started")

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Collector Service Stopped")

    async def collect_metrics(self):
        """Ejecución de recolección en paralelo (Fan-out)"""
        try:
            routers = self.get_router_inventory()
            if not routers:
                logger.warning("No routers found in inventory.")
                return

            timestamp = datetime.utcnow()
            logger.info(f"Iniciando recolección para {len(routers)} routers...")
            
            # Fan-out: Create tasks for all routers
            tasks = [
                self._collect_from_router(router, timestamp) 
                for router in routers
            ]
            
            # Wait for all tasks to complete (return_exceptions=True so one failure doesn't stop others)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results (optional, logging summary)
            success_count = 0
            for res in results:
                if not isinstance(res, Exception) and res is True:
                    success_count += 1
                elif isinstance(res, Exception):
                    logger.error(f"Error inesperado en loop de recolección: {res}")
            
            logger.info(f"Ciclo de recolección finalizado. Exitosos: {success_count}/{len(routers)}")
                
        except Exception as e:
            logger.error(f"Error crítico en collector: {e}")

    async def _collect_from_router(self, router: RouterConfig, timestamp: datetime) -> bool:
        """Recolecta métricas de un solo router y escribe en InfluxDB"""
        try:
            queues = await mikrotik_service.get_all_queues_metrics(router)
            points = []
            
            for q in queues:
                # Transformar QueueMetrics a InfluxPoint
                fields = {
                    "upload_bps": q.upload_bps,
                    "download_bps": q.download_bps,
                    "upload_bytes": q.upload_bytes,
                    "download_bytes": q.download_bytes,
                    "dropped_upload": q.dropped_packets_upload,
                    "dropped_download": q.dropped_packets_download
                }
                
                tags = {
                    "user_name": q.name,
                    "target_ip": q.target_ip,
                    "plan_profile": q.plan_profile,
                    "router_alias": router.alias # [NEW] Tag requirement
                }
                
                point = InfluxPoint(
                    measurement="mikrotik_traffic",
                    tags=tags,
                    fields=fields,
                    time=timestamp
                )
                points.append(point)
            
            if points:
                influx_db.write_batch(points)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error recolectando de router '{router.alias}' ({router.host}): {e}")
            return e

    async def _loop(self):
        while self.is_running:
            await self.collect_metrics()
            await asyncio.sleep(settings.COLLECTOR_INTERVAL_SECONDS)

# Global Instance
collector_service = CollectorService()
