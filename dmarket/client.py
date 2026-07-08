import json
from datetime import datetime
from urllib.parse import quote, urlencode

import requests
from nacl.bindings import crypto_sign

from dmarket.models import *

class DMarketAPIError(Exception):
    pass

class DMarketClient:
    def __init__(self, public_key: str, secret_key: str):
        if not public_key or not secret_key:
            raise ValueError("Public and secret keys must be provided.")
        self._public_key = public_key
        self._secret_key = secret_key
        self._root_api_url = "https://api.dmarket.com"
        self._signature_prefix = "dmar ed25519 "

    def call(self, method: str, path: str, payload: dict | None = None, sign_path: str | None = None) -> dict:
        """
        Makes a signed API call to DMarket.

        :param method: HTTP method (e.g., 'GET', 'POST').
        :param path: API endpoint path (e.g., '/trade-aggregator/v1/last-sales').
        :param payload: Dictionary of parameters for the request.
        :return: A tuple of (response_json, error_string).
        """
        method = method.upper()
        nonce = str(round(datetime.now().timestamp()))
        api_url_path = path
        actual_sign_path = sign_path if sign_path else path
        request_body = ""

        if payload:
            if method == "GET":
                query_string = urlencode(payload, quote_via=quote)
                api_url_path = f"{path}?{query_string}"
                actual_sign_path = f"{actual_sign_path}?{query_string}"
            else:
                request_body = json.dumps(payload)

        string_to_sign = method + actual_sign_path + request_body + nonce
        signature = self._generate_signature(string_to_sign)

        headers = {
            "X-Api-Key": self._public_key,
            "X-Request-Sign": self._signature_prefix + signature,
            "X-Sign-Date": nonce,
        }
        if method not in ["GET"] and payload:
            headers["Content-Type"] = "application/json"

        full_url = self._root_api_url + api_url_path

        try:
            response = requests.request(
                method,
                full_url,
                headers=headers,
                data=request_body.encode('utf-8') if request_body else None
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_details = e.response.text if e.response else "No response body"
            raise DMarketAPIError(f"API call failed: {e}. Details: {error_details}")

    def _generate_signature(self, string_to_sign: str) -> str: 
        encoded = string_to_sign.encode('utf-8')
        secret_bytes = bytes.fromhex(self._secret_key)
        signature_bytes = crypto_sign(encoded, secret_bytes)
        return signature_bytes[:64].hex()

    def get_account_balance(self) -> BalanceResponse:
        response = self.call("GET", "/account/v1/balance")
        return BalanceResponse(**response)

    def get_user_profile(self) -> UserProfileResponse:
        response = self.call("GET", "/account/v1/user")
        return UserProfileResponse(**response)

    def get_market_offers(
        self,
        gameid: str = "a8db",
        title: str | None = None,
        category_path: str | None = None,
        price_from: int | None = None,
        price_to: int | None = None,
        order_by: str = "price",
        order_dir: str = "asc",
        limit: int = 100,
        cursor: str | None = None,
    ) -> MarketplaceOffersResponse:

        path = "/marketplace-api/v2/offers"

        payload = {
                "gameId": gameid,
                "limit": limit,
                "orderBy": order_by,
                "orderDir": order_dir,
        }

        if title:
            payload["title"] = title

        if price_from is not None:
            payload["priceFrom"] = price_from

        if price_to is not None:
            payload["priceTo"] = price_to

        if cursor:
            payload["cursor"] = cursor

        if category_path:
            payload["treeFilters"] = f"categoryPath={category_path}"

        response = self.call("GET", path, payload=payload)

        return MarketplaceOffersResponse(**response)

    def get_targets_by_title(self, title: str, game_id: str = "a8db") -> TargetsByTitleResponse:
        encoded_title = quote(title, safe="!'()*")
        response = self.call(
            method = "GET",
            path = f"/marketplace-api/v1/targets-by-title/{game_id}/{encoded_title}",
            sign_path = f"/marketplace-api/v1/targets-by-title/{game_id}/{title}",

        )
        return TargetsByTitleResponse(**response)

    def get_item_sales_history(
        self,
        title: str,
        game_id: str = "a8db",
        operation_type: str | None = None,
        limit: int = 100,
        offset: int = 0 
    ) -> ItemSalesHistoryResponse:

        payload = {
                "gameId": game_id,
                "title":  title,
                "limit": limit,
        }

        if operation_type:
            payload["txOperationType"] = operation_type

        if offset:
            payload["offset"] = offset

        response = self.call("GET", "/trade-aggregator/v1/last-sales", payload=payload)

        return ItemSalesHistoryResponse(**response)
