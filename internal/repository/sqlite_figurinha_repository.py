import sqlite3
from datetime import datetime
from typing import List, Optional

from internal.domain.figurinha import Figurinha


class SQLiteFigurinhaRepository:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def create(self, figurinha: Figurinha) -> Figurinha:
        cursor = self.db.execute(
            """
            INSERT INTO figurinhas (numero, tipo, posicao, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                figurinha.numero,
                figurinha.tipo,
                figurinha.posicao,
                figurinha.created_at.isoformat(),
                figurinha.updated_at.isoformat(),
            ),
        )
        self.db.commit()
        return Figurinha(
            id=cursor.lastrowid,
            numero=figurinha.numero,
            tipo=figurinha.tipo,
            posicao=figurinha.posicao,
            created_at=figurinha.created_at,
            updated_at=figurinha.updated_at,
        )

    def get_by_id(self, figurinha_id: int) -> Optional[Figurinha]:
        row = self.db.execute(
            """
            SELECT id, numero, tipo, posicao, created_at, updated_at
            FROM figurinhas
            WHERE id = ?
            """,
            (figurinha_id,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def list(
        self, tipo: Optional[str] = None, posicao: Optional[str] = None
    ) -> List[Figurinha]:
        sql = """
            SELECT id, numero, tipo, posicao, created_at, updated_at
            FROM figurinhas
            WHERE 1 = 1
        """
        params = []

        if tipo is not None:
            sql += " AND tipo = ?"
            params.append(tipo)

        if posicao is not None:
            sql += " AND posicao = ?"
            params.append(posicao)

        sql += " ORDER BY id"

        rows = self.db.execute(sql, params).fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, figurinha: Figurinha) -> Figurinha:
        self.db.execute(
            """
            UPDATE figurinhas
            SET numero = ?, tipo = ?, posicao = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                figurinha.numero,
                figurinha.tipo,
                figurinha.posicao,
                figurinha.updated_at.isoformat(),
                figurinha.id,
            ),
        )
        self.db.commit()
        return figurinha

    def delete(self, figurinha_id: int) -> bool:
        cursor = self.db.execute(
            """
            DELETE FROM figurinhas
            WHERE id = ?
            """,
            (figurinha_id,),
        )
        self.db.commit()
        return cursor.rowcount > 0

    def _from_row(self, row: sqlite3.Row) -> Figurinha:
        return Figurinha(
            id=row["id"],
            numero=row["numero"],
            tipo=row["tipo"],
            posicao=row["posicao"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
