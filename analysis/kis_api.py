import os
import time
import requests


class KISClient:
    def __init__(self) -> None:
        self.app_key = os.getenv("KIS_APP_KEY", "")
        self.app_secret = os.getenv("KIS_APP_SECRET", "")
        self.base_url = os.getenv("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443")
        self.access_token = None
        self.token_expiry = 0

    def _ensure_token(self) -> str:
        now = int(time.time())
        if self.access_token and now < self.token_expiry:
            return self.access_token

        if not self.app_key or not self.app_secret:
            raise RuntimeError("KIS credentials are not configured")

        response = requests.post(
            f"{self.base_url}/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        self.token_expiry = now + int(data.get("expires_in", 0)) - 60
        return self.access_token

    def _headers(self) -> dict:
        token = self._ensure_token()
        return {
            "Authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100",
        }

    def get_quote(self, symbol: str) -> dict:
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
        }
        response = requests.get(
            f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price",
            headers=self._headers(),
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_candles(self, symbol: str, timeframe: str = "D", count: int = 200) -> list:
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
            "fid_period_div_code": timeframe,
            "fid_org_adj_prc": "0",
        }
        response = requests.get(
            f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            headers=self._headers(),
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("output2", [])[:count]

    def place_order(self, symbol: str, side: str, quantity: int, price: float) -> dict:
        payload = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
        }
        return {"status": "simulated", "payload": payload}
