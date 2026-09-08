class DomainError(Exception):
    """Base exception for business rule violations."""


class ContractAlreadyExistsError(DomainError):
    def __init__(self, data_asset_key: str, version: str):
        super().__init__(f"A versão '{version}' já existe para o Data Asset '{data_asset_key}'.")


class InvalidContractVersionError(DomainError):
    def __init__(self, current_version: str, requested_version: str):
        super().__init__(
            "A versão do contrato deve ser maior que a versão atual "
            f"('{current_version}'): '{requested_version}'."
        )


class IncompatibleSchemaError(DomainError):
    def __init__(
        self,
        field_name: str,
        reason: str = "foi removido",
        *,
        current_type: str | None = None,
        requested_type: str | None = None,
    ):
        if current_type is not None or requested_type is not None:
            message = (
                f"Atualização rejeitada: o campo '{field_name}' já está definido como "
                f"'{current_type}', mas a nova versão informa '{requested_type}'. "
                "Nenhum dado foi alterado."
            )
        else:
            message = (
                f"Alteração incompatível no schema: o campo '{field_name}' {reason}. "
                "A atualização foi rejeitada e nenhum dado foi alterado."
            )
        super().__init__(message)
