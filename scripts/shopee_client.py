#!/usr/bin/env python3
"""
Shopee Affiliate API Client
Cliente Python completo para integração com API de Afiliados Shopee
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

try:
    import requests
except ImportError:
    print("Instale requests: pip install requests --break-system-packages")
    raise


@dataclass
class ShopeeConfig:
    """Configuração do cliente Shopee"""
    app_id: str
    secret: str
    base_url: str = "https://open-api.affiliate.shopee.com.br/graphql"


class ShopeeAffiliateClient:
    """Cliente para API Shopee Affiliate com autenticação SHA256"""
    
    def __init__(self, app_id: str, secret: str):
        self.config = ShopeeConfig(app_id=app_id, secret=secret)
        self.session = requests.Session()
    
    def _generate_signature(self, payload: dict) -> tuple[str, str]:
        """
        Gera assinatura SHA256 para autenticação
        
        Returns:
            tuple: (signature, timestamp)
        """
        timestamp = str(int(time.time()))
        payload_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
        
        # Construir fator de assinatura
        sign_factor = f"{self.config.app_id}{timestamp}{payload_str}{self.config.secret}"
        
        # Gerar hash SHA256
        signature = hashlib.sha256(sign_factor.encode('utf-8')).hexdigest()
        
        return signature, timestamp
    
    def _build_headers(self, payload: dict) -> dict:
        """Constrói headers com autenticação"""
        signature, timestamp = self._generate_signature(payload)
        
        return {
            "Authorization": f"SHA256 Credential={self.config.app_id}, Timestamp={timestamp}, Signature={signature}",
            "Content-Type": "application/json"
        }
    
    def query(
        self, 
        query: str, 
        variables: Optional[dict] = None,
        operation_name: Optional[str] = None
    ) -> dict:
        """
        Executa query GraphQL na API Shopee
        
        Args:
            query: Query GraphQL
            variables: Variáveis da query (opcional)
            operation_name: Nome da operação (opcional, obrigatório se múltiplas operações)
        
        Returns:
            dict: Resposta da API
        
        Raises:
            ShopeeAPIError: Em caso de erro da API
        """
        payload = {"query": query}
        
        if variables:
            payload["variables"] = variables
        
        if operation_name:
            payload["operationName"] = operation_name
        
        headers = self._build_headers(payload)
        
        try:
            response = self.session.post(
                self.config.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Verificar erros da API
            if 'errors' in result:
                error = result['errors'][0]
                code = error.get('extensions', {}).get('code', 0)
                message = error.get('message', 'Unknown error')
                raise ShopeeAPIError(code, message, error)
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise ShopeeAPIError(0, f"Request failed: {str(e)}", {})
    
    # ==================== OFERTAS ====================
    
    def search_shopee_offers(
        self,
        keyword: str,
        sort_type: int = 2,
        page: int = 1,
        limit: int = 10
    ) -> dict:
        """
        Busca ofertas gerais da Shopee
        
        Args:
            keyword: Palavra-chave de busca
            sort_type: 1 (relevância) ou 2 (comissão desc)
            page: Número da página (começa em 1)
            limit: Itens por página (max 500)
        """
        query = """
        query($keyword: String!, $sortType: Int!, $page: Int!, $limit: Int!) {
          shopeeOfferV2(keyword: $keyword, sortType: $sortType, page: $page, limit: $limit) {
            nodes {
              commissionRate
              imageUrl
              offerLink
              offerName
              offerType
            }
            pageInfo {
              page
              limit
              hasNextPage
            }
          }
        }
        """
        
        variables = {
            "keyword": keyword,
            "sortType": sort_type,
            "page": page,
            "limit": limit
        }
        
        return self.query(query, variables)
    
    def search_shop_offers(
        self,
        keyword: str,
        shop_types: List[int] = [1, 4],
        sort_type: int = 2,
        page: int = 1,
        limit: int = 10
    ) -> dict:
        """
        Busca ofertas de lojas específicas
        
        Args:
            keyword: Nome da loja
            shop_types: [1] Mall, [4] Preferred, [1,4] Ambos
            sort_type: Tipo de ordenação
            page: Número da página
            limit: Itens por página
        """
        query = """
        query($keyword: String!, $shopTypes: [Int!]!, $sortType: Int!, $page: Int!, $limit: Int!) {
          shopOfferV2(keyword: $keyword, shopType: $shopTypes, sortType: $sortType, page: $page, limit: $limit) {
            nodes {
              commissionRate
              shopId
              shopName
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
              page
              limit
              hasNextPage
            }
          }
        }
        """
        
        variables = {
            "keyword": keyword,
            "shopTypes": shop_types,
            "sortType": sort_type,
            "page": page,
            "limit": limit
        }
        
        return self.query(query, variables)
    
    def search_products(
        self,
        keyword: Optional[str] = None,
        category_id: Optional[int] = None,
        shop_id: Optional[int] = None,
        list_type: int = 1,
        sort_type: int = 5,
        page: int = 1,
        limit: int = 10
    ) -> dict:
        """
        Busca ofertas de produtos
        
        Args:
            keyword: Palavra-chave (usado com list_type=1)
            category_id: ID da categoria (usado com list_type=1)
            shop_id: ID da loja (usado com list_type=5)
            list_type: 1 (categoria/keyword) ou 5 (loja específica)
            sort_type: 5 (mais vendidos) recomendado
            page: Número da página
            limit: Itens por página
        """
        # Query base
        query_parts = []
        variables = {
            "listType": list_type,
            "sortType": sort_type,
            "page": page,
            "limit": limit
        }
        
        if keyword:
            query_parts.append("keyword: $keyword")
            variables["keyword"] = keyword
        
        if category_id:
            query_parts.append("productCatId: $categoryId")
            variables["categoryId"] = category_id
        
        if shop_id:
            query_parts.append("shopId: $shopId")
            query_parts.append("matchId: $shopId")
            variables["shopId"] = shop_id
        
        query_params = ", ".join(query_parts) + ", listType: $listType, sortType: $sortType, page: $page, limit: $limit"
        
        query = f"""
        query ProductSearch($keyword: String, $categoryId: Int, $shopId: Int, $listType: Int!, $sortType: Int!, $page: Int!, $limit: Int!) {{
          productOfferV2({query_params}) {{
            nodes {{
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
              shopId
              shopName
              shopType
              productCatIds
            }}
            pageInfo {{
              page
              limit
              hasNextPage
            }}
          }}
        }}
        """
        
        return self.query(query, variables)
    
    # ==================== LINKS CURTOS ====================
    
    def generate_short_link(
        self,
        origin_url: str,
        sub_ids: Optional[List[str]] = None
    ) -> dict:
        """
        Gera link curto com rastreamento
        
        Args:
            origin_url: URL original do produto/loja Shopee
            sub_ids: Lista de até 5 subIds para rastreamento personalizado
        
        Returns:
            dict: {'data': {'generateShortLink': {'shortLink': 'https://...'}}}
        """
        if sub_ids is None:
            sub_ids = ["", "", "", "", ""]
        
        # Garantir exatamente 5 subIds
        while len(sub_ids) < 5:
            sub_ids.append("")
        sub_ids = sub_ids[:5]
        
        query = """
        mutation($url: String!, $subIds: [String!]!) {
          generateShortLink(input: {originUrl: $url, subIds: $subIds}) {
            shortLink
          }
        }
        """
        
        variables = {
            "url": origin_url,
            "subIds": sub_ids
        }
        
        return self.query(query, variables)
    
    # ==================== RELATÓRIOS ====================
    
    def conversion_report(
        self,
        start_timestamp: int,
        end_timestamp: int,
        page: int = 1,
        limit: int = 500,
        scroll_id: Optional[str] = None
    ) -> dict:
        """
        Busca relatório de conversão (últimos 3 meses disponíveis)
        
        Args:
            start_timestamp: Timestamp Unix início do período
            end_timestamp: Timestamp Unix fim do período
            page: Número da página
            limit: Itens por página (max 500)
            scroll_id: Para páginas seguintes (válido por 30s)
        
        Returns:
            dict: Relatório com nodes e pageInfo.scrollId
        """
        query = """
        query ConversionReport($start: Int!, $end: Int!, $page: Int!, $limit: Int!, $scrollId: String) {
          conversionReport(
            purchaseTimeStart: $start
            purchaseTimeEnd: $end
            page: $page
            limit: $limit
            scrollId: $scrollId
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
        """
        
        variables = {
            "start": start_timestamp,
            "end": end_timestamp,
            "page": page,
            "limit": limit
        }
        
        if scroll_id:
            variables["scrollId"] = scroll_id
        
        return self.query(query, variables)
    
    def validated_report(
        self,
        start_timestamp: int,
        end_timestamp: int,
        page: int = 1,
        limit: int = 500,
        scroll_id: Optional[str] = None
    ) -> dict:
        """
        Busca relatório validado (pedidos com comissão confirmada)
        
        Args similares ao conversion_report
        """
        query = """
        query ValidatedReport($start: Int!, $end: Int!, $page: Int!, $limit: Int!, $scrollId: String) {
          validatedReport(
            purchaseTimeStart: $start
            purchaseTimeEnd: $end
            page: $page
            limit: $limit
            scrollId: $scrollId
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
        """
        
        variables = {
            "start": start_timestamp,
            "end": end_timestamp,
            "page": page,
            "limit": limit
        }
        
        if scroll_id:
            variables["scrollId"] = scroll_id
        
        return self.query(query, variables)
    
    # ==================== HELPERS ====================
    
    def fetch_all_pages(
        self,
        query_func,
        max_pages: int = 10,
        **kwargs
    ) -> List[dict]:
        """
        Busca múltiplas páginas automaticamente (para queries com scrollId)
        
        Args:
            query_func: Função de query (conversion_report ou validated_report)
            max_pages: Máximo de páginas para buscar
            **kwargs: Argumentos para query_func
        
        Returns:
            List[dict]: Lista de todos os nodes coletados
        """
        all_nodes = []
        page = 1
        scroll_id = None
        
        while page <= max_pages:
            result = query_func(page=page, scroll_id=scroll_id, **kwargs)
            
            nodes = result['data'][list(result['data'].keys())[0]]['nodes']
            page_info = result['data'][list(result['data'].keys())[0]]['pageInfo']
            
            all_nodes.extend(nodes)
            
            if not page_info.get('hasNextPage'):
                break
            
            scroll_id = page_info.get('scrollId')
            page += 1
            
            # Aguardar para evitar rate limit
            time.sleep(1)
        
        return all_nodes


class ShopeeAPIError(Exception):
    """Exceção para erros da API Shopee"""
    
    ERROR_MESSAGES = {
        10000: "Erro do sistema",
        10010: "Erro de parsing (sintaxe incorreta ou API inexistente)",
        10020: "Erro de autenticação (assinatura incorreta ou expirada)",
        10030: "Rate limit excedido (2000 req/hora)",
        10032: "Invalid affiliate ID",
        10035: "Sem acesso à API (solicitar no suporte)",
        11000: "Erro de negócio",
        11001: "Erro de parâmetros"
    }
    
    def __init__(self, code: int, message: str, error_data: dict):
        self.code = code
        self.message = message
        self.error_data = error_data
        
        friendly_message = self.ERROR_MESSAGES.get(code, message)
        super().__init__(f"[{code}] {friendly_message}: {message}")


# ==================== EXEMPLO DE USO ====================

if __name__ == "__main__":
    # Configurar cliente
    client = ShopeeAffiliateClient(
        app_id="SEU_APP_ID",
        secret="SEU_SECRET"
    )
    
    # Exemplo 1: Buscar produtos por palavra-chave
    print("=== Buscando produtos 'smartphone' ===")
    try:
        result = client.search_products(keyword="smartphone", limit=5)
        products = result['data']['productOfferV2']['nodes']
        
        for product in products:
            print(f"- {product['productName']}")
            print(f"  Comissão: {product['commissionRate']}%")
            print(f"  Preço: R$ {product['priceMin']}")
            print()
    except ShopeeAPIError as e:
        print(f"Erro: {e}")
    
    # Exemplo 2: Gerar link curto
    print("=== Gerando link curto ===")
    try:
        origin_url = "https://shopee.com.br/product-i.123.456"
        result = client.generate_short_link(
            origin_url,
            sub_ids=["telegram", "bot", "teste", "", ""]
        )
        short_link = result['data']['generateShortLink']['shortLink']
        print(f"Link curto: {short_link}")
    except ShopeeAPIError as e:
        print(f"Erro: {e}")
    
    # Exemplo 3: Relatório de conversão (última semana)
    print("=== Relatório de conversão ===")
    try:
        end = int(time.time())
        start = end - 7 * 86400  # 7 dias atrás
        
        result = client.conversion_report(start, end, limit=10)
        orders = result['data']['conversionReport']['nodes']
        
        for order in orders:
            print(f"Pedido: {order['orderId']}")
            print(f"Comissão: R$ {order['commissionAmount']}")
            print(f"Status: {order['orderStatus']}")
            print()
    except ShopeeAPIError as e:
        print(f"Erro: {e}")
