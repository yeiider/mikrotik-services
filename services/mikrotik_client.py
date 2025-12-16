import routeros_api
import csv
from io import StringIO
from typing import List, Optional, Dict, Any
from models.mikrotik import (
    MikrotikCredentials,
    ConnectionStatus,
    Queue,
    QueueListResponse,
    QueueSearchResponse,
    SystemResources,
    InterfaceStats,
    DhcpLease,
    LogEntry
)


class MikrotikClient:
    """Cliente para gestionar conexiones y operaciones con MikroTik RouterOS"""

    def __init__(self, credentials: MikrotikCredentials):
        self.credentials = credentials
        self.connection = None

    def connect(self) -> routeros_api.RouterOsApiPool:
        """Establece conexión con el RouterOS"""
        try:
            port = self.credentials.port
            use_ssl = self.credentials.use_ssl
            ssl_verify = self.credentials.ssl_verify

            if use_ssl:
                # Si se usa SSL y el puerto es el por defecto no seguro, se cambia al puerto seguro por defecto
                if port == 8728:
                    port = 8729
                # Para entornos de desarrollo o internos, es común usar certificados autofirmados
                # no verificables. Forzamos la no verificación si se usa SSL.
                ssl_verify = False

                self.connection = routeros_api.RouterOsApiPool(
                    host=self.credentials.host,
                    username=self.credentials.username,
                    password=self.credentials.password,
                    port=port,
                    use_ssl=True,
                    ssl_verify=ssl_verify,
                    plaintext_login=True
                )
            else:
                self.connection = routeros_api.RouterOsApiPool(
                    host=self.credentials.host,
                    username=self.credentials.username,
                    password=self.credentials.password,
                    port=port,
                    plaintext_login=True
                )
            return self.connection
        except Exception as e:
            raise Exception(f"Error al conectar con RouterOS: {str(e)}")

    def disconnect(self):
        """Cierra la conexión con el RouterOS"""
        if self.connection:
            try:
                self.connection.disconnect()
            except:
                pass
            finally:
                self.connection = None

    def verify_connection(self) -> ConnectionStatus:
        """Verifica la conexión al RouterOS y obtiene información básica"""
        try:
            connection = self.connect()
            api = connection.get_api()

            # Obtener identidad del router
            identity_resource = api.get_resource('/system/identity')
            identity_data = identity_resource.get()
            router_identity = identity_data[0].get('name', 'Unknown') if identity_data else 'Unknown'

            # Obtener versión de RouterOS
            resource_resource = api.get_resource('/system/resource')
            resource_data = resource_resource.get()
            version = resource_data[0].get('version', 'Unknown') if resource_data else 'Unknown'

            self.disconnect()

            return ConnectionStatus(
                success=True,
                message="Conexión exitosa al RouterOS",
                router_identity=router_identity,
                version=version
            )
        except Exception as e:
            return ConnectionStatus(
                success=False,
                message=f"Error de conexión: {str(e)}"
            )

    def get_queues(self) -> QueueListResponse:
        """Obtiene la lista de todas las queues simples"""
        try:
            connection = self.connect()
            api = connection.get_api()

            queue_resource = api.get_resource('/queue/simple')
            queues_data = queue_resource.get()

            queues = []
            for queue_data in queues_data:
                try:
                    queue = Queue(**queue_data)
                    queues.append(queue)
                except Exception as e:
                    # Log pero continúa con las demás queues
                    print(f"Error procesando queue: {e}")
                    continue

            self.disconnect()

            return QueueListResponse(
                success=True,
                count=len(queues),
                queues=queues
            )
        except Exception as e:
            return QueueListResponse(
                success=False,
                count=0,
                queues=[]
            )

    def search_queue_by_name(self, name: str) -> QueueSearchResponse:
        """Busca una queue por su nombre"""
        try:
            connection = self.connect()
            api = connection.get_api()

            queue_resource = api.get_resource('/queue/simple')
            queues_data = queue_resource.get()

            # Buscar queue por nombre (case insensitive)
            found_queue = None
            for queue_data in queues_data:
                if queue_data.get('name', '').lower() == name.lower():
                    found_queue = Queue(**queue_data)
                    break

            self.disconnect()

            if found_queue:
                return QueueSearchResponse(
                    success=True,
                    found=True,
                    queue=found_queue,
                    message=f"Queue '{name}' encontrada"
                )
            else:
                return QueueSearchResponse(
                    success=True,
                    found=False,
                    message=f"Queue '{name}' no encontrada"
                )
        except Exception as e:
            return QueueSearchResponse(
                success=False,
                found=False,
                message=f"Error al buscar queue: {str(e)}"
            )

    def get_arp_list(self) -> Dict[str, Any]:
        """Obtiene la lista completa de entradas ARP"""
        try:
            connection = self.connect()
            api = connection.get_api()

            arp_resource = api.get_resource('/ip/arp')
            arp_data = arp_resource.get()

            arp_entries = []
            for entry in arp_data:
                arp_entries.append({
                    'address': entry.get('address', ''),
                    'mac_address': entry.get('mac-address', ''),
                    'interface': entry.get('interface', ''),
                    'status': entry.get('status', ''),
                    'published': entry.get('published', ''),
                    'invalid': entry.get('invalid', ''),
                    'DHCP': entry.get('DHCP', ''),
                    'dynamic': entry.get('dynamic', ''),
                    'complete': entry.get('complete', '')
                })

            self.disconnect()

            return {
                'success': True,
                'count': len(arp_entries),
                'entries': arp_entries
            }
        except Exception as e:
            return {
                'success': False,
                'count': 0,
                'entries': [],
                'error': str(e)
            }

    def export_arp_to_csv(self) -> Dict[str, Any]:
        """Exporta la tabla ARP a formato CSV"""
        try:
            connection = self.connect()
            api = connection.get_api()

            arp_resource = api.get_resource('/ip/arp')
            arp_data = arp_resource.get()

            # Crear CSV en memoria
            output = StringIO()
            csv_writer = csv.writer(output)

            # Escribir encabezados
            csv_writer.writerow(['IP Address', 'MAC Address', 'Interface', 'Status', 'Published', 'Invalid', 'DHCP', 'Dynamic', 'Complete'])

            # Escribir datos
            for entry in arp_data:
                csv_writer.writerow([
                    entry.get('address', ''),
                    entry.get('mac-address', ''),
                    entry.get('interface', ''),
                    entry.get('status', ''),
                    entry.get('published', ''),
                    entry.get('invalid', ''),
                    entry.get('DHCP', ''),
                    entry.get('dynamic', ''),
                    entry.get('complete', '')
                ])

            self.disconnect()

            csv_content = output.getvalue()
            output.close()

            return {
                'success': True,
                'count': len(arp_data),
                'csv_content': csv_content
            }
        except Exception as e:
            return {
                'success': False,
                'count': 0,
                'csv_content': '',
                'error': str(e)
            }

    def __enter__(self):
        """Context manager support"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.disconnect()

    def get_system_resources(self) -> Dict[str, Any]:
        """Obtiene información de recursos del sistema"""
        try:
            connection = self.connect()
            api = connection.get_api()

            # Obtener recursos (/system/resource)
            resource_res = api.get_resource('/system/resource')
            resource_data = resource_res.get()
            
            # Obtener info del board (/system/routerboard)
            board_res = api.get_resource('/system/routerboard')
            board_data = board_res.get()

            self.disconnect()

            if not resource_data:
                return {'success': False, 'message': 'No se pudo obtener system resource'}

            res = resource_data[0]
            board = board_data[0] if board_data else {}

            resources = SystemResources(
                uptime=res.get('uptime', 'unknown'),
                version=res.get('version', 'unknown'),
                cpu_load=res.get('cpu-load', '0') + '%',
                free_memory=res.get('free-memory', '0'),
                total_memory=res.get('total-memory', '0'),
                free_hdd=res.get('free-hdd-space', '0'),
                total_hdd=res.get('total-hdd-space', '0'),
                board_name=res.get('board-name', 'unknown'),
                model=board.get('model', 'unknown')
            )

            return {
                'success': True,
                'data': resources
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_interfaces(self) -> Dict[str, Any]:
        """Obtiene estadísticas de interfaces"""
        try:
            connection = self.connect()
            api = connection.get_api()

            # Obtener interfaces con stats
            # El endpoint /interface/print devuelve stats por defecto en la API
            # pero a veces es necesario solicitar detalle.
            # En routeros_api .get() suele traer todo.
            interface_res = api.get_resource('/interface')
            interfaces_data = interface_res.get()

            self.disconnect()

            stats_list = []
            for iface in interfaces_data:
                # Convertir strings a int seguros
                def safe_int(v):
                    try: return int(v) if v else 0
                    except: return 0

                stats_list.append(InterfaceStats(
                    name=iface.get('name', 'unknown'),
                    type=iface.get('type', 'unknown'),
                    mtu=iface.get('mtu', '0'),
                    mac_address=iface.get('mac-address', ''),
                    running=iface.get('running') == 'true',
                    disabled=iface.get('disabled') == 'true',
                    tx_byte=safe_int(iface.get('tx-byte')),
                    rx_byte=safe_int(iface.get('rx-byte')),
                    tx_packet=safe_int(iface.get('tx-packet')),
                    rx_packet=safe_int(iface.get('rx-packet')),
                    tx_error=safe_int(iface.get('tx-error')),
                    rx_error=safe_int(iface.get('rx-error')),
                ))

            # Ordenar por tráfico (opcional, pero útil)
            # stats_list.sort(key=lambda x: x.rx_byte + x.tx_byte, reverse=True)

            return {
                'success': True,
                'count': len(stats_list),
                'interfaces': stats_list
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_dhcp_leases(self) -> Dict[str, Any]:
        """Obtiene leases DHCP"""
        try:
            connection = self.connect()
            api = connection.get_api()

            lease_res = api.get_resource('/ip/dhcp-server/lease')
            leases_data = lease_res.get()

            self.disconnect()

            leases = []
            for l in leases_data:
                leases.append(DhcpLease(
                    address=l.get('address', ''),
                    mac_address=l.get('mac-address', ''),
                    server=l.get('server', ''),
                    status=l.get('status', ''),
                    last_seen=l.get('last-seen', ''),
                    host_name=l.get('host-name', ''),
                    dynamic=l.get('dynamic') == 'true'
                ))

            return {
                'success': True,
                'count': len(leases),
                'leases': leases
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_logs(self) -> Dict[str, Any]:
        """Obtiene logs del sistema"""
        try:
            connection = self.connect()
            api = connection.get_api()

            # Obtener logs (limitado para no saturar)
            log_res = api.get_resource('/log')
            # routeros_api no tiene 'limit' nativo en get(), pero devuelve lista.
            # Podríamos filtrar después, o confiar en que no sean demasiados.
            # En producción, cuidado con miles de logs.
            logs_data = log_res.get()

            # Tomar los últimos 100
            logs_data = logs_data[-100:]
            logs_data.reverse() # Más recientes primero

            self.disconnect()

            logs_list = []
            for l in logs_data:
                logs_list.append(LogEntry(
                    id=l.get('.id', ''),
                    time=l.get('time', ''),
                    topics=l.get('topics', ''),
                    message=l.get('message', '')
                ))

            return {
                'success': True,
                'count': len(logs_list),
                'logs': logs_list
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def bind_dhcp_lease(self, mac_address: str, ip_address: str, server: str, comment: str) -> Dict[str, Any]:
        """Amarra una IP a una MAC (Static Lease)"""
        try:
            connection = self.connect()
            api = connection.get_api()
            lease_resource = api.get_resource('/ip/dhcp-server/lease')

            # Buscar lease por MAC (RouterOS usa guiones en los nombres de parámetros)
            leases = lease_resource.get(**{'mac-address': mac_address})

            if leases:
                # Si existe, actualizamos
                lease_id = leases[0].get('.id')

                # Si es dinámico, hacerlo estático
                if leases[0].get('dynamic') == 'true':
                    lease_resource.call('make-static', {'numbers': lease_id})
                    # Recargar ID o datos si es necesario, pero make-static suele mantener el ID

                # Actualizar datos (RouterOS usa guiones en los nombres de parámetros)
                lease_resource.set(**{'.id': lease_id, 'address': ip_address, 'server': server, 'comment': comment})
                action = "updated"
            else:
                # Si no existe, creamos (RouterOS usa guiones en los nombres de parámetros)
                lease_resource.add(**{'mac-address': mac_address, 'address': ip_address, 'server': server, 'comment': comment})
                action = "created"

            self.disconnect()

            return {
                'success': True,
                'message': f"Lease {action} successfully",
                'action': action,
                'mac_address': mac_address,
                'ip_address': ip_address
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def create_simple_queue(self, name: str, target: str, max_limit: str, comment: str) -> Dict[str, Any]:
        """Crea o actualiza una Simple Queue"""
        try:
            connection = self.connect()
            api = connection.get_api()
            queue_resource = api.get_resource('/queue/simple')

            # Buscar queue por nombre
            queues = queue_resource.get(**{'name': name})

            if queues:
                # Actualizar (RouterOS usa guiones en los nombres de parámetros)
                queue_id = queues[0].get('.id')
                queue_resource.set(**{'.id': queue_id, 'target': target, 'max-limit': max_limit, 'comment': comment})
                action = "updated"
            else:
                # Crear (RouterOS usa guiones en los nombres de parámetros)
                queue_resource.add(**{'name': name, 'target': target, 'max-limit': max_limit, 'comment': comment})
                action = "created"

            self.disconnect()

            return {
                'success': True,
                'message': f"Queue {action} successfully",
                'action': action,
                'name': name
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
