# GraphQL Queries - Biblioteca

Esta página contém queries GraphQL prontas para usar com a API de Afiliados da Shopee.

## Shopee Offers

### Buscar ofertas gerais
```graphql
query {
  shopeeOfferV2(keyword: "smartphone", sortType: 2, page: 1, limit: 10) {
    nodes {
      offerName
      offerLink
      commissionRate
      imageUrl
    }
    pageInfo {
      page
      hasNextPage
    }
  }
}
```

## Shop Offers

### Buscar ofertas de lojas
```graphql
query {
  shopOfferV2(keyword: "loja exemplo", shopType: [1, 4], sortType: 2, page: 1, limit: 10) {
    nodes {
      shopId
      shopName
      commissionRate
      ratingStar
      offerLink
    }
    pageInfo {
      page
      hasNextPage
    }
  }
}
```

## Product Offers

### Buscar ofertas por categoria
```graphql
query {
  productOfferV2(productCatId: 10001, listType: 1, sortType: 5, page: 1, limit: 10) {
    nodes {
      itemId
      productName
      commissionRate
      priceMin
      priceMax
      offerLink
    }
    pageInfo {
      hasNextPage
    }
  }
}
```

### Buscar ofertas por loja
```graphql
query {
  productOfferV2(shopId: 84499012, listType: 5, matchId: 84499012, sortType: 5, page: 1, limit: 10) {
    nodes {
      itemId
      productName
      commissionRate
      offerLink
    }
    pageInfo {
      hasNextPage
    }
  }
}
```

## Reports

### Relatório de conversão (primeira página)
```graphql
query {
  conversionReport(
    purchaseTimeStart: 1600621200
    purchaseTimeEnd: 1601225999
    page: 1
    limit: 500
  ) {
    nodes {
      orderId
      commissionAmount
      orderStatus
      subIds
    }
    pageInfo {
      scrollId
      hasNextPage
    }
  }
}
```

### Relatório de conversão (páginas seguintes)
```graphql
query {
  conversionReport(
    purchaseTimeStart: 1600621200
    purchaseTimeEnd: 1601225999
    scrollId: "scroll_id_da_primeira_query"
    page: 2
    limit: 500
  ) {
    nodes {
      orderId
      commissionAmount
    }
    pageInfo {
      scrollId
      hasNextPage
    }
  }
}
```

### Relatório validado
```graphql
query {
  validatedReport(
    purchaseTimeStart: 1600621200
    purchaseTimeEnd: 1601225999
    page: 1
    limit: 500
  ) {
    nodes {
      orderId
      commissionAmount
      orderStatus
      subIds
    }
    pageInfo {
      scrollId
      hasNextPage
    }
  }
}
```

## Mutations

### Gerar link curto
```graphql
mutation {
  generateShortLink(
    input: {
      originUrl: "https://shopee.com.br/product-i.123456.789012"
      subIds: ["telegram", "bot01", "grupo-ofertas", "", ""]
    }
  ) {
    shortLink
  }
}
```
