import yaml

from app.models.contract import DataContract


class UniqueKeySafeLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        keys = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                if key in keys:
                    raise yaml.constructor.ConstructorError(
                        None, None, f"Chave duplicada no YAML: {key}", key_node.start_mark
                    )
                keys.add(key)
            except TypeError as error:
                raise yaml.constructor.ConstructorError(
                    None, None, "Chave inválida no YAML.", key_node.start_mark
                ) from error
        return super().construct_mapping(node, deep=deep)


class ContractParser:
    @staticmethod
    def parse(content: str) -> DataContract:
        try:
            data = yaml.load(content, Loader=UniqueKeySafeLoader)

        except yaml.YAMLError as error:
            raise ValueError(f"YAML inválido: {error}") from error

        if not isinstance(data, dict):
            raise ValueError("O contrato YAML deve conter um objeto valido.")

        return DataContract.model_validate(data)
