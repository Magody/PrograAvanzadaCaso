# models/dtos.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MenuDTO:
    codigo_plato: str
    nombre_plato: str
    categoria: str
    precio: float

@dataclass
class ClienteDTO:
    id_cliente: int
    nombre_cliente: str

@dataclass
class PedidoDTO:
    codigo_plato: str
    id_cliente: int
    fecha_pedido: datetime
    cantidad: int
    total: float
