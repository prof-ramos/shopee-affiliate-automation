# Shopee Affiliate Automation - README

## Instalação

### 1. Instalar Dependências Python

```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais
```

### 3. Obter Credenciais Shopee

1. Acesse a plataforma de afiliados Shopee
2. Solicite acesso à Open API (se ainda não tiver)
3. Obtenha seu `APP_ID` e `SECRET`
4. Configure no arquivo `.env`

## Uso Rápido

### Cliente Python

```python
from scripts.shopee_client import ShopeeAffiliateClient

# Inicializar
client = ShopeeAffiliateClient(
    app_id="SEU_APP_ID",
    secret="SEU_SECRET"
)

# Buscar produtos
result = client.search_products(keyword="smartphone", limit=10)
products = result['data']['productOfferV2']['nodes']

# Gerar link curto
link = client.generate_short_link(
    products[0]['offerLink'],
    sub_ids=["telegram", "bot", "teste", "", ""]
)
print(link['data']['generateShortLink']['shortLink'])
```

### Bot Telegram

```bash
# Configurar token no .env
TELEGRAM_BOT_TOKEN=seu_token
SHOPEE_APP_ID=seu_app_id
SHOPEE_SECRET=seu_secret

# Executar bot
python scripts/telegram_bot.py
```

### Webhook Handler (para N8N)

```bash
# Configurar no .env
PORT=5000
SHOPEE_APP_ID=seu_app_id
SHOPEE_SECRET=seu_secret

# Executar servidor
python scripts/webhook_handler.py

# Endpoints disponíveis:
# POST /webhook/search-products
# POST /webhook/generate-links
# POST /webhook/conversion-report
# POST /webhook/top-offers
```

### N8N Workflows

1. Abrir N8N
2. Importar `references/n8n-workflows.json`
3. Configurar variáveis de ambiente no N8N:
   - `SHOPEE_APP_ID`
   - `SHOPEE_SECRET`
   - `TELEGRAM_CHAT_ID` (para workflows com Telegram)
4. Ativar workflows

## Estrutura de Arquivos

```
shopee-affiliate-automation/
├── SKILL.md                      # Documentação principal da skill
├── requirements.txt              # Dependências Python
├── .env.example                  # Template de variáveis de ambiente
├── scripts/
│   ├── shopee_client.py         # Cliente Python completo
│   ├── telegram_bot.py          # Bot Telegram
│   └── webhook_handler.py       # Handler Flask para N8N
├── references/
│   ├── n8n-workflows.json       # Workflows prontos
│   ├── graphql-queries.md       # Biblioteca de queries
│   └── categories.md            # IDs de categorias
└── README.md                     # Este arquivo
```

## Exemplos de Uso

Ver `SKILL.md` para exemplos completos de:
- Busca de produtos por categoria
- Geração de links rastreados
- Integração com Telegram
- Workflows N8N
- Relatórios de conversão

## Suporte

- Documentação API: https://open-api.affiliate.shopee.com.br/explorer
- Issues: Consulte Claude Code com esta skill ativada
