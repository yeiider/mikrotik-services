from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MikrotikCredentials(BaseModel):
    host: str
    username: str
    password: str
    port: int = 8728
    use_ssl: bool = False
    ssl_verify: bool = False

class ConnectionStatus(BaseModel):
    success: bool
    message: str
    router_identity: Optional[str] = None
    version: Optional[str] = None

class Queue(BaseModel):
    """Modelo base de una Queue Simple de Mikrotik"""
    name: str = Field(..., alias="name")
    target: str = Field(..., alias="target")
    max_limit: Optional[str] = Field(None, alias="max-limit")
    rate: Optional[str] = Field(None, alias="rate")
    bytes: Optional[str] = Field(None, alias="bytes")
    packets: Optional[str] = Field(None, alias="packets")
    dropped: Optional[str] = Field(None, alias="dropped")
    comment: Optional[str] = Field(None, alias="comment")
    disabled: Optional[str] = Field(None, alias="disabled")

    class Config:
        populate_by_name = True


class QueueMetrics(BaseModel):
    name: str
    target_ip: str
    plan_profile: str
    upload_bps: int
    download_bps: int
    upload_bytes: int  # Counter acumulativo
    download_bytes: int  # Counter acumulativo
    dropped_packets_upload: int
    dropped_packets_download: int

    # Nuevos campos para calcular PPS (Packets Per Second)
    total_packets_upload: int = 0
    total_packets_download: int = 0

    # Estos puedes mantenerlos en 0 o quitarlos si no los calculas en Python
    packet_rate_upload: int = 0
    packet_rate_download: int = 0

class QueueListResponse(BaseModel):
    success: bool
    count: int
    queues: List[Queue]

class QueueSearchResponse(BaseModel):
    success: bool
    found: bool
    queue: Optional[Queue] = None
    message: str


class SystemResources(BaseModel):
    uptime: str
    version: str
    cpu_load: str
    free_memory: str
    total_memory: str
    free_hdd: str
    total_hdd: str
    board_name: str
    model: str


class InterfaceStats(BaseModel):
    name: str # name
    type: str # type
    mtu: str # mtu
    mac_address: str # mac-address
    running: bool # running
    disabled: bool # disabled
    tx_byte: int = 0 # tx-byte
    rx_byte: int = 0 # rx-byte
    tx_packet: int = 0 # tx-packet
    rx_packet: int = 0 # rx-packet
    tx_error: int = 0 # tx-error
    rx_error: int = 0 # rx-error


class DhcpLease(BaseModel):
    address: str # address
    mac_address: str # mac-address
    server: str # server
    status: str # status
    last_seen: str = "" # last-seen
    host_name: str = "" # host-name
    dynamic: bool = False # dynamic


class LogEntry(BaseModel):
    id: str # .id
    time: str # time
    topics: str # topics
    message: str # message


class BindDhcpLeaseRequest(BaseModel):
    mac_address: str
    ip_address: str
    server: str
    comment: Optional[str] = None
    credentials: MikrotikCredentials


class CreateSimpleQueueRequest(BaseModel):
    name: str
    target: str
    max_limit: str  # Format: "upload/download" e.g., "10M/10M"
    comment: Optional[str] = None
    credentials: MikrotikCredentials


class ProvisionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

