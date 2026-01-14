#!/usr/bin/env python3
"""
Shopee Telegram Bot
Bot para enviar ofertas da Shopee via Telegram com links rastreados
"""

import asyncio
import logging
import os
from typing import List, Optional

try:
    from aiogram import Bot, Dispatcher, F
    from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.filters import Command
    from aiogram.enums import ParseMode
except ImportError:
    print("Instale aiogram: pip install aiogram --break-system-packages")
    raise

# Importar cliente Shopee (ajustar path conforme necessário)
from shopee_client import ShopeeAffiliateClient, ShopeeAPIError

# Configuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_AQUI")
SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID", "SEU_APP_ID")
SHOPEE_SECRET = os.getenv("SHOPEE_SECRET", "SEU_SECRET")

# Inicializar bot e cliente Shopee
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
shopee = ShopeeAffiliateClient(SHOPEE_APP_ID, SHOPEE_SECRET)


# ==================== COMANDOS ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Comando /start - boas-vindas"""
    welcome_text = """
🛍️ *Bot de Ofertas Shopee*

Bem-vindo ao bot de afiliados Shopee!

*Comandos disponíveis:*

🔍 `/buscar <palavra-chave>` - Buscar produtos
📦 `/categoria <id>` - Produtos por categoria
🏪 `/loja <id>` - Produtos de uma loja
⭐ `/top` - Top ofertas com maior comissão
📊 `/relatorio` - Minhas comissões (últimos 7 dias)
❓ `/ajuda` - Ver todos os comandos

*Exemplo:*
`/buscar smartphone`
"""
    
    await message.answer(welcome_text, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("ajuda"))
async def cmd_help(message: Message):
    """Comando /ajuda - lista de comandos"""
    help_text = """
📚 *Comandos Disponíveis*

*Busca de Produtos:*
• `/buscar <palavra-chave>` - Buscar produtos
  Exemplo: `/buscar fone bluetooth`

• `/categoria <id>` - Produtos de uma categoria
  Exemplo: `/categoria 10001`

• `/loja <id>` - Produtos de uma loja específica
  Exemplo: `/loja 84499012`

• `/top` - Top 10 produtos com maior comissão

*Relatórios:*
• `/relatorio` - Suas comissões dos últimos 7 dias
• `/relatorio_mes` - Comissões do mês atual

*Configurações:*
• `/config` - Ver suas configurações
• `/subid <texto>` - Definir seu subId personalizado

*Outras:*
• `/start` - Mensagem de boas-vindas
• `/ajuda` - Esta mensagem
"""
    
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("buscar"))
async def cmd_search(message: Message):
    """Comando /buscar <palavra-chave> - buscar produtos"""
    # Extrair palavra-chave
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Use: `/buscar <palavra-chave>`\nExemplo: `/buscar smartphone`", parse_mode=ParseMode.MARKDOWN)
        return
    
    keyword = args[1]
    user_id = message.from_user.id
    
    await message.answer(f"🔍 Buscando produtos: *{keyword}*...", parse_mode=ParseMode.MARKDOWN)
    
    try:
        # Buscar produtos na Shopee
        result = shopee.search_products(keyword=keyword, sort_type=5, limit=10)
        products = result['data']['productOfferV2']['nodes']
        
        if not products:
            await message.answer("😕 Nenhum produto encontrado.")
            return
        
        # Enviar cada produto
        for product in products:
            await send_product_card(message.chat.id, product, user_id)
            await asyncio.sleep(0.5)  # Evitar flood
        
        await message.answer(f"✅ Encontrados {len(products)} produtos!")
        
    except ShopeeAPIError as e:
        logger.error(f"Erro Shopee API: {e}")
        await message.answer(f"❌ Erro ao buscar produtos: {e}")


@dp.message(Command("categoria"))
async def cmd_category(message: Message):
    """Comando /categoria <id> - buscar por categoria"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Use: `/categoria <id>`\nExemplo: `/categoria 10001`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        category_id = int(args[1])
    except ValueError:
        await message.answer("❌ ID da categoria deve ser um número")
        return
    
    user_id = message.from_user.id
    
    await message.answer(f"🗂️ Buscando produtos da categoria {category_id}...")
    
    try:
        result = shopee.search_products(
            category_id=category_id,
            list_type=1,
            sort_type=5,
            limit=15
        )
        products = result['data']['productOfferV2']['nodes']
        
        if not products:
            await message.answer("😕 Nenhum produto encontrado nesta categoria.")
            return
        
        for product in products:
            await send_product_card(message.chat.id, product, user_id)
            await asyncio.sleep(0.5)
        
        await message.answer(f"✅ {len(products)} produtos encontrados!")
        
    except ShopeeAPIError as e:
        logger.error(f"Erro Shopee API: {e}")
        await message.answer(f"❌ Erro: {e}")


@dp.message(Command("loja"))
async def cmd_shop(message: Message):
    """Comando /loja <id> - produtos de uma loja"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Use: `/loja <id>`\nExemplo: `/loja 84499012`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        shop_id = int(args[1])
    except ValueError:
        await message.answer("❌ ID da loja deve ser um número")
        return
    
    user_id = message.from_user.id
    
    await message.answer(f"🏪 Buscando produtos da loja {shop_id}...")
    
    try:
        result = shopee.search_products(
            shop_id=shop_id,
            list_type=5,
            sort_type=5,
            limit=15
        )
        products = result['data']['productOfferV2']['nodes']
        
        if not products:
            await message.answer("😕 Nenhum produto encontrado nesta loja.")
            return
        
        # Enviar info da loja
        first_product = products[0]
        await message.answer(
            f"🏪 *{first_product['shopName']}*\n"
            f"📦 {len(products)} produtos disponíveis",
            parse_mode=ParseMode.MARKDOWN
        )
        
        for product in products:
            await send_product_card(message.chat.id, product, user_id)
            await asyncio.sleep(0.5)
        
    except ShopeeAPIError as e:
        logger.error(f"Erro Shopee API: {e}")
        await message.answer(f"❌ Erro: {e}")


