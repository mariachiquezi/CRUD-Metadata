# Catálogo de metadados

Microserviço desenvolvido com FastAPI e MongoDB para catalogar tabelas de dados, seus schemas, responsáveis, origem, qualidade, ciclo de vida e histórico de alterações.

## O que o projeto oferece

- CRUD de metadados com `POST`, `GET`, `PUT`, `PATCH` e `DELETE`.
- Histórico versionado com responsável, data e tipo da alteração.
- Ingestão de contratos YAML individualmente ou em lote.
- Validação de schema, qualidade, ownership e compatibilidade entre versões.
- Autenticação JWT e autorização por papéis (`admin`, `editor` e `viewer`).
- Endpoints de saúde para uso em Docker, Kubernetes e pipelines de CI/CD.

## Como executar

Com Docker Desktop iniciado, abra o PowerShell nesta pasta e execute:

```powershell
$env:JWT_SECRET_KEY = "chave-local-com-pelo-menos-32-caracteres"
docker compose up --build
```

A API ficará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.

Para executar apenas a API localmente, mantendo o MongoDB em container:

```powershell
docker compose up -d mongo
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Acesso de demonstração

Obtenha um token em `POST /auth/login` usando:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Depois envie o token nas rotas protegidas como `Authorization: Bearer <token>`.

## Endpoints principais

```text
POST   /auth/login
POST   /metadata
GET    /metadata
GET    /metadata/{id}
GET    /metadata/history
GET    /metadata/{id}/history
PUT    /metadata/{id}
PATCH  /metadata/{id}
DELETE /metadata/{id}
POST   /contracts/bulk
GET    /health/live
GET    /health/ready
```

## Documentação técnica

- [Guia completo da aplicação](app/README.md)
- [Arquitetura e fluxo](docs/architecture.md)
- [Contrato de dados YAML](docs/data-contract.md)
- [Decisão sobre identidade do ativo](docs/adr/0001-data-asset-identity.md)

## Testes e qualidade

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m mypy app
```
