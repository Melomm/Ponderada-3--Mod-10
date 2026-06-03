import sqlite3
import unittest

from internal.database.sqlite import migrate
from internal.domain.figurinha import VALID_POSITIONS, VALID_TYPES
from internal.errors.errors import ErrFigureNotFound, ErrInvalidType, ErrMissingField
from internal.repository.sqlite_figurinha_repository import SQLiteFigurinhaRepository
from internal.service.figurinha_service import FigurinhaService


class FigurinhaServiceTest(unittest.TestCase):
    def setUp(self):
        db = sqlite3.connect(":memory:")
        db.row_factory = sqlite3.Row
        migrate(db)
        self.service = FigurinhaService(SQLiteFigurinhaRepository(db))

    def test_create_fills_dates(self):
        figurinha = self.service.create(
            {"numero": "BRA 15", "tipo": "comum", "posicao": "Atacante"}
        )

        self.assertEqual(figurinha.id, 1)
        self.assertEqual(figurinha.numero, "BRA 15")
        self.assertEqual(figurinha.tipo, "comum")
        self.assertEqual(figurinha.posicao, "Atacante")
        self.assertIsNotNone(figurinha.created_at)
        self.assertIsNotNone(figurinha.updated_at)

    def test_rejects_missing_required_field(self):
        with self.assertRaises(ErrMissingField):
            self.service.create({"tipo": "comum", "posicao": "Atacante"})

    def test_rejects_invalid_type(self):
        with self.assertRaises(ErrInvalidType):
            self.service.create(
                {"numero": "BRA 15", "tipo": "especial", "posicao": "Atacante"}
            )

    def test_not_found_on_get(self):
        with self.assertRaises(ErrFigureNotFound):
            self.service.get_by_id(99)

    def test_list_filters_by_type(self):
        self.service.create({"numero": "BRA 15", "tipo": "comum", "posicao": "Atacante"})
        self.service.create(
            {"numero": "ARG 10", "tipo": "brilhante", "posicao": "Meio-campista"}
        )

        result = self.service.list(tipo="brilhante")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].numero, "ARG 10")

    def test_open_pack_creates_random_figurinha(self):
        pack = self.service.open_pack()
        figurinha = pack["figurinha"]

        self.assertEqual(figurinha["id"], 1)
        self.assertIn(figurinha["tipo"], VALID_TYPES)
        self.assertIn(figurinha["posicao"], VALID_POSITIONS)
        self.assertTrue(figurinha["numero"])
        self.assertEqual(len(self.service.list()), 1)

    def test_open_pack_creates_one_figurinha_per_call(self):
        self.service.open_pack()
        self.service.open_pack()

        self.assertEqual(len(self.service.list()), 2)

    def test_pack_message_for_legends_ouro(self):
        self.assertIn("legends ouro", self.service._pack_message("legends_ouro"))


if __name__ == "__main__":
    unittest.main()
