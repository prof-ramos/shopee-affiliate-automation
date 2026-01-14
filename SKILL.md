---
name: shopee-affiliate-automation
description: Automação completa da API de Afiliados da Shopee com foco em bots Python, workflows N8N e integrações Telegram. Use quando precisar criar bots de afiliados, integrar Shopee com Telegram, automatizar geração de links, buscar ofertas programaticamente, ou construir sistemas de divulgação automática. Suporta autenticação SHA256, paginação com scrollId, rate limiting, e todos os endpoints GraphQL (ofertas, links curtos, relatórios). Ideal para sistemas que precisam buscar produtos, gerar links rastreados, enviar ofertas via Telegram, ou construir dashboards de comissões.
---

# Shopee Affiliate Automation

Automação completa da API de Afiliados da Shopee para criação de bots, workflows e integrações.

## Quando Usar Esta Skill

- Criar bots Python para divulgar ofertas da Shopee
- Integrar API Shopee com Telegram (envio de ofertas, links rastreados)
- Construir workflows N8N para automação de afiliados
- Gerar links curtos com rastreamento personalizado (subIds)
- Buscar ofertas por categoria, loja ou palavra-chave
- Automatizar relatórios de conversão e comissões
- Criar sistemas de busca e recomendação de produtos

## Arquitetura da API

**Endpoint Base:** `https://open-api.affiliate.shopee.com.br/graphql`

**Método:** POST (GraphQL)

**Rate Limit:** 2000 requisições/hora

**Restrição de Timestamp:** Máximo 10 minutos de diferença com o servidor

## Scripts Disponíveis

Esta skill inclui scripts prontos para uso:

### Python
- `scripts/shopee_client.py` - Cliente Python completo com autenticação
- `scripts/telegram_bot.py` - Bot Telegram para enviar ofertas
- `scripts/webhook_handler.py` - Handler para webhooks N8N

### N8N
- `references/n8n-workflows.json` - Workflows prontos para importar

## Autenticação

### Header Authorization

Todas as requisições exigem o header:

```
Authorization: SHA256 Credential={AppId}, Timestamp={Timestamp}, Signature={Signature}
```

### Cálculo da Assinatura

**Fórmula:**
```
Signature = SHA256(AppId + Timestamp + Payload + Secret)
```

**Passos:**
1. Obter payload JSON da requisição
2. Obter timestamp Unix atual
3. Concatenar: `AppId + Timestamp + Payload + Secret`
4. Aplicar SHA256 e gerar hash hexadecimal minúsculo (64 caracteres)

**Exemplo Python:**
```python
import hashlib
import json
import time

def generate_signature(app_id: str, secret: str, payload: dict) -> tuple:
    timestamp = str(int(time.time()))
    payload_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    
    sign_factor = f"{app_id}{timestamp}{payload_str}{secret}"
    signature = hashlib.sha256(sign_factor.encode('utf-8')).hexdigest()
    
    return signature, timestamp

# Uso
app_id = "123456"
secret = "demo"
payload = {"query": "query { shopeeOfferV2(keyword: \"phone\") { nodes { offerName } } }"}

signature, timestamp = generate_signature(app_id, secret, payload)

headers = {
    "Authorization": f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}",
    "Content-Type": "application/json"
}
```

## Endpoints Principais

### 1. Buscar Ofertas da Shopee

**Query:** `shopeeOfferV2`

**Parâmetros:**
- `keyword` (String) - Palavra-chave de busca
- `sortType` (Int) - Tipo de ordenação (1: relevância, 2: comissão descendente)
- `page` (Int) - Número da página (começa em 1)
- `limit` (Int) - Itens por página (max: 500)

**Retorno:**
- `nodes[]` - Lista de ofertas
  - `commissionRate` - Taxa de comissão (%)
  - `imageUrl` - URL da imagem
  - `offerLink` - Link de afiliado
  - `offerName` - Nome da oferta
  - `offerType` - Tipo da oferta
- `pageInfo` - Informações de paginação
  - `hasNextPage` - Indica se há próxima página

**Exemplo:**
```graphql
query {
  shopeeOfferV2(keyword: "smartphone", sortType: 2, page: 1, limit: 10) {
    nodes {
      commissionRate
      imageUrl
      offerLink
      offerName
    }
    pageInfo {
      page
      hasNextPage
    }
  }
}
```

### 2. Buscar Ofertas de Lojas

**Query:** `shopOfferV2`

