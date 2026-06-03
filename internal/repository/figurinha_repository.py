from typing import List, Optional, Protocol

from internal.domain.figurinha import Figurinha


class FigurinhaRepository(Protocol):
    def create(self, figurinha: Figurinha) -> Figurinha:
        ...

    def get_by_id(self, figurinha_id: int) -> Optional[Figurinha]:
        ...

    def list(self, tipo: Optional[str] = None, posicao: Optional[str] = None) -> List[Figurinha]:
        ...

    def update(self, figurinha: Figurinha) -> Figurinha:
        ...

    def delete(self, figurinha_id: int) -> bool:
        ...
