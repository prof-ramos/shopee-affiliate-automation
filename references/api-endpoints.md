# API Endpoints (Shopee Affiliate)

## Base URL

`https://open-api.affiliate.shopee.com.br/graphql`

## Autenticação

Header obrigatório:
```
Authorization: SHA256 Credential={AppId}, Timestamp={Timestamp}, Signature={Signature}
```

Formula da assinatura:
```
Signature = SHA256(AppId + Timestamp + Payload + Secret)
```

**Nota importante:** A concatenação dos componentes (AppId, Timestamp, Payload, Secret) deve ser feita usando **codificação UTF-8** antes de aplicar SHA256. O resultado deve ser o hash hexadecimal em **minúsculas**.

Passos resumidos:
1. Gere o payload JSON da requisição
2. Calcule o timestamp Unix atual
3. Concatene `AppId + Timestamp + Payload + Secret`
4. Aplique SHA256 e gere o hash hexadecimal minúsculo

## 1) shopeeOfferV2 (Buscar ofertas)

Parâmetros:
- `keyword` (String)
- `sortType` (Int) 1: relevância, 2: comissão descendente
- `page` (Int)
- `limit` (Int, max 500)

Retorno principal:
- `nodes[]` (offerName, offerLink, commissionRate, imageUrl)
- `pageInfo` (page, hasNextPage)

Exemplo:
```graphql
query {
  shopeeOfferV2(keyword: "smartphone", sortType: 2, page: 1, limit: 10) {
    nodes { commissionRate imageUrl offerLink offerName }
    pageInfo { page hasNextPage }
  }
}
```

## 2) shopOfferV2 (Ofertas de lojas)

Parâmetros:
- `keyword` (String) nome da loja
- `shopType` ([Int]) 1: Mall, 4: Preferred
- `sortType` (Int)
- `page`, `limit`
- `shopId` (Int64) Buscar por ID da loja
- `isKeySeller` (Bool) Filtrar ofertas de key sellers
- `sellerCommCoveRatio` (String) Razão de produtos com comissão

Retorno principal:
- `nodes[]` (shopId, shopName, commissionRate, ratingStar, offerLink)

### Exemplo shopOfferV2

```graphql
query {
  shopOfferV2(
    keyword: "loja exemplo"
    shopType: [1, 4]
    sortType: 2
    page: 1
    limit: 10
  ) {
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

## 3) productOfferV2 (Ofertas de produtos)

Parâmetros:
- `keyword` (String)
- `productCatId` (Int)
- `shopId` (Int)
- `itemId` (Int64) Buscar por ID do produto
- `listType` (Int) 1: categoria, 5: loja
- `matchId` (Int64) ID correspondente para listType específico
- `sortType` (Int) 5: mais vendidos
- `page`, `limit`
- `isAMSOffer` (Bool) Filtrar ofertas com comissão de vendedor
- `isKeySeller` (Bool) Filtrar ofertas de key sellers

Retorno principal:
- `nodes[]` (itemId, productName, commissionRate, commission, priceMin, priceMax, sales, ratingStar, offerLink)

Exemplo por categoria:
```graphql
query {
  productOfferV2(productCatId: 10001, listType: 1, sortType: 5, page: 1, limit: 20) {
    nodes { itemId productName commissionRate priceMin priceMax sales offerLink }
    pageInfo { hasNextPage }
  }
}
```

Exemplo por loja:
```graphql
query {
  productOfferV2(shopId: 84499012, listType: 5, matchId: 84499012, sortType: 5, page: 1, limit: 10) {
    nodes { itemId productName commissionRate commission priceMin offerLink }
  }
}
```

## 4) generateShortLink (Gerar link curto)

Input:
- `originUrl` (String!)
- `subIds` ([String]) **até 5 subIds**
  - Máximo de 5 elementos
  - Aceita menos de 5 elementos (não requer exatamente 5)
  - Strings não-vazias (empty strings não permitidas)

Retorno:
- `shortLink` (String!)

Exemplo:
```graphql
mutation {
  generateShortLink(
    input: {
      originUrl: "https://shopee.com.br/product-i.123456.789012"
      subIds: ["telegram", "bot01", "grupo-ofertas", "extra4", "extra5"]
    }
  ) { shortLink }
}
```

## 5) conversionReport (Relatório de conversão)

Parâmetros:
- `purchaseTimeStart` (Int!)
- `purchaseTimeEnd` (Int!)
- `page` (Int!)
- `limit` (Int!, max 500)
- `scrollId` (String) para páginas seguintes

Retorno principal:
- `nodes[]` (orderId, purchaseTime, commissionRate, commissionAmount, orderStatus, subIds)
- `pageInfo` (scrollId, hasNextPage)

### ⚠️ AVISO IMPORTANTE - scrollId

**O scrollId expira em 30 segundos!**
- Se expirado, execute a query inicial SEM scrollId novamente
- **NÃO faça queries paralelas usando o mesmo scrollId**

### Paginação com scrollId:
1. Primeira query sem scrollId retorna o primeiro scrollId
2. Queries seguintes devem usar o scrollId recebido
3. scrollId expira em 30 segundos
4. Queries sem scrollId requerem intervalo > 30s

Exemplo primeira página:
```graphql
query {
  conversionReport(
    purchaseTimeStart: 1600621200
    purchaseTimeEnd: 1601225999
    page: 1
    limit: 500
  ) {
    nodes { orderId commissionAmount orderStatus subIds }
    pageInfo { scrollId hasNextPage }
  }
}
```

Exemplo páginas seguintes:
```graphql
query {
  conversionReport(
    purchaseTimeStart: 1600621200
    purchaseTimeEnd: 1601225999
    scrollId: "abc123xyz..."
    page: 2
    limit: 500
  ) {
    nodes { orderId commissionAmount }
    pageInfo { scrollId hasNextPage }
  }
}
```

## 6) validatedReport (Relatório validado)

Retorna apenas pedidos com status **validado/aprovado**.

### Parâmetros
- `purchaseTimeStart` (Int!) - timestamp Unix início
- `purchaseTimeEnd` (Int!) - timestamp Unix fim
- `page` (Int!) - número da página
- `limit` (Int!, max 500) - itens por página
- `scrollId` (String) - para páginas seguintes

### Retorno
- `nodes[]` - orderId, purchaseTime, commissionRate, commissionAmount, orderStatus, subIds
- `pageInfo` - scrollId, hasNextPage

### Exemplo
```graphql
query {
  validatedReport(
    purchaseTimeStart: 1600621200
    purchaseTimeEnd: 1601225999
    page: 1
    limit: 500
  ) {
    nodes { orderId commissionAmount orderStatus subIds }
    pageInfo { scrollId hasNextPage }
  }
}
```

## Códigos de erro comuns

| Código | Erro                  | Ação                                   |
|--------|-----------------------|----------------------------------------|
| 10020  | Erro de autenticação  | Verifique AppId, Secret, timestamp e payload (Invalid Signature, Request Expired, Invalid Credential, etc) |
| 10030  | Rate limit exceeded   | Aguarde a próxima janela               |
| 10031  | Access deny           | Verifique permissões de acesso         |
| 10032  | Invalid affiliate id  | Valide AppId e credenciais             |
| 10033  | Account is frozen     | Entre em contato com o suporte         |
| 10034  | Affiliate id in black list | Verifique status da conta        |
| 10035  | Sem acesso à API      | Solicite acesso via suporte Shopee     |
| 11001  | Params Error          | Valide parâmetros da query             |
