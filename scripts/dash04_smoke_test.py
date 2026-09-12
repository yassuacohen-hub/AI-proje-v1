import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.dash04_api_client import APIError, get_api
from scripts.dash04_db_reader import DBQueryError, read_only_query


def main() -> None:
    try:
        health = get_api("/api/health")
        print(f"API yanıtı: {health}")
    except APIError as exc:
        print(f"API kullanılamıyor; DB fallback devrede: {exc}")

    try:
        result = read_only_query("SELECT 1 AS sonuc")
        print(f"DB fallback sonucu: {result}")
    except DBQueryError as exc:
        print(f"DB fallback çalıştırılamadı: {exc}")


if __name__ == "__main__":
    main()