from internal.database.sqlite import connect, migrate
from internal.handler.http_handler import build_app
from internal.repository.sqlite_figurinha_repository import SQLiteFigurinhaRepository
from internal.service.figurinha_service import FigurinhaService


def create_app():
    db = connect("figurinhas.db")
    migrate(db)

    repository = SQLiteFigurinhaRepository(db)
    service = FigurinhaService(repository)
    return build_app(service)


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)
