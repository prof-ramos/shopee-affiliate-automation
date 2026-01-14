---
name: shopee-affiliate-automation
description: Automação completa da API de Afiliados da Shopee com foco em bots Python, workflows N8N e integrações Telegram. Use quando precisar criar bots de afiliados, integrar Shopee com Telegram, automatizar geração de links, buscar ofertas programaticamente, ou construir sistemas de divulgação automática. Suporta autenticação SHA256, paginação com scrollId, rate limiting, e endpoints GraphQL (ofertas, links curtos, relatórios).
---

# Shopee Affiliate Automation

Automação da API de Afiliados da Shopee para criar bots, workflows e integrações.

## Visão geral da API

### Versão
- Shopee Affiliate API v2.0

### Requisitos mínimos
- Python >= 3.9

### Dependências
- `requests>=2.28.0`
- `graphql-core>=3.2.0`

### Segurança de credenciais
- Use variáveis de ambiente (.env)
- Considere secrets manager para produção
- **Nunca hardcode keys** no código

### Endpoint base
`https://open-api.affiliate.shopee.com.br/graphql`

### Método
POST (GraphQL)

### Rate limit
2000 requisições/hora

### Timestamp
Diferença máxima de 10 minutos com o servidor

## Scripts disponíveis

### Python
- `scripts/shopee_client.py` - Cliente Python com autenticação SHA256
- `scripts/telegram_bot.py` - Bot Telegram para envio de ofertas
- `scripts/webhook_handler.py` - Handler para webhooks N8N

### N8N
- `references/n8n-workflows.json` - Workflows prontos para importar

## Início rápido (Python)

Use `scripts/shopee_client.py` como implementação principal. Exemplo mínimo:

```python
from scripts.shopee_client import ShopeeAffiliateClient

try:
    client = ShopeeAffiliateClient(app_id="SUA_APP_ID", secret="SEU_SECRET")
    query = """
    query {
      shopeeOfferV2(keyword: "smartphone", page: 1, limit: 5) {
        nodes { offerName offerLink commissionRate }
      }
    }
    """
    result = client.query(query)
except Exception as e:
    print(f"Erro na API Shopee: {e}")
    # Implemente retry ou fallback conforme necessário
```

## Início rápido (Telegram)

O fluxo básico do bot:
1. Recebe comando ou agendamento
2. Consulta ofertas via API
3. Gera link curto com subIds
4. Envia mensagem formatada

Implementação completa: `scripts/telegram_bot.py`

## Início rápido (N8N)

1. Importe `references/n8n-workflows.json`
2. Configure `SHOPEE_APP_ID` e `SHOPEE_SECRET`
3. Use o Function node de assinatura do workflow
4. Envie ofertas para Telegram ou outro canal

## Referências

- `references/api-endpoints.md` - Documentação detalhada dos endpoints
- `references/graphql-queries.md` - Biblioteca de queries prontas
- `references/categories.md` - IDs de categorias
- `references/use-cases.md` - Casos de uso prontos
- `references/n8n-workflows.json` - Workflows N8N

## Boas práticas

- Rate limit: implemente backoff e cache para reduzir chamadas.
- Paginação: use `scrollId` em relatórios e respeite o timeout de 30s.
- SubIds: mantenha convenção consistente para rastreamento por canal.
- Erros: trate limites, autenticação e parâmetros inválidos.
- Dados: valide campos opcionais e formate valores monetários.

## Tratamento de erros (resumo)

| Código | Erro                      | Ação                                   |
|--------|---------------------------|----------------------------------------|
| 10020  | Erro de autenticação      | Verifique AppId, Secret, timestamp e payload (Invalid Signature, Request Expired, etc) |
| 10030  | Rate limit exceeded       | Aguarde a próxima janela               |
| 10031  | Access deny               | Verifique permissões de acesso         |
| 10032  | Invalid affiliate id      | Valide AppId e credenciais             |
| 10033  | Account is frozen         | Entre em contato com o suporte         |
| 10034  | Affiliate id in black list| Verifique status da conta              |
| 10035  | Sem acesso à API          | Solicite acesso via suporte Shopee     |
| 11001  | Params Error              | Valide parâmetros da query             |

## Recursos externos

- GraphQL Spec: https://graphql.org/
- Telegram Bot API: https://core.telegram.org/bots/api
- N8N Docs: https://docs.n8n.io/
