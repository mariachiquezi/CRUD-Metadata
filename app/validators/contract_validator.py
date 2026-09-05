from app.models.contract import DataContract


class ContractValidator:

    ALLOWED_TYPES = {"string", "integer", "float", "boolean", "date", "datetime"}
    ALLOWED_SOURCE_TYPES = {"database", "api", "file", "stream"}
    ALLOWED_LIFECYCLE_STATUS = {"active", "deprecated", "draft"}

    @classmethod
    def validate(cls, contract: DataContract):

        cls._validate_schema(contract)
        cls._validate_source(contract)
        cls._validate_lifecycle(contract)

    @classmethod
    def _validate_schema(cls, contract):

        fields = contract.contract.schema
        if not fields:
            raise ValueError("O contrato deve possuir pelo menos um campo.")

        field_names = set()
        for field in fields:
            if field.name in field_names:
                raise ValueError(f"Campo duplicado no schema: {field.name}")
            field_names.add(field.name)
            if field.type not in cls.ALLOWED_TYPES:
                raise ValueError(f"Tipo inválido para {field.name}: {field.type}")

    @classmethod
    def _validate_source(cls, contract):
        source_type = contract.contract.source.type
        if source_type not in cls.ALLOWED_SOURCE_TYPES:
            raise ValueError(f"Tipo de source inválido: {source_type}")

    @classmethod
    def _validate_lifecycle(cls, contract):
        lifecycle = contract.contract.lifecycle
        if lifecycle is None:
            return
        if lifecycle.status not in cls.ALLOWED_LIFECYCLE_STATUS:
            raise ValueError(f"Status inválido: {lifecycle.status}")
