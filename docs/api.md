# API HTTP

Este documento organiza os endpoints por recurso. A aplicação está disponível, por padrão, em `http://localhost:8000`.

No Swagger (`http://localhost:8000/docs`), os mesmos recursos aparecem separados pelas tags `auth`, `metadata`, `metadata-history`, `contracts`, `health` e `system`.

## Convenções

As rotas protegidas exigem o cabeçalho:

```text
Authorization: Bearer <jwt>
```

Os corpos de metadados seguem o formato oficial descrito em [data-contract.md](data-contract.md). Na entrada, `version` representa a versão do contrato enviada pelo cliente. Na resposta, `version` representa a revisão interna do metadado; a versão do contrato aparece como `contract_version`. No histórico, `version` também representa a revisão daquele evento.

### Perfis

| Perfil | Pode consultar | Pode criar/editar | Pode excluir | Pode enviar contratos |
| --- | --- | --- | --- | --- |
| `viewer` | Sim | Não | Não | Não |
| `editor` | Sim | Sim | Não | Sim |
| `admin` | Sim | Sim | Sim | Sim |

## 1. Autenticação

### `POST /auth/login`

Gera um JWT para um usuário válido.

**Corpo:**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Resposta `200`:**

```json
{
  "access_token": "<jwt>"
}
```

Credenciais de demonstração: `admin/admin123`, `editor/editor123` e `viewer/viewer123`.

## 2. Metadados ativos

Estas rotas trabalham com o documento atual de cada ativo na collection `metadata`.

### `POST /metadata`

Cria um metadado. Exige `admin` ou `editor` e retorna `201`.

Exemplo mínimo:

```json
{
  "data_asset": {"name": "orders", "type": "table"},
  "version": "1.0",
  "domain": "commerce",
  "description": "Pedidos realizados pelos clientes",
  "ownership": {"owner": "commerce-platform", "steward": "order-team"},
  "source": {"system": "ecommerce", "type": "database"},
  "schema": [
    {"name": "order_id", "type": "string", "nullable": false}
  ]
}
```

### `GET /metadata`

Lista os metadados ativos. Aceita `admin`, `editor` e `viewer`.

Parâmetros de consulta:

| Parâmetro | Descrição |
| --- | --- |
| `page` | Página, começando em `1`. Padrão: `1`. |
| `page_size` | Itens por página, de `1` a `100`. Padrão: `20`. |
| `domain` | Filtra pelo domínio. |
| `owner` | Filtra pelo responsável em `ownership.owner`. |
| `asset_name` | Filtra por `data_asset.name`. |

### `GET /metadata/{metadata_id}`

Retorna um metadado ativo pelo ID. Se o registro não existir na collection ativa, retorna `404`.

### `PUT /metadata/{metadata_id}`

Substitui o cadastro completo. Exige o corpo completo de `MetadataReplace`, além do perfil `admin` ou `editor`. Alterações incompatíveis com o schema ou com a versão retornam `409`.

### `PATCH /metadata/{metadata_id}`

Altera somente os campos enviados. Exige `admin` ou `editor`.

Para alterar somente o ciclo de vida:

```http
PATCH /metadata/{metadata_id}
```

```json
{
  "lifecycle": {"status": "deprecated"}
}
```

Campos aninhados enviados no `PATCH` são tratados como uma atualização daquele bloco. O restante do documento é preservado.

### `DELETE /metadata/{metadata_id}`

Remove o documento da collection ativa. Exige `admin`. O histórico não é removido; a resposta informa que a exclusão foi registrada.

## 3. Histórico de metadados

O histórico fica separado na collection `metadata_history`. Ele permite auditoria e consulta da evolução do ativo, inclusive depois de uma exclusão.

### `GET /metadata/history`

Lista o histórico de todos os metadados. Aceita `admin`, `editor` e `viewer`.

### `GET /metadata/{metadata_id}/history`

Lista as versões e eventos de um metadado específico. Aceita os três perfis de leitura.

Cada evento informa, entre outros campos:

| Campo | Significado |
| --- | --- |
| `version` | Revisão do metadado naquele evento. |
| `change_type` | `CREATE`, `UPDATE` ou `DELETE`. |
| `changed_by` | Usuário que realizou a operação. |
| `changed_at` | Data e hora da operação. |
| `deleted` | Indica se o evento representa uma exclusão. |

Depois de um `DELETE`, `GET /metadata/{id}` retorna `404`, mas `GET /metadata/{id}/history` continua disponível porque os eventos foram preservados.

## 4. Contratos YAML

### `POST /contracts/bulk`

Recebe um ou mais arquivos YAML no campo multipart `files`. Exige `admin` ou `editor`.

- Quantidade: de `1` a `10` arquivos por chamada.
- Tamanho: até `5 MB` por arquivo.
- Codificação: UTF-8.
- Todos os arquivos válidos: resposta `200`.
- Ao menos um arquivo inválido: resposta `207`, com o resultado individual em `items`.

A rota é a mesma para um arquivo ou para vários; o nome `bulk` indica que ela aceita ambos os casos. O processamento não é transacional: um arquivo válido pode ser salvo mesmo que outro do mesmo lote falhe.

## 5. Saúde da aplicação

### `GET /health/live`

Verifica se o processo HTTP está respondendo. Não acessa o MongoDB. Retorna `200` com `{"status": "ok"}`.

### `GET /health/ready` e `GET /health`

Verificam se a aplicação consegue acessar o MongoDB. Retornam `200` quando o banco está disponível e `503` quando a dependência está indisponível.

## Códigos de resposta mais comuns

| Código | Uso |
| --- | --- |
| `200` | Consulta, atualização, exclusão ou lote totalmente processado. |
| `201` | Metadado ou contrato criado. |
| `207` | Lote processado parcialmente. |
| `401` | Token ausente, inválido ou credenciais inválidas. |
| `403` | Perfil sem permissão para a operação. |
| `404` | Metadado ativo não encontrado. |
| `409` | Identidade duplicada, versão inválida ou incompatibilidade de schema. |
| `413` | Arquivo maior que `5 MB`. |
| `422` | Corpo ou arquivo não atende ao formato esperado. |
| `503` | MongoDB indisponível. |
