# Biblioteca de Queries GraphQL - Shopee Affiliate API

Coleção de queries prontas para copiar e usar.

## Índice

1. [Busca de Ofertas](#busca-de-ofertas)
2. [Produtos por Categoria](#produtos-por-categoria)
3. [Produtos por Loja](#produtos-por-loja)
4. [Geração de Links](#geração-de-links)
5. [Relatórios](#relatórios)

---

## Busca de Ofertas

### Buscar Produtos por Palavra-chave

```graphql
query SearchProducts($keyword: String!, $page: Int!, $limit: Int!) {
  productOfferV2(keyword: $keyword, sortType: 5, page: $page, limit: $limit) {
    nodes {
      itemId
      productName
      commissionRate
      priceMin
      priceMax
      sales
      ratingStar
      imageUrl
      offerLink
      shopName
      shopType
    }
    pageInfo {
      page
      limit
      hasNextPage
    }
  }
}
```

**Variáveis:**
```json
{
  "keyword": "smartphone",
  "page": 1,
  "limit": 20
}
```

---

### Buscar Ofertas Gerais Shopee

```graphql
query ShopeeOffers($keyword: String!) {
  shopeeOfferV2(keyword: $keyword, sortType: 2, page: 1, limit: 10) {
    nodes {
      commissionRate
      imageUrl
      offerLink
      offerName
      offerType
    }
    pageInfo {
      hasNextPage
    }
  }
}
```

---

### Buscar Lojas

```graphql
query SearchShops($keyword: String!, $types: [Int!]!) {
  shopOfferV2(keyword: $keyword, shopType: $types, sortType: 2, page: 1, limit: 10) {
    nodes {
      shopId
      shopName
      commissionRate
      ratingStar
      remainingBudget
      offerLink
      bannerInfo {
        count
        banners {
          imageUrl
          imageWidth
          imageHeight
        }
      }
    }
    pageInfo {
      hasNextPage
    }
  }
}
```

**Tipos de Loja:**
- `[1]` - Mall
- `[4]` - Preferred
- `[1, 4]` - Ambos

---

## Produtos por Categoria

### Buscar por Categoria ID

```graphql
query ProductsByCategory($catId: Int!, $page: Int!, $limit: Int!) {
  productOfferV2(
    productCatId: $catId
    listType: 1
    sortType: 5
    page: $page
    limit: $limit
  ) {
    nodes {
      itemId
      productName
      commissionRate
      sellerCommissionRate
      shopeeCommissionRate
      commission
      priceMin
      priceMax
      sales
      ratingStar
      imageUrl
      offerLink
      productCatIds
    }
    pageInfo {
      page
      hasNextPage
    }
  }
}
```

**Variáveis:**
```json
{
  "catId": 10001,
  "page": 1,
  "limit": 50
}
```

---

### Top Produtos de uma Categoria

```graphql
query TopCategoryProducts($catId: Int!) {
  productOfferV2(
    productCatId: $catId
    listType: 1
    sortType: 5
    page: 1
    limit: 20
  ) {
    nodes {
      productName
      commissionRate
      commission
      priceMin
      sales
      ratingStar
      imageUrl
      offerLink
    }
  }
}
```

---

## Produtos por Loja

### Listar Produtos de uma Loja

```graphql
query ShopProducts($shopId: Int!, $page: Int!) {
  productOfferV2(
    shopId: $shopId
    listType: 5
    matchId: $shopId
    sortType: 5
    page: $page
    limit: 20
  ) {
    nodes {
      itemId
      productName
      commissionRate
      sellerCommissionRate
      shopeeCommissionRate
      commission
      priceMin
      priceMax
      sales
      offerLink
    }
    pageInfo {
      hasNextPage
    }
  }
}
```

**Variáveis:**
```json
{
  "shopId": 84499012,
  "page": 1
}
```

---

### Top Produtos da Loja com Alta Comissão

```graphql
query TopShopProducts($shopId: Int!) {
  productOfferV2(
    shopId: $shopId
    listType: 5
    matchId: $shopId
    sortType: 5
    page: 1
    limit: 30
  ) {
    nodes {
      productName
      commissionRate
      commission
      priceMin
      sales
      ratingStar
      offerLink
    }
  }
}
```

---

## Geração de Links

### Gerar Link Curto Simples

```graphql
mutation GenerateLink($url: String!) {
  generateShortLink(input: { originUrl: $url, subIds: ["", "", "", "", ""] }) {
    shortLink
  }
}
```

**Variáveis:**
```json
{
  "url": "https://shopee.com.br/product-i.123456.789012"
}
```

---

### Gerar Link com Rastreamento Completo

```graphql
mutation GenerateTrackedLink($url: String!, $subIds: [String!]!) {
  generateShortLink(input: { originUrl: $url, subIds: $subIds }) {
    shortLink
  }
}
```

**Variáveis:**
```json
{
  "url": "https://shopee.com.br/product-i.123456.789012",
  "subIds": ["telegram", "user_123", "grupo_ofertas", "202501", "promo"]
}
```

**Estrutura de SubIds Recomendada:**
- `subIds[0]` - Canal (telegram, whatsapp, instagram)
- `subIds[1]` - Identificador do usuário/grupo
- `subIds[2]` - Campanha ou tipo de conteúdo
- `subIds[3]` - Data ou período
- `subIds[4]` - Extra (promo, cupom, etc)

---

## Relatórios

### Relatório de Conversão - Primeira Página

```graphql
query ConversionReport($start: Int!, $end: Int!) {
  conversionReport(
    purchaseTimeStart: $start
    purchaseTimeEnd: $end
    page: 1
    limit: 500
  ) {
    nodes {
      orderId
      purchaseTime
      commissionRate
      commissionAmount
      orderStatus
      subIds
      productName
      itemPrice
    }
    pageInfo {
      page
      limit
      hasNextPage
      scrollId
    }
  }
}
```

**Variáveis (últimos 7 dias):**
```json
{
  "start": 1609459200,
  "end": 1610064000
}
```

---

### Relatório de Conversão - Páginas Seguintes

```graphql
query ConversionReportPaginated($start: Int!, $end: Int!, $scrollId: String!, $page: Int!) {
  conversionReport(
    purchaseTimeStart: $start
    purchaseTimeEnd: $end
    scrollId: $scrollId
    page: $page
    limit: 500
  ) {
    nodes {
      orderId
      commissionAmount
      orderStatus
      subIds
    }
    pageInfo {
      hasNextPage
      scrollId
    }
  }
}
```

**IMPORTANTE:** scrollId expira em 30 segundos!

---

### Relatório Validado (Comissões Confirmadas)

```graphql
query ValidatedReport($start: Int!, $end: Int!) {
  validatedReport(
    purchaseTimeStart: $start
    purchaseTimeEnd: $end
    page: 1
    limit: 500
  ) {
    nodes {
      orderId
      purchaseTime
      commissionRate
      commissionAmount
      orderStatus
      subIds
      productName
      itemPrice
    }
    pageInfo {
      hasNextPage
      scrollId
    }
  }
}
```

---

## Queries Combinadas

### Buscar + Gerar Links (Python Example)

```python
# 1. Buscar produtos
search_query = """
query {
  productOfferV2(keyword: "fone bluetooth", sortType: 5, page: 1, limit: 10) {
    nodes {
      productName
      offerLink
      commissionRate
    }
  }
}
"""

result = client.query(search_query)
products = result['data']['productOfferV2']['nodes']

# 2. Gerar link para cada produto
for product in products:
    link_mutation = f"""
    mutation {{
      generateShortLink(input: {{
        originUrl: "{product['offerLink']}"
        subIds: ["telegram", "bot", "auto", "", ""]
      }}) {{
        shortLink
      }}
    }}
    """
    
    link_result = client.query(link_mutation)
    short_link = link_result['data']['generateShortLink']['shortLink']
    
    print(f"{product['productName']}: {short_link}")
```

---

## Filtros e Ordenação

### Tipos de Ordenação (sortType)

- `1` - Por relevância
- `2` - Por comissão (descendente)
- `5` - Por mais vendidos (recomendado)

### Tipos de Lista (listType)

- `1` - Por categoria ou palavra-chave
- `5` - Por loja específica

---

## Dicas de Uso

### Rate Limiting

Respeite o limite de 2000 req/hora. Para buscar múltiplas páginas:

```python
import time

pages_to_fetch = 10
for page in range(1, pages_to_fetch + 1):
    result = client.search_products(keyword="smartphone", page=page)
    # Processar resultado
    time.sleep(2)  # Aguardar 2s entre requisições
```

### Paginação com scrollId

```python
# Primeira página
result = client.conversion_report(start, end, page=1)
scroll_id = result['data']['conversionReport']['pageInfo']['scrollId']

# Páginas seguintes (dentro de 30s!)
page = 2
while scroll_id:
    result = client.conversion_report(start, end, page=page, scroll_id=scroll_id)
    
    if not result['data']['conversionReport']['pageInfo']['hasNextPage']:
        break
    
    scroll_id = result['data']['conversionReport']['pageInfo']['scrollId']
    page += 1
    time.sleep(1)
```

### Tratamento de Erros

```python
try:
    result = client.query(query)
except ShopeeAPIError as e:
    if e.code == 10030:  # Rate limit
        print("Rate limit atingido, aguardando...")
        time.sleep(3600)  # 1 hora
    elif e.code == 10020:  # Auth error
        print(f"Erro de autenticação: {e.message}")
    else:
        print(f"Erro {e.code}: {e.message}")
```

---

## Templates para N8N

### Function Node - Assinatura

```javascript
const crypto = require('crypto');

const appId = $env.SHOPEE_APP_ID;
const secret = $env.SHOPEE_SECRET;
const query = $json.query;

const payload = { query };
const payloadStr = JSON.stringify(payload);
const timestamp = Math.floor(Date.now() / 1000).toString();

const signFactor = `${appId}${timestamp}${payloadStr}${secret}`;
const signature = crypto.createHash('sha256').update(signFactor).digest('hex');

return {
  json: {
    url: 'https://open-api.affiliate.shopee.com.br/graphql',
    headers: {
      'Authorization': `SHA256 Credential=${appId}, Timestamp=${timestamp}, Signature=${signature}`,
      'Content-Type': 'application/json'
    },
    body: payload
  }
};
```

### HTTP Request Node Config

```json
{
  "method": "POST",
  "url": "={{$json.url}}",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "={{$json.headers.Authorization}}"
      },
      {
        "name": "Content-Type",
        "value": "={{$json.headers['Content-Type']}}"
      }
    ]
  },
  "sendBody": true,
  "jsonBody": "={{JSON.stringify($json.body)}}"
}
```
