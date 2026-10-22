# -*- coding: utf-8 -*-
"""Evren anahtarını config.toml'a PROGRAMLIK yazar — anahtar elle yazılmaz,
kaynak dosyadan okunur (üçüncü kez '…' bozulması tuzağı: elle kopyalama YASAK).
Anahtar DEĞERİ ekrana basılmaz (D-380)."""
import json
import re
import tomllib
import urllib.request
from pathlib import Path

KAYNAK = Path(r"C:\Users\yasin\zoo-9router-import.json")
CFG = Path.home() / ".codex" / "config.toml"


def anahtar_bul():
    d = json.loads(KAYNAK.read_text(encoding="utf-8"))
    for prof in d["providerProfiles"]["apiConfigs"].values():
        u = prof.get("openAiBaseUrl", "")
        if "evren" in u:
            return prof["openAiApiKey"]
    raise SystemExit("Evren anahtarı kaynakta yok")


def main():
    anahtar = anahtar_bul()
    print("anahtar uzunluğu:", len(anahtar), "· ascii mi:", anahtar.isascii())

    metin = CFG.read_text(encoding="utf-8")
    yeni, n = re.subn(
        r'(\[model_providers\.evren\.http_headers\]\s*\nAuthorization = ")Bearer [^"]*(")',
        r"\g<1>Bearer " + anahtar + r"\g<2>", metin, count=1)
    if n != 1:
        raise SystemExit("Authorization satırı bulunamadı — desen uyuşmadı")
    CFG.write_text(yeni, encoding="utf-8")
    print("config.toml güncellendi")

    with open(CFG, "rb") as f:
        d = tomllib.load(f)
    yazili = d["model_providers"]["evren"]["http_headers"]["Authorization"]
    print("config'teki uzunluk:", len(yazili), "· eşleşme:", yazili == "Bearer " + anahtar)

    # canlı doğrulama: /responses
    body = json.dumps({"model": "glm-5.3", "input": "Say OK", "stream": False}).encode()
    req = urllib.request.Request(
        "https://evren-llmapi.ssyz.org.tr/v1/responses", data=body,
        headers={"Authorization": yazili, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.loads(r.read().decode())
    print("canli /responses status:", j.get("status"))


if __name__ == "__main__":
    main()
