# Guia de API

## Endpoint base

- `https://open-api.affiliate.shopee.com.br/graphql`
- POST com payload GraphQL

## Modelo de autenticacao

```
Authorization: SHA256 Credential={AppId}, Timestamp={Timestamp}, Signature={Signature}
Signature = SHA256(AppId + Timestamp + Payload + Secret)
```

Detalhes completos em `references/api-endpoints.md`.

## Operacoes principais

- `shopeeOfferV2`: busca ofertas por palavra-chave.
- `shopOfferV2`: busca ofertas por loja.
- `productOfferV2`: busca produtos por categoria ou loja.
- `generateShortLink`: gera links com subIds.
- `conversionReport` / `validatedReport`: relatorios com scrollId.

## Tratamento de erros

Consulte `references/api-endpoints.md` para codigos e acoes.
