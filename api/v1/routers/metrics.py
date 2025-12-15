from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.collector_service import collector_service
from core.database import influx_db
from typing import List, Dict, Any

router = APIRouter()

@router.post("/sync/force")
async def force_sync(background_tasks: BackgroundTasks):
    """Forza una recolección manual de métricas"""
    background_tasks.add_task(collector_service.collect_metrics)
    return {"message": "Recolección iniciada en segundo plano"}

@router.get("/user/{username}/history")
async def get_user_history(username: str, range: str = "1h"):
    """
    Obtiene historial de consumo para un usuario.
    Range ejemplos: 1h, 24h, 7d
    """
    query = f'''
    from(bucket: "{influx_db.bucket}")
      |> range(start: -{range})
      |> filter(fn: (r) => r["_measurement"] == "mikrotik_traffic")
      |> filter(fn: (r) => r["user_name"] == "{username}")
      |> filter(fn: (r) => r["_field"] == "upload_bps" or r["_field"] == "download_bps")
      |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
      |> yield(name: "mean")
    '''
    
    try:
        tables = influx_db.query_api.query(query, org=influx_db.client.org)
        result = []
        for table in tables:
            for record in table.records:
                result.append({
                    "time": record.get_time(),
                    "field": record.get_field(),
                    "value": record.get_value()
                })
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/network/current_load")
async def get_network_load():
    """Obtiene la carga total de la red actual (Suma de todos los usuarios)"""
    query = f'''
    from(bucket: "{influx_db.bucket}")
      |> range(start: -5m)
      |> filter(fn: (r) => r["_measurement"] == "mikrotik_traffic")
      |> filter(fn: (r) => r["_field"] == "upload_bps" or r["_field"] == "download_bps")
      |> last()
      |> group(columns: ["_field"])
      |> sum()
    '''
    
    try:
        tables = influx_db.query_api.query(query, org=influx_db.client.org)
        load = {"upload_bps": 0, "download_bps": 0}
        
        for table in tables:
            for record in table.records:
                field = record.get_field()
                if field in load:
                    load[field] = record.get_value()
                    
        return {"current_load": load}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
