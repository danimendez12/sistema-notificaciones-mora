from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class Persona(ABC):
    nombre: str
    email: str
    estado:str
    coutoas_atrasadas: int = field(default=0)
    fecha_proximo_pago: str = field(default="")
    rango_mora: str = field(default="")
    correo_fiador: str = field(default="")