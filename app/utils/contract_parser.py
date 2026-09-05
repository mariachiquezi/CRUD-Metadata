import yaml

from app.models.contract import DataContract


class ContractParser:

    @staticmethod
    def parse(content: str) -> DataContract:

        try:
            data = yaml.safe_load(content)

        except yaml.YAMLError as error:
            raise ValueError(f"YAML inválido: {error}")

        if not isinstance(data, dict):
            raise ValueError("O contrato YAML deve conter um objeto valido.")

        try:
            return DataContract.model_validate(data)
        except TypeError as error:
            raise ValueError("O contrato YAML possui formato invalido.") from error