@dp.message(Command("top"))
async def cmd_top(message: Message):
    """Comando /top - produtos com maior comissão"""
    user_id = message.from_user.id
    
    await message.answer("⭐ Buscando top ofertas com maior comissão...")
    
    try:
        # Buscar produtos mais vendidos
        result = shopee.search_products(sort_type=5, limit=20)
        products = result['data']['productOfferV2']['nodes']
        
        # Filtrar e ordenar por comissão
        top_products = sorted(
            [p for p in products if p['commissionRate'] >= 5.0],
            key=lambda x: x['commissionRate'],
            reverse=True
        )[:10]
        
        if not top_products:
            await message.answer("😕 Nenhuma oferta encontrada no momento.")
            return
        
        await message.answer(f"🔥 *Top {len(top_products)} ofertas!*", parse_mode=ParseMode.MARKDOWN)
        
        for product in top_products:
            await send_product_card(message.chat.id, product, user_id)
            await asyncio.sleep(0.5)
        
    except ShopeeAPIError as e:
        logger.error(f"Erro Shopee API: {e}")
        await message.answer(f"❌ Erro: {e}")


@dp.message(Command("relatorio"))
async def cmd_report(message: Message):
    """Comando /relatorio - comissões dos últimos 7 dias"""
    await message.answer("📊 Gerando relatório de comissões...")
    
    try:
        import time
        end = int(time.time())
        start = end - 7 * 86400  # 7 dias
        
        result = shopee.conversion_report(start, end, limit=500)
        orders = result['data']['conversionReport']['nodes']
        
        if not orders:
            await message.answer("📭 Nenhuma conversão nos últimos 7 dias.")
            return
        
        # Calcular estatísticas
        total_commission = sum(float(o['commissionAmount']) for o in orders)
        total_orders = len(orders)
        avg_commission = total_commission / total_orders if total_orders > 0 else 0
        
        # Contar status
        status_count = {}
        for order in orders:
            status = order['orderStatus']
            status_count[status] = status_count.get(status, 0) + 1
        
        report = f"""
📊 *Relatório - Últimos 7 dias*

💰 *Total em Comissões:* R$ {total_commission:.2f}
📦 *Total de Pedidos:* {total_orders}
📈 *Comissão Média:* R$ {avg_commission:.2f}

*Status dos Pedidos:*
"""
        for status, count in status_count.items():
            report += f"• {status}: {count}\n"
        
        await message.answer(report, parse_mode=ParseMode.MARKDOWN)
        
        # Listar últimos 5 pedidos
        recent_orders = orders[:5]
        await message.answer("*Últimos pedidos:*", parse_mode=ParseMode.MARKDOWN)
        
        for order in recent_orders:
            order_msg = f"""
🛍️ Pedido: `{order['orderId']}`
💵 Comissão: R$ {order['commissionAmount']}
📊 Taxa: {order['commissionRate']}%
🏷️ Produto: {order.get('productName', 'N/A')[:50]}
"""
            await message.answer(order_msg, parse_mode=ParseMode.MARKDOWN)
        
    except ShopeeAPIError as e:
        logger.error(f"Erro Shopee API: {e}")
        await message.answer(f"❌ Erro ao gerar relatório: {e}")


# ==================== FUNÇÕES AUXILIARES ====================

async def send_product_card(chat_id: int, product: dict, user_id: int):
    """Envia card formatado do produto com imagem e link"""
    
    try:
        # Gerar link curto com rastreamento
        sub_ids = [
            "telegram",
            f"user_{user_id}",
            "bot",
            "",
            ""
        ]
        
        link_result = shopee.generate_short_link(
            product['offerLink'],
            sub_ids=sub_ids
        )
        short_link = link_result['data']['generateShortLink']['shortLink']
        
        # Formatar mensagem
        price_min = float(product['priceMin'])
        price_max = float(product['priceMax'])
        commission_rate = float(product['commissionRate'])
        commission = float(product.get('commission', 0))
        
        caption = f"""
🛍️ *{product['productName'][:100]}*

💰 *Preço:* R$ {price_min:.2f}"""
        
        if price_max > price_min:
            caption += f" - R$ {price_max:.2f}"
        
        caption += f"""

📊 *Comissão:* {commission_rate:.1f}%"""
        
        if commission > 0:
            caption += f" (R$ {commission:.2f})"
        
        if product.get('sales'):
            caption += f"""
🔥 *Vendas:* {product['sales']}"""
        
        if product.get('ratingStar'):
            stars = "⭐" * int(product['ratingStar'])
            caption += f"""
{stars} {product['ratingStar']}/5"""
        
        # Botão com link
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Comprar Agora", url=short_link)]
        ])
        
        # Enviar foto com caption
        await bot.send_photo(
            chat_id=chat_id,
            photo=product['imageUrl'],
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Erro ao enviar produto: {e}")
        # Enviar sem imagem em caso de erro
        await bot.send_message(
            chat_id=chat_id,
            text=f"🛍️ {product['productName']}\n{product['offerLink']}"
        )


# ==================== MAIN ====================

async def main():
    """Iniciar bot"""
    logger.info("Bot iniciado!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