**Parâmetros:**
- `keyword` (String) - Nome da loja
- `shopType` ([Int]) - Tipos de loja (1: Mall, 4: Preferred)
- `sortType` (Int) - Ordenação
- `page`, `limit` - Paginação

**Retorno:**
- `nodes[]`
  - `shopId` - ID da loja
  - `shopName` - Nome da loja
  - `commissionRate` - Taxa de comissão
  - `ratingStar` - Avaliação (estrelas)
  - `remainingBudget` - Orçamento restante
  - `offerLink` - Link da loja
  - `bannerInfo` - Banners da loja

### 3. Buscar Ofertas de Produtos

**Query:** `productOfferV2`

**Parâmetros:**
- `keyword` (String) - Palavra-chave
- `productCatId` (Int) - ID da categoria
- `shopId` (Int) - ID da loja específica
- `listType` (Int) - Tipo de lista (1: categoria, 5: loja)
- `sortType` (Int) - Ordenação (5: mais vendidos)
- `page`, `limit` - Paginação

**Retorno:**
- `nodes[]`
  - `itemId` - ID do item
  - `productName` - Nome do produto
  - `commissionRate` - Taxa de comissão total
  - `sellerCommissionRate` - Taxa do vendedor
  - `shopeeCommissionRate` - Taxa da Shopee
  - `commission` - Valor da comissão (R$)
  - `priceMin`, `priceMax` - Faixa de preço
  - `sales` - Quantidade vendida
  - `ratingStar` - Avaliação
  - `imageUrl` - Imagem do produto
  - `offerLink` - Link de afiliado

