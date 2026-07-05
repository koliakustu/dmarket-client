import json
from datetime import datetime
from types import NoneType
from urllib.parse import quote, urlencode

import requests
from nacl.bindings import crypto_sign

from dmarket.models import BalanceResponse, MarketplaceOffersResponse, UserProfileResponse

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

    def call(self, method: str, path: str, payload: dict | NoneType = None) -> dict:
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
        request_body = ""

        if payload:
            if method == "GET":
                api_url_path = f"{path}?{urlencode(payload, quote_via=quote)}"
            else:
                request_body = json.dumps(payload)

        string_to_sign = method + api_url_path + request_body + nonce
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
        price_from: int | None = None,
        price_to: int | None = None,
        limit: int = 10,
        cursor: str | None = None
    ) -> MarketplaceOffersResponse:

        path = "/marketplace-api/v2/offers"

        payload = {
                "gameId": gameid,
                "limit": limit,
        }

        if title:
            payload["title"] = title

        if price_from is not None:
            payload["priceFrom"] = price_from

        if price_to is not None:
            payload["priceTo"] = price_to

        if cursor:
            payload["cursor"] = cursor

        response = self.call("GET", path, payload=payload)

        return MarketplaceOffersResponse(**response)
