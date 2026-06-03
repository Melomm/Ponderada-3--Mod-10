from datetime import datetime, timezone
from typing import Dict, List, Optional

from internal.domain.figurinha import Figurinha, VALID_POSITIONS, VALID_TYPES
from internal.errors.errors import (
    ErrFigureNotFound,
    ErrInvalidPosition,
    ErrInvalidType,
    ErrMissingField,
    ErrReadOnlyField,
)
from internal.repository.figurinha_repository import FigurinhaRepository


class FigurinhaService:
    def __init__(self, repository: FigurinhaRepository):
        self.repository = repository

    def create(self, data: Dict) -> Figurinha:
        self._reject_read_only_fields(data)
        self._validate_required_fields(data)
        self._validate_type(data["tipo"])
        self._validate_position(data["posicao"])

        now = self._now()
        figurinha = Figurinha(
            id=0,
            numero=data["numero"].strip(),
            tipo=data["tipo"],
            posicao=data["posicao"],
            created_at=now,
            updated_at=now,
        )

        return self.repository.create(figurinha)

    def list(
        self, tipo: Optional[str] = None, posicao: Optional[str] = None
    ) -> List[Figurinha]:
        if tipo is not None:
            self._validate_type(tipo)

        if posicao is not None:
            self._validate_position(posicao)

        return self.repository.list(tipo=tipo, posicao=posicao)

    def get_by_id(self, figurinha_id: int) -> Figurinha:
        figurinha = self.repository.get_by_id(figurinha_id)
        if figurinha is None:
            raise ErrFigureNotFound()
        return figurinha

    def update(self, figurinha_id: int, data: Dict) -> Figurinha:
        current = self.repository.get_by_id(figurinha_id)
        if current is None:
            raise ErrFigureNotFound()

        self._reject_read_only_fields(data)
        self._validate_required_fields(data)
        self._validate_type(data["tipo"])
        self._validate_position(data["posicao"])

        updated = Figurinha(
            id=current.id,
            numero=data["numero"].strip(),
            tipo=data["tipo"],
            posicao=data["posicao"],
            created_at=current.created_at,
            updated_at=self._now(),
        )

        return self.repository.update(updated)

    def delete(self, figurinha_id: int) -> None:
        removed = self.repository.delete(figurinha_id)
        if not removed:
            raise ErrFigureNotFound()

    def _validate_required_fields(self, data: Dict) -> None:
        for field in ("numero", "tipo", "posicao"):
            value = data.get(field)
            if value is None or str(value).strip() == "":
                raise ErrMissingField(field)

    def _validate_type(self, tipo: str) -> None:
        if tipo not in VALID_TYPES:
            raise ErrInvalidType()

    def _validate_position(self, posicao: str) -> None:
        if posicao not in VALID_POSITIONS:
            raise ErrInvalidPosition()

    def _reject_read_only_fields(self, data: Dict) -> None:
        for field in ("id", "created_at", "updated_at"):
            if field in data:
                raise ErrReadOnlyField(field)

    def _now(self) -> datetime:
        return datetime.now(timezone.utc).replace(microsecond=0)
