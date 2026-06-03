from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from internal.errors.errors import (
    DomainError,
    ErrFigureNotFound,
    ErrInvalidPosition,
    ErrInvalidType,
    ErrMissingField,
    ErrReadOnlyField,
)


class FigurinhaRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    numero: Optional[str] = None
    tipo: Optional[str] = None
    posicao: Optional[str] = None


def build_app(service) -> FastAPI:
    app = FastAPI(title="API de Figurinhas da Copa 2026")

    @app.post("/figurinha", status_code=201)
    async def create_figurinha(request: FigurinhaRequest):
        try:
            figurinha = service.create(request.model_dump())
            return figurinha.to_dict()
        except DomainError as error:
            return _domain_error_response(error)

    @app.get("/figurinha")
    async def list_figurinhas(tipo: Optional[str] = None, posicao: Optional[str] = None):
        try:
            figurinhas = service.list(tipo=tipo, posicao=posicao)
            return [figurinha.to_dict() for figurinha in figurinhas]
        except DomainError as error:
            return _domain_error_response(error)

    @app.get("/figurinha/{figurinha_id}")
    async def get_figurinha(figurinha_id: int):
        try:
            figurinha = service.get_by_id(figurinha_id)
            return figurinha.to_dict()
        except DomainError as error:
            return _domain_error_response(error)

    @app.put("/figurinha/{figurinha_id}")
    async def update_figurinha(figurinha_id: int, request: FigurinhaRequest):
        try:
            figurinha = service.update(figurinha_id, request.model_dump())
            return figurinha.to_dict()
        except DomainError as error:
            return _domain_error_response(error)

    @app.delete("/figurinha/{figurinha_id}", status_code=204)
    async def delete_figurinha(figurinha_id: int):
        try:
            service.delete(figurinha_id)
            return None
        except DomainError as error:
            return _domain_error_response(error)

    @app.get("/pacotinho")
    async def open_pack():
        return service.open_pack()

    return app


def _domain_error_response(error: DomainError) -> JSONResponse:
    status = 400
    if isinstance(error, ErrFigureNotFound):
        status = 404
    elif isinstance(
        error,
        (ErrInvalidType, ErrInvalidPosition, ErrMissingField, ErrReadOnlyField),
    ):
        status = 400

    return JSONResponse(status_code=status, content={"error": str(error)})
