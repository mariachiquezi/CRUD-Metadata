# Contrato de dados

O contrato descreve um ativo de dados e suas expectativas de uso. É um formato próprio deste projeto. A API cataloga as declarações; não lê as tabelas para medir qualidade, aplicar tipos ou executar migrações.

Envie de 1 a 10 arquivos em `POST /contracts/bulk`, usando o campo multipart `files`. O limite por arquivo é 5 MiB. Cada arquivo tem seu próprio resultado; o lote não é atômico. O processamento grava o metadado e o histórico em chamadas separadas, permitindo executar com uma instalação comum do MongoDB.

## Mesmo padrão no cadastro manual

O corpo de `POST /metadata` usa os mesmos campos internos do bloco `contract`. A diferença é que a requisição manual não possui o invólucro `contract`:

```json
{
  "data_asset": {"name": "orders", "type": "table"},
  "version": "1.0",
  "domain": "commerce",
  "description": "Pedidos realizados pelos clientes.",
  "ownership": {"owner": "commerce-platform", "steward": "order-team"},
  "source": {"system": "ecommerce", "type": "database"},
  "schema": [{"name": "order_id", "type": "string", "nullable": false}],
  "quality": {"freshness": {"max_delay": "1h"}},
  "lifecycle": {"status": "active"}
}
```

No YAML, `version` é convertido para `contract_version` durante a ingestão. No cadastro manual, a API faz a mesma conversão internamente. Os campos achatados antigos, como `table_name`, `owner_info`, `source_system` e `freshness`, continuam aceitos apenas para compatibilidade com clientes legados e não fazem parte do padrão recomendado.

Um exemplo completo desse corpo JSON está em [examples/employee_department.json](examples/employee_department.json).

## Estrutura recomendada

```yaml
contract:
  data_asset:
    name: orders
    type: table
  version: "1.0"
  domain: commerce
  description: Pedidos dos clientes e seus valores totais.
  tags: [commerce, orders]

  data_product:
    name: order-platform
    description: Produto de dados para análise da jornada de compra.

  ownership:
    owner: commerce-platform
    steward: analytics-team

  source:
    system: ecommerce
    type: database
    database: commerce_db
    table: orders
    location: postgresql://commerce-db.internal:5432/commerce_db

  schema:
    - name: order_id
      type: string
      nullable: false
      unique: true
      description: Identificador do pedido.
    - name: total_amount
      type: decimal
      nullable: false
      description: Valor total do pedido.

  refresh_frequency: daily

  quality:
    freshness:
      max_delay: 1h
    completeness:
      - field: order_id
        threshold: 100

  classification:
    data_classification: internal
  lifecycle:
    status: active
```

| Campo | Obrigatório | Regra e significado |
| --- | --- | --- |
| `contract` | Sim | Objeto raiz do arquivo. |
| `data_asset.name` | Sim no formato recomendado | Identidade lógica do ativo. Não repita como `contract.name`. |
| `data_asset.type` | Não | Padrão `table`; outros tipos não vazios são aceitos. |
| `version` | Sim | Texto com componentes numéricos, como `"1.0"`. Não é o contador interno de alterações do catálogo. |
| `domain` | Sim | Domínio de negócio não vazio. |
| `description` | Não | Contexto desta tabela. |
| `data_product` | Não | Produto que agrupa ou utiliza o ativo. Sua descrição tem escopo diferente da descrição da tabela. |
| `ownership.owner` | Sim | Equipe responsável. |
| `ownership.steward` | Não | Responsável por curadoria e documentação. |
| `source.system` | Sim | Sistema de origem. |
| `source.type` | Sim | `database`, `api`, `file` ou `stream`. |
| `source.database`, `source.table` | Não | Localização física quando aplicável. A tabela física pode ter nome diferente do ativo lógico. |
| `source.location` | Não | Localização declarada, como URL de uma API ou caminho `s3://bucket/prefix/`. Não é consultada pela aplicação. |
| `schema` | Sim | Lista não vazia de colunas com nome e tipo não vazios. Nomes não podem repetir. |
| `schema[].nullable` | Não | Padrão `true`. |
| `schema[].unique` | Não | Padrão `false`. |
| `tags` | Não | Lista de textos não vazios. |
| `refresh_frequency` | Não | Frequência esperada de atualização, como `daily`, `hourly` ou `weekly`. |
| `quality.freshness.max_delay` | Se `freshness` for informado | Inteiro positivo seguido de `s`, `m`, `h` ou `d`, por exemplo `30s`, `15m`, `1h`, `2d`. |
| `quality.completeness` | Não | Percentuais entre 0 e 100, uma regra por coluna, referenciando nomes presentes no schema. |
| `classification.data_classification` | Se o bloco for informado | Texto não vazio. A aplicação não presume uma taxonomia corporativa universal. |
| `lifecycle.status` | Se o bloco for informado | `active`, `deprecated` ou `draft`; o valor legado `ativo` é normalizado para `active`. |

Os tipos de coluna permanecem abertos para tipos nativos como `uuid`, `decimal(18,2)` ou `array<string>`. A comparação de compatibilidade usa o texto exato do tipo; não há equivalência automática entre `int` e `integer`. Os exemplos monetários usam `decimal`; isso não converte dados nem migra contratos previamente cadastrados como `float`.

## Validação e compatibilidade

- Campos desconhecidos são rejeitados, inclusive dentro dos objetos aninhados. Isso evita ignorar erros como `stewrad` em vez de `steward`.
- Chaves YAML repetidas são rejeitadas antes que sobrescrevam valores. O parser usa um loader derivado de `SafeLoader`; tags que constroem objetos Python não são aceitas.
- Os formatos antigos `contract.name` e, na ausência do ativo, `source.table` continuam aceitos como alternativas de entrada. São convertidos para `data_asset`; nomes lógicos contraditórios são rejeitados.
- A identidade persistida continua sendo `domain + "." + data_asset.name`. Alterá-la exige cadastrar outro ativo. Ambientes que tenham o mesmo nome em vários bancos do mesmo domínio precisam rever essa identidade em uma migração específica.
- Uma nova versão de contrato precisa avançar. `1.0` e `1.0.0` são comparadas como a mesma versão.
- Remover coluna, adicionar coluna obrigatória ou tornar restrições existentes mais exigentes é rejeitado. A troca de tipo também é rejeitada em versões menores; ela só é permitida quando a versão principal aumenta, por exemplo, de `1.0` para `2.0`. A API informa os tipos anterior e solicitado e não altera o registro quando a compatibilidade falha.
