from app.models.contract import DataContract


class ContractValidator:

    ALLOWED_SOURCE_TYPES = {"database", "api", "file", "stream"}
    ALLOWED_LIFECYCLE_STATUS = {"active", "deprecated", "draft"}

    @classmethod
    def validate(cls, contract: DataContract):

        cls._validate_data_asset(contract)
        cls._validate_schema(contract)
        cls._validate_source(contract)
        cls._validate_lifecycle(contract)

    @classmethod
    def _validate_data_asset(cls, contract):
        definition = contract.contract
        asset_name = (
            definition.data_asset.name
            if definition.data_asset
            else definition.source.table or definition.name
        )
        if not asset_name or not asset_name.strip():
            raise ValueError(
                "O contrato deve informar data_asset.name. "
                "source.table e name são alternativas legadas."
            )

    @classmethod
    def _validate_schema(cls, contract):

        fields = contract.contract.schema_
        if not fields:
            raise ValueError("O contrato deve possuir pelo menos um campo.")

        field_names = set()
        for field in fields:
            if field.name in field_names:
                raise ValueError(f"Campo duplicado no schema: {field.name}")
            field_names.add(field.name)
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
