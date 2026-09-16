from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

DEFAULT_API_URL = "http://localhost:8000"
CONFIG_PATH = Path(__file__).resolve().parents[1] / ".streamlit" / "config.toml"


class APIError(Exception):
    pass


def _api_url() -> str:
    configured_url = os.getenv("DASH_API_URL", "").strip()
    if configured_url:
        return configured_url.rstrip("/")

    try:
        with CONFIG_PATH.open("rb") as config_file:
            config = tomllib.load(config_file)
        api_config = config.get("api", {})
        url = api_config.get("url") if isinstance(api_config, dict) else None
        if isinstance(url, str) and url.strip():
            return url.strip().rstrip("/")
    except (OSError, tomllib.TOMLDecodeError, TypeError, AttributeError):
        pass

    return DEFAULT_API_URL


def get_api(
    endpoint: str,
    token: str | None = None,
    params: dict[str, Any] | None = None,
    timeout: float = 10,
) -> Any:
    if not isinstance(endpoint, str) or not endpoint.startswith("/"):
        raise APIError("API endpoint '/' karakteri ile başlamalıdır.")

    url = f"{_api_url()}/{endpoint.lstrip('/')}"
    effective_token = token if token is not None else os.getenv("DASH_API_TOKEN", "").strip()
    headers = {"Authorization": f"Bearer {effective_token}"} if effective_token else {}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
    except requests.Timeout as exc:
        raise APIError(f"API zaman aşımına uğradı: {url}") from exc
    except requests.ConnectionError as exc:
        raise APIError(f"API sunucusuna bağlanılamadı: {url}") from exc
    except requests.RequestException as exc:
        raise APIError(f"API isteği başarısız oldu: {exc}") from exc

    if response.status_code >= 400:
        detail = ""
        try:
            payload = response.json()
            if isinstance(payload, dict):
                detail = str(payload.get("detail") or payload.get("message") or "")
            elif payload:
                detail = str(payload)
        except (ValueError, TypeError):
            detail = (response.text or "")[:200]
        message = f"API HTTP {response.status_code} hatası"
        if detail:
            message = f"{message}: {detail}"
        raise APIError(message)

    try:
        return response.json()
    except (ValueError, TypeError) as exc:
        raise APIError("API yanıtı geçerli JSON değil.") from exc
def post_api(endpoint, json=None, token=None, timeout=10):
    """web_app API'sine POST request gonderir."""
    if not isinstance(endpoint, str) or not endpoint.startswith("/"):
        raise APIError("API endpoint '/' karakteri ile baslamalidir.")
    url = f"{_api_url()}/{endpoint.lstrip('/')}"
    effective_token = token if token is not None else os.getenv("DASH_API_TOKEN", "").strip()
    headers = {"Authorization": f"Bearer {effective_token}"} if effective_token else {}
    try:
        response = requests.post(url, json=json, headers=headers, timeout=timeout)
    except requests.Timeout as exc:
        raise APIError(f"API zaman asimina ugradi: {url}") from exc
    except requests.ConnectionError as exc:
        raise APIError(f"API sunucusuna baglanilamadi: {url}") from exc
    except requests.RequestException as exc:
        raise APIError(f"API istegi basarisiz oldu: {exc}") from exc
    if response.status_code >= 400:
        detail = ""
        try:
            payload = response.json()
            if isinstance(payload, dict):
                detail = str(payload.get("detail") or payload.get("message") or "")
            elif payload:
                detail = str(payload)
        except (ValueError, TypeError):
            detail = (response.text or "")[:200]
        message = f"API HTTP {response.status_code} hatasi"
        if detail:
            message = f"{message}: {detail}"
        raise APIError(message)
    try:
        return response.json()
    except (ValueError, TypeError) as exc:
        raise APIError("API yanimi gecerli JSON degil.") from exc
