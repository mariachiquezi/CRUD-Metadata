from typing import Any, Dict


class MetadataValidator:
    ALLOWED_SOURCE_TYPES = {"database", "api", "file", "stream"}
    ALLOWED_LIFECYCLE_STATUS = {"active", "ativo", "deprecated", "draft"}

    @staticmethod
    def validate(payload: Dict[str, Any]) -> None:
        table_name = str(payload.get("table_name") or "").strip()
        if not table_name:
            raise ValueError("Campo 'table_name' é obrigatório.")
        if table_name.lower() == "string":
            raise ValueError("Campo 'table_name' deve identificar uma tabela real.")

        owner_info = payload.get("owner_info")
        if (
            not isinstance(owner_info, dict)
            or not str(owner_info.get("team") or "").strip()
        ):
            raise ValueError("Campo 'owner_info.team' é obrigatório.")
        if str(owner_info.get("team") or "").strip().lower() == "string":
            raise ValueError("Campo 'owner_info.team' deve identificar um time real.")

        schema = payload.get("schema")
        if not isinstance(schema, list) or not schema:
            raise ValueError("Campo 'schema' deve ser uma lista não vazia.")

        field_names = set()
        for field in schema:
            if not isinstance(field, dict):
                raise ValueError(
                    "Cada item do schema deve ser um objeto com 'name' e 'type'."
                )

            field_name = str(field.get("name") or "").strip()
            field_type = str(field.get("type") or "").strip()

            if not field_name:
                raise ValueError("Campo 'schema[].name' é obrigatório.")
            if field_name.lower() == "string":
                raise ValueError("Campo 'schema[].name' deve identificar um campo real.")

            if not field_type:
                raise ValueError(f"Campo 'schema[].type' é obrigatório para '{field_name}'.")

            if field_name in field_names:
                raise ValueError(f"Campo duplicado no schema: {field_name}")

            field_names.add(field_name)

        source_type = str(payload.get("source_type") or "").strip().lower()
        if source_type and source_type not in MetadataValidator.ALLOWED_SOURCE_TYPES:
            raise ValueError(
                f"Tipo de source inválido: '{payload.get('source_type')}'. "
                "Valores aceitos: database, api, file, stream."
            )

        lifecycle = payload.get("lifecycle")
        if isinstance(lifecycle, dict):
            status = str(lifecycle.get("status") or "").strip().lower()
            if status and status not in MetadataValidator.ALLOWED_LIFECYCLE_STATUS:
                raise ValueError(
                    f"Status inválido para 'lifecycle.status': '{lifecycle.get('status')}'. "
                    "Valores aceitos: active, ativo, deprecated, draft."
                )

        quality = payload.get("quality")
        if quality is not None:
            if not isinstance(quality, dict):
                raise ValueError("Campo 'quality' deve ser um objeto.")

            completeness = quality.get("completeness", [])
            if completeness is not None:
                if not isinstance(completeness, list):
                    raise ValueError("Campo 'quality.completeness' deve ser uma lista.")

                for item in completeness:
                    if not isinstance(item, dict):
                        raise ValueError(
                            "Cada regra de completeness deve ser um objeto."
                        )
                    threshold = item.get("threshold")
                    if threshold is None:
                        raise ValueError(
                            "Campo 'quality.completeness[].threshold' é obrigatório."
                        )
                    if not isinstance(threshold, (int, float)) or not (
                        0 <= float(threshold) <= 100
                    ):
                        raise ValueError(
                            "Campo 'quality.completeness[].threshold' deve estar entre 0 e 100."
                        )

            freshness = quality.get("freshness")
            if freshness is not None:
                if not isinstance(freshness, dict):
                    raise ValueError("Campo 'quality.freshness' deve ser um objeto.")
                if not str(freshness.get("max_delay") or "").strip():
                    raise ValueError(
                        "Campo 'quality.freshness.max_delay' é obrigatório."
                    )

        tags = payload.get("tags")
        if tags is not None:
            if not isinstance(tags, list):
                raise ValueError("Campo 'tags' deve ser uma lista.")
            for tag in tags:
                if not str(tag or "").strip():
                    raise ValueError("Tags não podem conter valores vazios.")
