from fastapi import APIRouter
from services.mikrotik_service import mikrotik_service
from services.collector_service import collector_service
from core.database import influx_db
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    """Verifica estado de servicios dependientes y conectividad con todos los routers"""
    influx_status = influx_db.check_health()
    
    # Check all routers
    routers = collector_service.get_router_inventory()
    mikrotik_results = {}
    
    if routers:
        tasks = [mikrotik_service.check_connection(r) for r in routers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for router, res in zip(routers, results):
            status = "connected" if res is True else "disconnected"
            mikrotik_results[router.alias] = status
    else:
        mikrotik_results["error"] = "No routers in inventory"

    # Status is healthy if Influx is OK and at least one router is reachable (or depending on policy)
    # For now, if Influx is UP, we say healthy, but report individual router status.
    status = "healthy" if influx_status else "degraded"
    
    return {
        "status": status,
        "components": {
            "influxdb": "connected" if influx_status else "disconnected",
            "routers": mikrotik_results
        }
    }
