from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.models.mikrotik import (
    MikrotikCredentials,
    ConnectionStatus,
    QueueListResponse,
    QueueSearchResponse,
    SystemResources,
    InterfaceStats,
    DhcpLease,
    LogEntry
)
from app.services.mikrotik_client import MikrotikClient

router = APIRouter()


@router.post("/verify-connection", response_model=ConnectionStatus)
async def verify_connection(credentials: MikrotikCredentials):
    """
    Verifica la conexión al RouterOS de MikroTik

    - **host**: Dirección IP o hostname del RouterOS
    - **username**: Usuario de RouterOS
    - **password**: Contraseña de RouterOS
    - **port**: Puerto API de RouterOS (default: 8728)
    - **use_ssl**: Usar SSL para la conexión (default: false)
    - **ssl_verify**: Verificar certificado SSL (default: true)
    - **timeout**: Timeout de conexión en segundos (default: 10)
    """
    try:
        client = MikrotikClient(credentials)
        result = client.verify_connection()

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/queues", response_model=QueueListResponse)
async def get_queues(credentials: MikrotikCredentials):
    """
    Obtiene la lista de todas las queues simples del RouterOS

    Requiere las credenciales de conexión al RouterOS
    """
    try:
        client = MikrotikClient(credentials)
        result = client.get_queues()

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al obtener las queues"
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/queues/search/{queue_name}", response_model=QueueSearchResponse)
async def search_queue(queue_name: str, credentials: MikrotikCredentials):
    """
    Busca una queue específica por su nombre

    - **queue_name**: Nombre de la queue a buscar (case insensitive)
    - Requiere las credenciales de conexión al RouterOS en el body
    """
    try:
        client = MikrotikClient(credentials)
        result = client.search_queue_by_name(queue_name)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/arp")
async def get_arp_list(credentials: MikrotikCredentials):
    """
    Obtiene la lista completa de entradas ARP del RouterOS

    Retorna todas las IPs y direcciones MAC de la tabla ARP
    - Requiere las credenciales de conexión al RouterOS
    """
    try:
        client = MikrotikClient(credentials)
        result = client.get_arp_list()

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Error al obtener la tabla ARP')
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/arp/export")
async def export_arp_to_csv(credentials: MikrotikCredentials):
    """
    Exporta la tabla ARP a formato CSV

    Genera un archivo CSV con todas las IPs y direcciones MAC
    - Requiere las credenciales de conexión al RouterOS
    - Retorna un archivo CSV descargable
    """
    try:
        client = MikrotikClient(credentials)
        result = client.export_arp_to_csv()

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Error al exportar la tabla ARP')
            )

        # Crear respuesta con el CSV
        csv_bytes = BytesIO(result['csv_content'].encode('utf-8'))

        return StreamingResponse(
            csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=arp_table.csv"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/system/resources")
async def get_system_resources(credentials: MikrotikCredentials):
    """
    Obtiene información de recursos del sistema (CPU, Memoria, Disco, etc)
    """
    try:
        client = MikrotikClient(credentials)
        result = client.get_system_resources()

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Error al obtener recursos')
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/interfaces")
async def get_interfaces(credentials: MikrotikCredentials):
    """
    Obtiene estadísticas detalladas de todas las interfaces
    """
    try:
        client = MikrotikClient(credentials)
        result = client.get_interfaces()

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Error al obtener interfaces')
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/dhcp/leases")
async def get_dhcp_leases(credentials: MikrotikCredentials):
    """
    Obtiene la lista de leases DHCP
    """
    try:
        client = MikrotikClient(credentials)
        result = client.get_dhcp_leases()

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Error al obtener leases DHCP')
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/logs")
async def get_logs(credentials: MikrotikCredentials):
    """
    Obtiene los últimos logs del router
    """
    try:
        client = MikrotikClient(credentials)
        result = client.get_logs()

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Error al obtener logs')
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
