# Catálogo de metadados

Microserviço FastAPI para catálogo de metadados de tabelas de dados.

## Funcionalidades
- CRUD de metadados com POST, GET, PUT, PATCH e DELETE
- histórico versionado com `changed_by` e `change_type`
- persistência em MongoDB
- ingestão individual e em lote via contrato YAML
- autenticação JWT com RBAC
- validações estruturais e de domínio
- testes unitários

## Execução local

```bash
python -m venv venv
source venv/bin/activate  # no Windows: venv\Scripts\activate
pip install -r app/requirements.txt
uvicorn app.main:app --reload
```

No Windows PowerShell, a instalação existente do projeto pode ser usada diretamente:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Docker

Defina uma chave JWT antes de iniciar os containers:

```bash
JWT_SECRET_KEY=uma-chave-secreta-longa docker compose up --build
```

No PowerShell:

```powershell
$env:JWT_SECRET_KEY = "uma-chave-secreta-longa"
docker compose up --build
```

A API ficará disponível em `http://localhost:8000` e o MongoDB será persistido no volume `mongodb_data`.

Para parar os containers:

```bash
docker compose down
```

## Arquitetura e fluxo

```text
Rotas -> Serviços -> Repositórios -> MongoDB
YAML -> ContractParser -> ContractDefinition -> ContractService -> MetadataService
```

As rotas recebem a requisição e autenticam o usuário. Os serviços aplicam as regras de negócio e de compatibilidade. Os repositórios persistem os dados no MongoDB. O estado atual fica em `metadata` e as versões em `metadata_history`.

No cadastro ou alteração, o serviço valida o modelo, calcula `data_asset_key`, grava o estado atual e cria uma entrada de histórico. O histórico registra o usuário, a data e o tipo da alteração.

## Autenticação e autorização

Obtenha um token em `POST /auth/login`:

```json
{"username": "admin", "password": "admin123"}
```

Usuários de teste:

| Usuário | Senha | Permissões |
| --- | --- | --- |
| admin | admin123 | Todas |
| editor | editor123 | Consultar, criar e editar |
| viewer | viewer123 | Apenas consultar |

Para testes, foi implementado um mecanismo simplificado baseado em usuários de demonstração e JWT. Em ambiente corporativo, a autenticação seria delegada a um provedor de identidade via OAuth2, OIDC ou SSO.

Envie o token nas rotas protegidas:

```text
Authorization: Bearer <token>
```

## Principais endpoints

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

As rotas de leitura aceitam `admin`, `editor` e `viewer`. Criação e alteração aceitam `admin` e `editor`; exclusão exige `admin`. `/health/live` verifica se o processo responde. `/health/ready` e `/health` verificam também a conexão com o MongoDB.

`POST /contracts/bulk` aceita de 1 a 10 arquivos no campo multipart `files` e retorna o status individual de cada contrato. O envio de um único contrato usa a mesma rota e o mesmo formato de resposta.

Quando todos os arquivos são processados, a rota retorna `200`. Se algum arquivo falhar, retorna `207` e informa o resultado de cada arquivo em `items`. O lote não é transacional.

## Alteração parcial

Use `PATCH` quando quiser alterar apenas alguns campos. Por exemplo, para mudar o ciclo de vida:

```http
PATCH /metadata/{id}
```

```json
{
  "lifecycle": {
    "status": "deprecated"
  }
}
```

Use `PUT` quando quiser substituir o cadastro completo. Alterações incompatíveis no schema retornam `409` e não alteram o registro.

## Mesmo padrão para contrato e cadastro manual

O corpo de `POST /metadata` usa o mesmo formato do conteúdo de `contract` no YAML. No cadastro manual, remova apenas o invólucro `contract` e envie `version`, `data_asset`, `domain`, `ownership`, `source`, `schema`, `quality` e os demais blocos necessários. A API converte `version` para `contract_version` internamente.

Campos achatados como `table_name`, `source_system`, `source_type`, `business_domain` e `freshness` permanecem aceitos para compatibilidade com clientes antigos, mas não devem ser usados em novos cadastros. O ownership é representado apenas pelo bloco `ownership`.

## Histórico

Cada evento possui `changed_by` e `change_type`: `CREATE`, `UPDATE` ou `DELETE`.

## Exemplo de contrato YAML

A estrutura completa, os campos obrigatórios e as regras de compatibilidade estão em [docs/data-contract.md](../docs/data-contract.md).

```yaml
contract:
  data_asset:
    name: orders
    type: table
  version: "1.4"

  data_product:
    name: order-platform
    description: Pedidos realizados pelos clientes

  ownership:
    owner: commerce-platform
    steward: order-team

  source:
    system: ecommerce
    type: database
    database: commerce_db
    location: postgresql://commerce-db.internal:5432/commerce_db

  domain: commerce

  schema:
    - name: order_id
      type: string
      nullable: false
      unique: true
      description: Identificador unico do pedido
    - name: total_amount
      type: decimal
      nullable: false
      description: Valor total do pedido
```

## Testes

```bash
python -m pytest -q
```

## Verificações de qualidade

Instale as ferramentas de desenvolvimento com `pip install -r requirements.txt` e execute:

```bash
ruff check app tests
ruff format --check app tests
mypy app
python -m pytest --cov=app --cov-report=term-missing -q
```

A arquitetura e as decisões de domínio estão documentadas em `docs/architecture.md` e `docs/adr/`.
