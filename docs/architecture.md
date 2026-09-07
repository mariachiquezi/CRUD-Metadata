# Arquitetura

## Domínio

O conceito central é o ativo de dados. Um contrato de dados governa esse ativo ao declarar seu schema, ownership, qualidade, classificação, ciclo de vida e versão.

A identidade estável é `data_asset_key`, normalmente derivada de `domain` e `data_asset.name`. Por exemplo, o ativo `orders` do domínio `commerce` recebe a chave `commerce.orders`.

## Camadas

```text
Rotas HTTP -> serviços de aplicação -> validadores de domínio -> protocolo do repositório -> MongoDB
                                                |
                                                +-> histórico de metadados
```

As rotas cuidam da autenticação, autorização, códigos HTTP e serialização. Os serviços coordenam os casos de uso e aplicam as regras de versionamento. Os modelos Pydantic validam a estrutura dos dados. O `schema_validator` verifica nomes de colunas e referências de qualidade tanto nos contratos YAML quanto nos metadados JSON. Os repositórios concentram somente a persistência.

## Fluxo de uma requisição

1. O cliente envia uma requisição HTTP com o token JWT quando a rota exige autenticação.
2. A rota valida o corpo ou os arquivos recebidos e identifica o usuário atual.
3. O serviço executa as regras de negócio, normaliza campos legados e valida compatibilidade.
4. O repositório consulta ou altera as collections `metadata` e `metadata_history`.
5. A rota converte o resultado para a resposta pública da API.

No upload de contratos, o fluxo é `YAML -> ContractParser -> ContractDefinition -> ContractService -> MetadataService -> MongoDB`.

## Versionamento e histórico

O documento ativo representa o estado atual do ativo. Cada alteração aceita cria uma entrada no histórico com o mesmo ID do metadado e incrementa `metadata_version`. A API mantém `version` como alias público por compatibilidade. Já `contract_version` é a versão do contrato de negócio e deve sempre avançar.

O histórico registra `changed_at`, `changed_by` e `change_type` (`CREATE`, `UPDATE` ou `DELETE`). A exclusão remove o documento ativo, mas preserva os registros históricos.

## Compatibilidade do schema

É permitido adicionar campos opcionais e relaxar a obrigatoriedade de campos existentes. Remover campos, adicionar campos obrigatórios, exigir unicidade ou deixar um campo que aceitava nulos como obrigatório são alterações rejeitadas.

A troca de tipo de uma coluna é rejeitada em versões menores. Ela é permitida quando a versão principal aumenta, como de `1.0` para `2.0`. Nesse caso, o histórico registra a nova definição. A identidade do ativo continua a mesma.

O índice único de `data_asset_key` impede dois metadados ativos para a mesma identidade. A API também compara a versão atual antes de aceitar uma alteração.


## Modelos e compatibilidade de entrada

As estruturas canônicas são aninhadas: `data_asset`, `ownership` e `source`, os contratos YAML devem usar a estrutura canônica.

O cadastro manual em `POST /metadata` usa o mesmo conteúdo do bloco `contract` do YAML, sem o invólucro externo. Assim, a mesma definição pode ser enviada por arquivo ou diretamente como JSON. A única conversão interna é `version` para `contract_version`, pois o segundo nome distingue a versão do contrato da versão interna do metadado.

As regras completas do contrato estão em [Contrato de dados](data-contract.md). A decisão sobre a identidade está documentada em [ADR 0001](adr/0001-data-asset-identity.md).
