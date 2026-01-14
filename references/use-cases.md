# Casos de uso

## 1) Bot de ofertas diárias no Telegram

Fluxo:
1. Buscar ofertas top
2. Filtrar por comissão
3. Gerar link curto com subIds
4. Enviar no canal

Exemplo (resumido):
```python
query = """
query {
  productOfferV2(sortType: 5, page: 1, limit: 20) {
    nodes { productName commissionRate priceMin imageUrl offerLink }
  }
}
"""
products = shopee.query(query)["data"]["productOfferV2"]["nodes"]
selected = [p for p in products if p["commissionRate"] > 10]
for product in selected:
    link = shopee.generate_short_link(product["offerLink"], subIds=["telegram", "daily", "oferta", "", ""])
    await telegram_bot.send_offer(CHANNEL_ID, product, link)
```

## 2) Webhook N8N para notificações de conversão

Workflow:
1. Schedule Trigger (a cada hora)
2. HTTP Request - conversionReport
3. Filter - últimas 24h
4. Telegram - notificar novas comissões

Exemplo (Function node):
```javascript
// Constantes nomeadas para melhor legibilidade e manutenibilidade
const SECONDS_IN_DAY = 86400; // 24 horas em segundos
const PURCHASE_QUERY_LIMIT = 500; // Limite configurável de consultas

const now = Math.floor(Date.now() / 1000);
const yesterday = now - SECONDS_IN_DAY;

return {
  json: {
    query: `query {
      conversionReport(
        purchaseTimeStart: ${yesterday}
        purchaseTimeEnd: ${now}
        page: 1
        limit: ${PURCHASE_QUERY_LIMIT}
      ) { nodes { orderId commissionAmount orderStatus } }
    }`
  }
};
```

## 3) Sistema de recomendação por categoria

Exemplo (resumido):
```python
def recommend_by_category(category_id: int, min_commission: float = 5.0):
    query = f"""
    query {{
      productOfferV2(productCatId: {category_id}, listType: 1, sortType: 5, page: 1, limit: 50) {{
        nodes { productName commissionRate commission priceMin sales ratingStar offerLink }
      }}
    }}
    """
    products = shopee.query(query)["data"]["productOfferV2"]["nodes"]
    filtered = [p for p in products if p["commissionRate"] >= min_commission and p["ratingStar"] >= 4.0]
    return sorted(filtered, key=lambda x: x["commission"], reverse=True)
```
