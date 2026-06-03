from dataclasses import dataclass
from datetime import datetime


VALID_TYPES = {"comum", "brilhante", "legends_ouro", "legends_bronze"}
VALID_POSITIONS = {"Goleiro", "Zagueiro", "Meio-campista", "Atacante"}


@dataclass
class Figurinha:
    id: int
    numero: str
    tipo: str
    posicao: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero": self.numero,
            "tipo": self.tipo,
            "posicao": self.posicao,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
