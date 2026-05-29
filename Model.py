from dataclasses import dataclass
from typing import Optional


@dataclass
class Persona:

    nombre: str
    email: str
    estado: str

    cuotas_atrasadas: int = 0

    total: Optional[float] = None

    correo_fiador: Optional[str] = None

    fiador: Optional[str] = None

    @property
    def total_formateado(self) -> str:

        if self.total is None:
            return "0.00"

        return f"{self.total:,.2f}"