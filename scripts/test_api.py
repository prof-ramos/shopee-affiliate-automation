import argparse
import hashlib
import json
import os
import time

import requests

BASE_URL = "https://open-api.affiliate.shopee.com.br/graphql"
DEFAULT_FIELDS = """
      itemId
      productName
      commissionRate
      priceMin
      priceMax
      offerLink
""".strip()


def build_query(keyword: str, page: int, limit: int, fields: str) -> str:
    sanitized_keyword = keyword.replace('"', "\\\"")
    return f"""
query {{
  productOfferV2(keyword: \"{sanitized_keyword}\", page: {page}, limit: {limit}) {{
    nodes {{
{fields}
    }}
  }}
}}
""".strip()


def build_signature(app_id: str, secret: str, timestamp: str, payload: str) -> str:
    sign_factor = f"{app_id}{timestamp}{payload}{secret}"
    return hashlib.sha256(sign_factor.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Teste rapido da Shopee Affiliate API")
    parser.add_argument("--keyword", default="smartphone", help="Keyword para busca")
    parser.add_argument("--page", type=int, default=1, help="Pagina da busca")
    parser.add_argument("--limit", type=int, default=5, help="Itens por pagina")
    parser.add_argument(
        "--no-proxy",
        action="store_true",
        help="Ignora variaveis de proxy do ambiente",
    )
    parser.add_argument(
        "--fields",
        default=DEFAULT_FIELDS,
        help="Campos GraphQL separados por nova linha (\"itemId\nproductName\")",
    )
    args = parser.parse_args()

    app_id = os.getenv("SHOPEE_APP_ID")
    secret = os.getenv("SHOPEE_SECRET")

    if not app_id or not secret:
        print("Defina SHOPEE_APP_ID e SHOPEE_SECRET no ambiente.")
        return 1

    query = build_query(args.keyword, args.page, args.limit, args.fields)
    payload = {"query": query}
    payload_str = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    timestamp = str(int(time.time()))
    signature = build_signature(app_id, secret, timestamp, payload_str)

    headers = {
        "Authorization": (
            f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}"
        ),
        "Content-Type": "application/json",
    }

    session = requests.Session()
    if args.no_proxy:
        session.trust_env = False

    try:
        response = session.post(
            BASE_URL,
            headers=headers,
            data=payload_str,
            timeout=30,
        )
    except requests.RequestException as exc:
        print(f"Falha na requisicao: {exc}")
        return 1

    print(f"Status: {response.status_code}")
    try:
        body = response.json()
        print(json.dumps(body, indent=2, ensure_ascii=False))
    except ValueError:
        print(response.text)

    if response.status_code >= 400:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
