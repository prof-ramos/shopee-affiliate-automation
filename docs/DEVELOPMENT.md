# Guia de Desenvolvimento

## Pre-requisitos

- Python 3.9+ se voce for adicionar ou executar scripts locais.
- Dependencias (de `SKILL.md`): `requests>=2.28.0`, `graphql-core>=3.2.0`.

## Setup local

1. Copie `.env.example` para `.env` e defina `SHOPEE_APP_ID` e `SHOPEE_SECRET`.
2. Instale dependencias quando houver scripts, por exemplo:
   `python -m pip install -r requirements.txt`

## Scripts

- `scripts/test_api.py` - Teste rapido da API Shopee com assinatura SHA256.
- Se voce adicionar novos scripts, mantenha exemplos minimos em `SKILL.md`,
  apontando para a implementacao completa em `scripts/`.

## Atualizacao de docs

- Mantenha `SKILL.md` curto e mova detalhes para `references/`.
- Evite duplicar conteudo entre o arquivo da skill e as referencias.
