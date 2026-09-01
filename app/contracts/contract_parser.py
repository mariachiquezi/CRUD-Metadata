import yaml

from app.models.contract import DataContract


class ContractParser:

    @staticmethod
    def parse(content: str) -> DataContract:

        try:
            data = yaml.safe_load(content)

        except yaml.YAMLError as error:
            raise ValueError(f"YAML inválido: {error}")

        return DataContract.model_validate(data)
