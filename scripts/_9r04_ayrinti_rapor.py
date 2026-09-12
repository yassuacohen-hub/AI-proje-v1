# -*- coding: utf-8 -*-
"""9R-04: 9Router DB'deki provider kayıtlarının ayrıntılı dökümü.

Amaç: Kullanıcıya "DB'de gerçekte ne görünüyor" sorusuna net kanıt sunmak.
- providerConnections tablosundaki TÜM provider adlarını listeler
- Web provider adı geçen satırların apiKey alanının gerçek/dolu olup olmadığını gösterir
- _meta / settings tablolarından DATA_DIR, baseUrl, cloud-sync gibi bilgileri döker
"""
from __future__ import annotations

import json
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = r"C:\Users\yasin\AppData\Roaming\9router\db\data.sqlite"
WEB_PROVIDERLER = ("firecrawl", "tavily", "jina-reader", "jina", "exa", "brave", "serper")


def _satir_ozet(row: tuple) -> dict:
    """Satırı sözlüğe çevirir; apiKey'i maskeleyerek gösterir."""
    d = {}
    for i, v in enumerate(row):
        anahtar = f"kolon{i}"
        if isinstance(v, str) and len(v) > 120:
            anahtar += "(ozet)"
            v = v[:120] + "..."
        d[anahtar] = v
    return d


def _api_key_mask(data: str | None) -> str:
    if not data:
        return "(yok)"
    try:
        obj = json.loads(data)
        if isinstance(obj, dict):
            ak = obj.get("apiKey") or obj.get("api_key") or ""
            if not ak:
                return "(data JSON var ama apiKey yok)"
            if len(ak) <= 6:
                return f"(apiKey cok kisa: {ak!r})"
            return f"apiKey OK: {ak[:4]}...{ak[-4:]} (uzunluk={len(ak)})"
        return f"(data JSON degil, tip={type(obj).__name__})"
    except Exception as exc:  # noqa: BLE001
        return f"(JSON parse hatasi: {exc})"


def main() -> int:
    con = sqlite3.connect(DB)
    cur = con.cursor()

    print("=== 1) providerConnections: TUM KAYITLAR ===")
    cur.execute("PRAGMA table_info(providerConnections)")
    kolonlar = [r[1] for r in cur.fetchall()]
    print("Kolonlar:", kolonlar)
    rows = cur.execute("SELECT * FROM providerConnections").fetchall()
    print(f"Toplam kayıt: {len(rows)}")
    # provider adı hangi kolonda olabilir? bilgi için ilk satırı yazdır
    for r in rows:
        print("  -", _satir_ozet(r) if False else [str(x)[:60] for x in r])
    print()

    print("=== 2) Web provider kontrolu (firecrawl/tavily/jina/exa/brave/serper) ===")
    kurallar = " OR ".join(
        f"(provider LIKE '%{a}%' OR data LIKE '%{a}%' OR id LIKE '%{a}%')" for a in WEB_PROVIDERLER
    )
    try:
        web_rows = cur.execute(f"SELECT * FROM providerConnections WHERE {kurallar}").fetchall()
    except sqlite3.Error as exc:
        print(f"Sorgu hatası: {exc} — providerColumnsDeneme")
        web_rows = []
    if not web_rows:
        print("SONUÇ: providerConnections tablosunda HİÇBİR web provider kaydı YOK.")
        print("=> 5 'data' eşleşmesi yanlış pozitif (chat provider JWT token'larında geçen alt dizeler).")
    for r in web_rows:
        idx = {k: i for i, k in enumerate(kolonlar)}
        veri = r[idx["data"]] if "data" in idx else ""
        pid = r[idx["id"]] if "id" in idx else r[idx["provider"]] if "provider" in idx else "?"
        print(f"  - id={pid} apiKey={_api_key_mask(veri)}")
    print()

    print("=== 3) providerConnections icindeki provider adlari (benzersiz) ===")
    try:
        adlar = cur.execute("SELECT DISTINCT provider FROM providerConnections ORDER BY provider").fetchall()
        for (a,) in adlar:
            print(f"  - {a}")
    except sqlite3.Error as exc:
        print(f"(provider kolonu sorgulanamadi: {exc})")
    print()

    print("=== 4) _meta tablosu ===")
    try:
        cur.execute("PRAGMA table_info(_meta)")
        mk = [r[1] for r in cur.fetchall()]
        print("Kolonlar:", mk)
        for r in cur.execute("SELECT * FROM _meta").fetchall():
            print("  -", r)
    except sqlite3.Error as exc:
        print(f"(hata: {exc})")
    print()

    print("=== 5) settings tablosu ===")
    try:
        cur.execute("PRAGMA table_info(settings)")
        sk = [r[1] for r in cur.fetchall()]
        print("Kolonlar:", sk)
        for r in cur.execute("SELECT * FROM settings").fetchall():
            print("  -", [str(x)[:160] for x in r])
    except sqlite3.Error as exc:
        print(f"(hata: {exc})")
    print()

    print("=== 6) apiKeys tablosu ===")
    try:
        cur.execute("PRAGMA table_info(apiKeys)")
        akk = [r[1] for r in cur.fetchall()]
        print("Kolonlar:", akk)
        for r in cur.execute("SELECT * FROM apiKeys").fetchall():
            print("  -", [str(x)[:80] for x in r])
    except sqlite3.Error as exc:
        print(f"(hata: {exc})")

    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())