**Exemplo por Categoria:**
```graphql
query {
  productOfferV2(productCatId: 10001, listType: 1, sortType: 5, page: 1, limit: 20) {
    nodes {
      itemId
      productName
      commissionRate
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

**Exemplo por Loja:**
```graphql
query {
  productOfferV2(shopId: 84499012, listType: 5, matchId: 84499012, sortType: 5, page: 1, limit: 10) {
    nodes {
      itemId
      productName
      commissionRate
      commission
      priceMin
      offerLink
    }
  }
}
```

### 4. Gerar Link Curto

**Mutation:** `generateShortLink`

**Input:**
- `originUrl` (String!) - URL original do produto/loja Shopee
- `subIds` ([String]) - Array de até 5 subIds para rastreamento personalizado

**Retorno:**
- `shortLink` (String!) - Link curto gerado

**Exemplo:**
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

**Uso de subIds:**
- Até 5 subIds personalizados
- Use para rastrear fonte (ex: "telegram", "whatsapp", "instagram")
- Aparecem no relatório de conversão para análise de canais

### 5. Relatório de Conversão

**Query:** `conversionReport`

**Parâmetros:**
- `purchaseTimeStart` (Int!) - Timestamp início (Unix)
- `purchaseTimeEnd` (Int!) - Timestamp fim (Unix)
- `page` (Int!) - Número da página
- `limit` (Int!) - Itens por página (max: 500)
- `scrollId` (String) - Para páginas seguintes (expira em 30s)

**Retorno:**
- `nodes[]`
  - `orderId` - ID do pedido
  - `purchaseTime` - Timestamp da compra
  - `commissionRate` - Taxa de comissão
  - `commissionAmount` - Valor da comissão (R$)
  - `orderStatus` - Status do pedido
  - `subIds` - SubIds usados no link
- `pageInfo`
  - `scrollId` - Para próxima página (válido por 30s)
  - `hasNextPage` - Indica se há mais páginas

**IMPORTANTE - Paginação com scrollId:**

1. **Primeira query:** Não usa scrollId, retorna primeira página + scrollId
2. **Queries seguintes:** Use o scrollId retornado para buscar próximas páginas
3. **Tempo limite:** scrollId expira em 30 segundos
4. **Intervalo:** Queries sem scrollId requerem >30s de intervalo

**Exemplo Primeira Página:**
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

**Exemplo Páginas Seguintes:**
```graphql
query {
  conversionReport(
    purchaseTimeStart: 1600621200
    purchaseTimeEnd: 1601225999
    scrollId: "abc123xyz..."
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

### 6. Relatório Validado

**Query:** `validatedReport`

Parâmetros e estrutura similar ao `conversionReport`, mas retorna apenas pedidos validados (comissões confirmadas).

## Integração Python

Ver `scripts/shopee_client.py` para cliente completo.

**Estrutura básica:**
```python
import requests
import hashlib
import json
import time

class ShopeeAffiliateClient:
    BASE_URL = "https://open-api.affiliate.shopee.com.br/graphql"
    
    def __init__(self, app_id: str, secret: str):
        self.app_id = app_id
        self.secret = secret
    
    def _sign(self, payload: dict) -> dict:
        timestamp = str(int(time.time()))
        payload_str = json.dumps(payload, separators=(',', ':'))
        sign_factor = f"{self.app_id}{timestamp}{payload_str}{self.secret}"
        signature = hashlib.sha256(sign_factor.encode()).hexdigest()
        
        return {
            "Authorization": f"SHA256 Credential={self.app_id}, Timestamp={timestamp}, Signature={signature}",
            "Content-Type": "application/json"
        }
    
    def query(self, query: str, variables: dict = None):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        headers = self._sign(payload)
        response = requests.post(self.BASE_URL, json=payload, headers=headers)
        return response.json()
```

## Integração Telegram

Ver `scripts/telegram_bot.py` para bot completo.

**Fluxo típico:**
1. Bot recebe comando `/ofertas smartphone`
2. Bot consulta `productOfferV2` na API Shopee
3. Para cada produto, gera link curto com subIds rastreados
4. Envia mensagem formatada com imagem, preço e link

**Exemplo de envio:**
```python
async def send_offer(bot, chat_id, product):
    # Gerar link curto
    short_link = shopee_client.generate_short_link(
        product['offerLink'],
        subIds=["telegram", f"user_{chat_id}", "bot", "", ""]
    )
    
    # Formatar mensagem
    message = f"""
🛍️ *{product['productName']}*

💰 Preço: R$ {product['priceMin']} - R$ {product['priceMax']}
📊 Comissão: {product['commissionRate']}%
⭐ Avaliação: {product['ratingStar']}/5
🔥 Vendas: {product['sales']}

🔗 Link: {short_link['data']['generateShortLink']['shortLink']}
"""
    
    await bot.send_photo(
        chat_id=chat_id,
        photo=product['imageUrl'],
        caption=message,
        parse_mode='Markdown'
    )
```

## Integração N8N

Ver `references/n8n-workflows.json` para workflows prontos.

**Nós N8N recomendados:**
1. **Trigger:** Webhook, Schedule, ou Telegram
2. **HTTP Request:** POST para API Shopee com autenticação
3. **Function:** Calcular assinatura SHA256
4. **Split In Batches:** Processar múltiplas ofertas
5. **Telegram:** Enviar ofertas formatadas

**Exemplo Function Node (Assinatura):**
```javascript
const crypto = require('crypto');

const appId = $env.SHOPEE_APP_ID;
const secret = $env.SHOPEE_SECRET;
const payload = JSON.stringify($json.body);
const timestamp = Math.floor(Date.now() / 1000).toString();

const signFactor = `${appId}${timestamp}${payload}${secret}`;
const signature = crypto.createHash('sha256').update(signFactor).digest('hex');

return {
  json: {
    authorization: `SHA256 Credential=${appId}, Timestamp=${timestamp}, Signature=${signature}`,
    payload: $json.body
  }
};
```

## Tratamento de Erros

### Códigos Principais

| Código | Erro                     | Ação                                         |
|--------|--------------------------|----------------------------------------------|
| 10020  | Assinatura inválida      | Verificar AppId, Secret, payload e timestamp |
| 10020  | Request Expired          | Ajustar timestamp (diferença < 10 min)       |
| 10030  | Rate limit exceeded      | Aguardar próxima janela (1 hora)             |
| 10032  | Invalid affiliate id     | Verificar AppId nas credenciais              |
| 10035  | Sem acesso à API         | Solicitar acesso via suporte Shopee          |
| 11001  | Params Error             | Validar parâmetros da query                  |

### Exemplo de Tratamento

```python
def safe_query(client, query, retries=3):
    for attempt in range(retries):
        try:
            result = client.query(query)
            
            if 'errors' in result:
                error_code = result['errors'][0]['extensions']['code']
                
                if error_code == 10030:  # Rate limit
                    print("Rate limit atingido, aguardando 1 hora")
                    time.sleep(3600)
                    continue
                elif error_code == 10020:  # Timestamp/Auth
                    print("Erro de autenticação, verificar credenciais")
                    return None
                else:
                    print(f"Erro {error_code}: {result['errors'][0]['message']}")
                    return None
            
            return result['data']
            
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
```

## Casos de Uso Práticos

### 1. Bot de Ofertas Diárias no Telegram

```python
# 1. Agendar busca diária de ofertas top
# 2. Filtrar por comissão > 10%
# 3. Gerar links rastreados por Telegram
# 4. Enviar para canal/grupo

async def daily_offers():
    query = """
    query {
      productOfferV2(sortType: 5, page: 1, limit: 20) {
        nodes {
          productName
          commissionRate
          priceMin
          imageUrl
          offerLink
        }
      }
    }
    """
    
    result = shopee.query(query)
    products = result['data']['productOfferV2']['nodes']
    
    # Filtrar comissão > 10%
    top_products = [p for p in products if p['commissionRate'] > 10]
    
    for product in top_products:
        # Gerar link
        link_result = shopee.generate_short_link(
            product['offerLink'],
            subIds=["telegram", "daily", "oferta", "", ""]
        )
        
        # Enviar para Telegram
        await telegram_bot.send_offer(CHANNEL_ID, product, link_result)
```

### 2. Webhook N8N para Notificações de Conversão

```javascript
// Workflow N8N
// 1. Schedule Trigger (a cada hora)
// 2. HTTP Request - buscar conversionReport
// 3. Filter - apenas novos pedidos (últimas 24h)
// 4. Telegram - notificar novas comissões

// Function Node - Calcular período
const now = Math.floor(Date.now() / 1000);
const yesterday = now - 86400;

return {
  json: {
    query: `query {
      conversionReport(
        purchaseTimeStart: ${yesterday}
        purchaseTimeEnd: ${now}
        page: 1
        limit: 500
      ) {
        nodes {
          orderId
          commissionAmount
          orderStatus
        }
      }
    }`
  }
};
```

### 3. Sistema de Recomendação por Categoria

```python
def recommend_by_category(category_id: int, min_commission: float = 5.0):
    """Busca produtos de uma categoria com boa comissão"""
    query = f"""
    query {{
      productOfferV2(
        productCatId: {category_id}
        listType: 1
        sortType: 5
        page: 1
        limit: 50
      ) {{
        nodes {{
          productName
          commissionRate
          commission
          priceMin
          sales
          ratingStar
          offerLink
        }}
      }}
    }}
    """
    
    result = shopee.query(query)
    products = result['data']['productOfferV2']['nodes']
    
    # Filtrar e ordenar
    filtered = [
        p for p in products 
        if p['commissionRate'] >= min_commission and p['ratingStar'] >= 4.0
    ]
    
    return sorted(filtered, key=lambda x: x['commission'], reverse=True)
```

## Boas Práticas

### Rate Limiting
- Respeitar limite de 2000 req/hora
- Implementar retry com backoff exponencial
- Cache de ofertas para reduzir chamadas

### Autenticação
- Nunca expor Secret em código cliente
- Validar timestamp antes de cada request
- Renovar assinatura a cada requisição

### Paginação
- Usar scrollId para páginas seguintes
- Respeitar timeout de 30s do scrollId
- Implementar controle de páginas para evitar loops infinitos

### SubIds
- Usar convenção consistente (ex: "telegram|grupo|data")
- Documentar estrutura de rastreamento
- Analisar relatórios por subId para otimizar canais

### Tratamento de Dados
- Validar estrutura de resposta antes de processar
- Lidar com campos opcionais (podem ser null)
- Formatar valores monetários corretamente (centavos -> reais)

## Ferramentas de Desenvolvimento

### API Explorer
Teste queries online: https://open-api.affiliate.shopee.com.br/explorer

### Timestamp Generator
Gere timestamps Unix: https://www.unixtimestamp.com/

### GraphQL Clients
- Python: `gql`, `requests`
- JavaScript: `graphql-request`, `apollo-client`
- N8N: HTTP Request node com custom headers

## Referências Adicionais

- `scripts/shopee_client.py` - Cliente Python completo
- `scripts/telegram_bot.py` - Bot Telegram integrado
- `scripts/webhook_handler.py` - Handler para N8N webhooks
- `references/n8n-workflows.json` - Workflows prontos
- `references/graphql-queries.md` - Biblioteca de queries
- `references/categories.md` - Lista de IDs de categorias

## Recursos Externos

- Documentação oficial: (incluída nesta skill)
- GraphQL Spec: https://graphql.org/
- Telegram Bot API: https://core.telegram.org/bots/api
- N8N Docs: https://docs.n8n.io/
