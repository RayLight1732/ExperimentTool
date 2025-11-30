from dataclasses import dataclass
from domain.entities.connection_params import ConnectionParams


@dataclass
class TCPConnectionParams(ConnectionParams):
    host: str
    port: str
