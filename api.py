from __future__ import annotations

import os
from typing import Dict, Any, List

import requests


class AjaxAPI:
    def __init__(self, base_url: str, token: str | None = None, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token or os.getenv("AJAX_API_TOKEN", "")
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, email: str, password: str) -> str:
        """
        Obtain JWT access token using email/password against /api/token/.
        Returns the access token and stores it on the client for subsequent calls.
        """
        url = f"{self.base_url}/api/token/"
        payload = {"email": email, "password": password}
        resp = requests.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        access = data.get("access")
        if not access:
            raise ValueError("No 'access' token in response")
        self.token = access
        return access

    def fetch_facturas(self, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        # Always target the integraciones endpoint
        url = f"{self.base_url}/integraciones/api/facturas"
        params = {"fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta}
        resp = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        if isinstance(data, list):
            return data
        raise ValueError("Unexpected API response format for facturas")

    def download_dbf_zip(self, fecha_desde: str, fecha_hasta: str) -> bytes:
        url = f"{self.base_url}/integraciones/api/export_dbf"
        params = {"fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta}
        resp = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.content


