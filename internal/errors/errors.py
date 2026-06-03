class DomainError(Exception):
    pass


class ErrInvalidType(DomainError):
    def __init__(self):
        super().__init__(
            "tipo inválido. Use: comum, brilhante, legends_ouro ou legends_bronze"
        )


class ErrInvalidPosition(DomainError):
    def __init__(self):
        super().__init__(
            "posição inválida. Use: Goleiro, Zagueiro, Meio-campista ou Atacante"
        )


class ErrFigureNotFound(DomainError):
    def __init__(self):
        super().__init__("figurinha não encontrada")


class ErrMissingField(DomainError):
    def __init__(self, field: str):
        super().__init__(f"campo obrigatório ausente: {field}")


class ErrReadOnlyField(DomainError):
    def __init__(self, field: str):
        super().__init__(f"o campo {field} é controlado pela API")
