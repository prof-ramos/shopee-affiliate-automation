# Teste rapido da API Shopee

## Pre-requisitos

- `SHOPEE_APP_ID` e `SHOPEE_SECRET` definidos no ambiente.
- Dependencias instaladas: `python -m pip install -r requirements.txt`.

## Execucao basica

```bash
python scripts/test_api.py --keyword "smartphone"
```

O script gera a assinatura SHA256, envia a query `productOfferV2` e imprime o JSON da resposta.

## Ajustes de consulta

- `--keyword`: termo de busca.
- `--page`: pagina atual.
- `--limit`: limite de itens por pagina.
- `--no-proxy`: ignora proxies definidos no ambiente.
- `--fields`: lista de campos GraphQL (um por linha).

Exemplo com campos customizados:

```bash
python scripts/test_api.py --fields $'itemId\nproductName\ncommissionRate\nofferLink'
```
