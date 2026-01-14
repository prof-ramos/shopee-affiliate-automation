#!/usr/bin/env python3
"""
Shopee Webhook Handler
Handler Flask para receber webhooks do N8N e processar ofertas Shopee
"""

import json
import logging
from typing import Dict, List, Optional

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Instale Flask: pip install flask --break-system-packages")
    raise

from shopee_client import ShopeeAffiliateClient, ShopeeAPIError
import os

# Configuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cliente Shopee
SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID", "SEU_APP_ID")
SHOPEE_SECRET = os.getenv("SHOPEE_SECRET", "SEU_SECRET")
shopee = ShopeeAffiliateClient(SHOPEE_APP_ID, SHOPEE_SECRET)


# ==================== ENDPOINTS ====================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "shopee-webhook-handler"})


@app.route("/webhook/search-products", methods=["POST"])
def webhook_search_products():
    """
    Webhook para buscar produtos
    
    Payload esperado:
    {
        "keyword": "smartphone",
        "limit": 10,
        "sort_type": 5,
        "min_commission": 5.0
    }
    
    Retorna lista de produtos formatados para N8N
    """
    try:
        data = request.get_json()
        
        keyword = data.get("keyword")
        limit = data.get("limit", 10)
        sort_type = data.get("sort_type", 5)
        min_commission = data.get("min_commission", 0.0)
        
        if not keyword:
            return jsonify({"error": "keyword é obrigatório"}), 400
        
        # Buscar produtos
        result = shopee.search_products(
            keyword=keyword,
            sort_type=sort_type,
            limit=limit
        )
        
        products = result['data']['productOfferV2']['nodes']
        
        # Filtrar por comissão mínima
        filtered_products = [
            p for p in products 
            if float(p['commissionRate']) >= min_commission
        ]
        
        # Formatar resposta para N8N
        formatted_products = []
        for product in filtered_products:
            formatted_products.append({
                "itemId": product['itemId'],
                "name": product['productName'],
                "price_min": float(product['priceMin']),
                "price_max": float(product['priceMax']),
                "commission_rate": float(product['commissionRate']),
                "commission_value": float(product.get('commission', 0)),
                "sales": product.get('sales', 0),
                "rating": product.get('ratingStar', 0),
                "image_url": product['imageUrl'],
                "offer_link": product['offerLink'],
                "shop_name": product.get('shopName', '')
            })
        
        return jsonify({
            "success": True,
            "total": len(filtered_products),
            "products": formatted_products
        })
        
    except ShopeeAPIError as e:
        logger.error(f"Shopee API Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "code": e.code
        }), 500
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/webhook/generate-links", methods=["POST"])
def webhook_generate_links():
    """
    Webhook para gerar links curtos em lote
    
    Payload esperado:
    {
        "products": [
            {
                "url": "https://shopee.com.br/...",
                "sub_ids": ["telegram", "bot", "user123", "", ""]
            }
        ]
    }
    
    Retorna lista de links curtos gerados
    """
    try:
        data = request.get_json()
        products = data.get("products", [])
        
        if not products:
            return jsonify({"error": "Lista de products é obrigatória"}), 400
        
        results = []
        
        for product in products:
            url = product.get("url")
            sub_ids = product.get("sub_ids", ["", "", "", "", ""])
            
            if not url:
                results.append({
                    "success": False,
                    "error": "URL não fornecida"
                })
                continue
            
            try:
                link_result = shopee.generate_short_link(url, sub_ids)
                short_link = link_result['data']['generateShortLink']['shortLink']
                
                results.append({
                    "success": True,
                    "original_url": url,
                    "short_link": short_link,
                    "sub_ids": sub_ids
                })
            except ShopeeAPIError as e:
                results.append({
                    "success": False,
                    "original_url": url,
                    "error": str(e)
                })
        
        return jsonify({
            "total": len(results),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/webhook/conversion-report", methods=["POST"])
def webhook_conversion_report():
    """
    Webhook para gerar relatório de conversão
    
    Payload esperado:
    {
        "start_timestamp": 1600000000,
        "end_timestamp": 1600100000,
        "max_pages": 5
    }
    
    Retorna relatório consolidado
    """
    try:
        data = request.get_json()
        
        start = data.get("start_timestamp")
        end = data.get("end_timestamp")
        max_pages = data.get("max_pages", 5)
        
        if not start or not end:
            return jsonify({
                "error": "start_timestamp e end_timestamp são obrigatórios"
            }), 400
        
        # Buscar todas as páginas
        all_orders = shopee.fetch_all_pages(
            shopee.conversion_report,
            max_pages=max_pages,
            start_timestamp=start,
            end_timestamp=end
        )
        
        # Calcular estatísticas
        total_commission = sum(float(o['commissionAmount']) for o in all_orders)
        total_orders = len(all_orders)
        
        # Agrupar por status
        by_status = {}
        for order in all_orders:
            status = order['orderStatus']
            if status not in by_status:
                by_status[status] = {
                    "count": 0,
                    "total_commission": 0.0
                }
            by_status[status]["count"] += 1
            by_status[status]["total_commission"] += float(order['commissionAmount'])
        
        # Agrupar por subId (canal)
        by_channel = {}
        for order in all_orders:
            sub_ids = order.get('subIds', [])
            channel = sub_ids[0] if sub_ids else "unknown"
            
            if channel not in by_channel:
                by_channel[channel] = {
                    "count": 0,
                    "total_commission": 0.0
                }
            by_channel[channel]["count"] += 1
            by_channel[channel]["total_commission"] += float(order['commissionAmount'])
        
        return jsonify({
            "success": True,
            "period": {
                "start": start,
                "end": end
            },
            "summary": {
                "total_orders": total_orders,
                "total_commission": round(total_commission, 2),
                "average_commission": round(total_commission / total_orders if total_orders > 0 else 0, 2)
            },
            "by_status": by_status,
            "by_channel": by_channel,
            "orders": all_orders[:100]  # Limitar a 100 pedidos na resposta
        })
        
    except ShopeeAPIError as e:
        logger.error(f"Shopee API Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "code": e.code
        }), 500
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/webhook/top-offers", methods=["POST"])
def webhook_top_offers():
    """
    Webhook para buscar top ofertas com maior comissão
    
    Payload esperado:
    {
        "category_id": 10001,  // opcional
        "shop_id": 84499012,   // opcional
        "min_commission": 5.0,
        "min_rating": 4.0,
        "limit": 20
    }
    
    Retorna produtos ordenados por comissão
    """
    try:
        data = request.get_json()
        
        category_id = data.get("category_id")
        shop_id = data.get("shop_id")
        min_commission = data.get("min_commission", 5.0)
        min_rating = data.get("min_rating", 0.0)
        limit = data.get("limit", 20)
        
        # Buscar produtos
        result = shopee.search_products(
            category_id=category_id,
            shop_id=shop_id,
            sort_type=5,  # Mais vendidos
            limit=limit * 2  # Buscar mais para filtrar
        )
        
        products = result['data']['productOfferV2']['nodes']
        
        # Filtrar e ordenar
        filtered = [
            p for p in products
            if float(p['commissionRate']) >= min_commission 
            and float(p.get('ratingStar', 0)) >= min_rating
        ]
        
        sorted_products = sorted(
            filtered,
            key=lambda x: float(x['commissionRate']),
            reverse=True
        )[:limit]
        
        # Formatar resposta
        formatted = []
        for product in sorted_products:
            formatted.append({
                "itemId": product['itemId'],
                "name": product['productName'],
                "price_min": float(product['priceMin']),
                "price_max": float(product['priceMax']),
                "commission_rate": float(product['commissionRate']),
                "commission_value": float(product.get('commission', 0)),
                "sales": product.get('sales', 0),
                "rating": product.get('ratingStar', 0),
                "image_url": product['imageUrl'],
                "offer_link": product['offerLink']
            })
        
        return jsonify({
            "success": True,
            "total": len(formatted),
            "filters": {
                "min_commission": min_commission,
                "min_rating": min_rating
            },
            "products": formatted
        })
        
    except ShopeeAPIError as e:
        logger.error(f"Shopee API Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "code": e.code
        }), 500
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== MAIN ====================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting webhook handler on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
