from dataclasses import dataclass
from typing import Optional


@dataclass
class Persona:

    nombre: str
    email: str
    estado: str

    cuotas_atrasadas: int = 0

    fecha_proximo_pago: Optional[str] = None

    total: Optional[str] = None

    correo_fiador: Optional[str] = None

    fiador: Optional[str] = None