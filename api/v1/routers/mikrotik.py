from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from io import BytesIO
from models.mikrotik import (
    MikrotikCredentials,
    ConnectionStatus,
    QueueListResponse,
    QueueSearchResponse,
    SystemResources,
    InterfaceStats,
    DhcpLease,
    LogEntry,
    BindDhcpLeaseRequest,
    CreateSimpleQueueRequest,
    ProvisionResponse,
    ProvisionFlowRequest
)
from services.mikrotik_client import MikrotikClient

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


@router.post("/dhcp/servers")
async def get_dhcp_servers(credentials: MikrotikCredentials):
    """
    Obtiene la lista de servidores DHCP disponibles
    """
    try:
        client = MikrotikClient(credentials)
        result = client.get_dhcp_servers()

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Error al obtener servidores DHCP')
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


@router.get("/health")
async def health_check():
    """
    Endpoint de health check para verificar que el servicio está activo
    """
    return {
        "status": "healthy",
        "service": "mikrotik-api",
        "version": "1.0.0"
    }


@router.post("/dhcp/bind", response_model=ProvisionResponse)
async def bind_dhcp_lease(request: BindDhcpLeaseRequest):
    """
    Amarra una IP a una MAC (Static Lease)
    """
    try:
        client = MikrotikClient(request.credentials)
        result = client.bind_dhcp_lease(
            mac_address=request.mac_address,
            ip_address=request.ip_address,
            server=request.server,
            comment=request.comment
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Error al hacer bind del lease')
            )

        return ProvisionResponse(
            success=True,
            message=result['message'],
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/queues/create", response_model=ProvisionResponse)
async def create_simple_queue(request: CreateSimpleQueueRequest):
    """
    Crea o actualiza una Simple Queue
    """
    try:
        client = MikrotikClient(request.credentials)
        result = client.create_simple_queue(
            name=request.name,
            target=request.target,
            max_limit=request.max_limit,
            comment=request.comment
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Error al crear la queue')
            )

        return ProvisionResponse(
            success=True,
            message=result['message'],
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.post("/provision/simple-flow", response_model=ProvisionResponse)
async def provision_simple_flow(request: ProvisionFlowRequest):
    """
    Flujo completo de provisionamiento: Amarrar IP a MAC y crear Simple Queue

    Parámetros:
    - credentials: Credenciales del RouterOS
    - mac_address: MAC address del dispositivo (ej: "b4:64:15:02:4a:de")
    - ip_address: IP a asignar (ej: "172.19.1.73")
    - server: Nombre del servidor DHCP (opcional, ej: "vlan801")
    - queue_name: Nombre de la queue (ej: "cliente_4")
    - max_limit: Límite de velocidad upload/download (ej: "500M/500M")
    - comment: Comentario opcional (ej: "JULIAN DAVID CAMPO ZUNIGA")
    """
    try:
        client = MikrotikClient(request.credentials)

        # 1. Bind DHCP Lease
        bind_result = client.bind_dhcp_lease(
            mac_address=request.mac_address,
            ip_address=request.ip_address,
            server=request.server,
            comment=request.comment
        )

        if not bind_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fallo en bind lease: {bind_result.get('message')}"
            )

        # 2. Create Simple Queue
        queue_result = client.create_simple_queue(
            name=request.queue_name,
            target=request.ip_address,  # El target es la IP asignada
            max_limit=request.max_limit,
            comment=request.comment
        )

        if not queue_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fallo en create queue: {queue_result.get('message')}"
            )

        return ProvisionResponse(
            success=True,
            message="Provisionamiento completado exitosamente",
            data={
                "lease": bind_result,
                "queue": queue_result
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
