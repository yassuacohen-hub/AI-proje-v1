# -*- coding: utf-8 -*-
"""Ajan Chat Sistemi — D-192 Library.

Append-only JSONL log + lock-safe operations.
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

# ponytail: thread-local lock; upgrade to multiprocess Lock if needed
_LOCK = threading.RLock()


def _data_dir() -> Path:
    """Chat veri dizini."""
    d = Path(__file__).parent.parent.parent / "data" / "orchestrator"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _log_path(name: str = "ajan-chat") -> Path:
    """JSONL dosya yolu."""
    return _data_dir() / f"{name}.jsonl"


def _ensure_log(name: str = "ajan-chat") -> None:
    """Log dosyası varsa oku, yoksa boş oluştur."""
    p = _log_path(name)
    if not p.exists():
        p.touch()


def _ajan_normalize(ad: str | None) -> str:
    """Ajan adını kanonik forma çevir."""
    if not ad:
        return "unknown"
    ad = ad.lower().strip()
    if ad in ("ihsan", "utku", "salih", "yasu"):
        return ad
    # Fallback
    return ad


ONEM_SEVIYELERI: tuple[str, ...] = ("kritik", "yuksek", "orta", "dusuk")


def ac(
    ajan: str,
    task_id: str,
    sorun: str,
    cozum: str = "",
    kimden: str = "orkestrator",
    onem: str = "orta",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Sorun aç (problem kayıt).
    
    Args:
        ajan: kime (hedef ajan adı)
        task_id: görev ID
        sorun: 1-200 char alıntı
        cozum: 0-300 char çözüm önerisi (isteğe bağlı)
        kimden: gönderen ajan adı (varsayılan: orkestrator)
        onem: önem derecesi — kritik/yuksek/orta/dusuk (varsayılan: orta)
        data_dir: test için custom data dir
    
    Returns:
        Eklenen satır (dict)
    """
    _ensure_log()
    
    satir = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "kimden": _ajan_normalize(kimden),
        "ajan": _ajan_normalize(ajan),
        "task_id": task_id.upper(),
        "sorun": sorun[:200],
        "cozum": cozum[:300] if cozum else "",
        "durum": "acik",
        "onem": onem if onem in ONEM_SEVIYELERI else "orta",
        "link": "",
    }
    
    satir_json = json.dumps(satir, ensure_ascii=False) + "\n"
    
    # Atomic append
    with _LOCK:
        p = _log_path() if data_dir is None else data_dir / "ajan-chat.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(satir_json)
    
    return satir


def guncelle(
    task_id: str,
    sorun_index: int,
    cozum_guncel: str = "",
    durum: str = "cokundurmus",
    data_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Sorunun çözümünü güncelle.
    
    Args:
        task_id: görev ID
        sorun_index: satır index (0-based)
        cozum_guncel: yeni çözüm metni
        durum: yeni durum (cokundurmus|cozuldu)
        data_dir: test için custom data dir
    
    Returns:
        Güncellenen satır, bulunamaz ise None
    """
    _ensure_log()
    
    with _LOCK:
        p = _log_path() if data_dir is None else data_dir / "ajan-chat.jsonl"
        
        # Oku
        satirlar = []
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                satirlar = [json.loads(line) for line in f if line.strip()]
        
        # Bul ve güncelle
        idx = 0
        guncellenmi_satir = None
        for i, s in enumerate(satirlar):
            if s.get("task_id") == task_id.upper():
                if idx == sorun_index:
                    s["cozum"] = cozum_guncel[:300]
                    s["durum"] = durum
                    s["timestamp"] = datetime.now().isoformat(timespec="seconds")
                    guncellenmi_satir = s
                    break
                idx += 1
        
        if guncellenmi_satir is None:
            return None
        
        # Yaz
        with p.open("w", encoding="utf-8") as f:
            for s in satirlar:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        
        return guncellenmi_satir


def kapat(
    task_id: str,
    sorun_index: int,
    karar: str = "",
    data_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Sorunukapalı işaretle (durum=cozuldu).
    
    Args:
        task_id: görev ID
        sorun_index: satır index
        karar: karar notu
        data_dir: test için custom data dir
    
    Returns:
        Kapalı satır, bulunamaz ise None
    """
    return guncelle(task_id, sorun_index, karar, "cozuldu", data_dir)


def oku(
    task_id: str | None = None,
    son: int | None = None,
    data_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Chat mesajlarını oku.
    
    Args:
        task_id: belirli görevle filtrele
        son: son N satırı al
        data_dir: test için custom data dir
    
    Returns:
        Satırlar listesi
    """
    _ensure_log()
    
    p = _log_path() if data_dir is None else data_dir / "ajan-chat.jsonl"
    satirlar = []
    
    if p.exists():
        with p.open("r", encoding="utf-8") as f:
            satirlar = [json.loads(line) for line in f if line.strip()]
    
    # Filtre
    if task_id:
        satirlar = [s for s in satirlar if s.get("task_id") == task_id.upper()]
    
    if son:
        satirlar = satirlar[-son:]
    
    return satirlar


def ozet(
    durum: str | None = None,
    data_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Durum başına sayı ve sorunlar.
    
    Args:
        durum: filtrele (acik|cokundurmus|cozuldu)
        data_dir: test için custom data dir
    
    Returns:
        Filtrelenmiş satırlar
    """
    satirlar = oku(data_dir=data_dir)
    
    if durum:
        satirlar = [s for s in satirlar if s.get("durum") == durum]
    
    return satirlar


def bulgula(
    konu: str,
    bulgu: str,
    link: str = "",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Tasarım eleştirisi/görüşü kaydı.
    
    Args:
        konu: başlık (örn. "Tasarım Belgesi (D-192)")
        bulgu: eleştiri/görüş metni
        link: ilgili dosya/karar linki
        data_dir: test için custom data dir
    
    Returns:
        Eklenen satır
    """
    satir = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "konu": konu,
        "bulgu": bulgu[:500],
        "link": link,
    }
    
    satir_json = json.dumps(satir, ensure_ascii=False) + "\n"
    
    with _LOCK:
        p = _log_path("ajan-chat-bulgular") if data_dir is None else data_dir / "ajan-chat-bulgular.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(satir_json)
    
    return satir


def bulgular_oku(
    konu: str | None = None,
    son: int | None = None,
    data_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Bulgular logunu oku.
    
    Args:
        konu: belirli konuya filtrele
        son: son N bulgular
        data_dir: test için custom data dir
    
    Returns:
        Bulgular listesi
    """
    p = _log_path("ajan-chat-bulgular") if data_dir is None else data_dir / "ajan-chat-bulgular.jsonl"
    satirlar = []
    
    if p.exists():
        with p.open("r", encoding="utf-8") as f:
            satirlar = [json.loads(line) for line in f if line.strip()]
    
    if konu:
        satirlar = [s for s in satirlar if konu in s.get("konu", "")]
    
    if son:
        satirlar = satirlar[-son:]
    
    return satirlar


def kahin_gonder(
    mesaj: str,
    task_id: str = "",
    onem: str = "orta",
    kimden: str = "kahin",
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """KAHİN (Ürün Sahibi) mesaj gönder (D-210, D-212 Telegram).
    
    Broadcast mesajı chat logu + Telegram'a gönderir.
    
    Args:
        mesaj: 1-500 char sorun/istek
        task_id: ilgili görev (isteğe bağlı, boşsa genel)
        onem: önem seviyesi — kritik/yuksek/orta/dusuk
        kimden: sabit "kahin" (override edilmez)
        data_dir: test için custom data dir
    
    Returns:
        Eklenen satır (dict)
    """
    # Chat logu
    kayit = ac(
        ajan="*",  # Broadcast: tüm ajanlar bu mesajı görür
        task_id=task_id or "genel",
        sorun=mesaj[:500],
        cozum="",
        kimden="kahin",
        onem=onem if onem in ONEM_SEVIYELERI else "orta",
        data_dir=data_dir,
    )
    
    # D-212: Telegram'a gönder (hata sessiz)
    try:
        _gonder_telegram_kahin(mesaj, task_id, onem)
    except Exception:
        pass  # Telegram hatası chat'i etkilemesin
    
    return kayit


def _gonder_telegram_kahin(mesaj: str, task_id: str, onem: str) -> None:
    """D-212: KAHİN mesajını Telegram grubuna gönder. (Internal)"""
    import os
    import requests
    
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    
    if not token or not chat_id:
        return  # Yapılandırma yoksa sessiz dön
    
    onem_etiket = {
        "kritik": "🔴",
        "yuksek": "🟠",
        "orta": "🟡",
        "dusuk": "🟢",
    }.get(onem, "🟡")
    
    telegram_msg = (
        f"{onem_etiket} **KAHİN Mesajı**\n\n"
        f"__{mesaj[:400]}__\n\n"
        f"Görev: `{task_id or 'genel'}`"
    )
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": telegram_msg, "parse_mode": "Markdown"},
            timeout=5,
        )
    except Exception:
        pass  # Ağ hatası sessiz


def ajan_acik_sorulari(
    ajan: str,
    data_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Ajana yöneltilmiş açık sorunlar (D-210 basla kapısı).
    
    Args:
        ajan: kanonik ajan adı
        data_dir: test için custom data dir
    
    Returns:
        Açık (durum=acik) ve ajana ait sorunlar
    """
    satirlar = oku(data_dir=data_dir)
    ajan_norm = _ajan_normalize(ajan)
    
    # Filtrele: hedef=ajan ve durum=acik
    acik = [s for s in satirlar
            if s.get("ajan") == ajan_norm and s.get("durum") == "acik"]
    
    return acik


def teslim_kontrol_et(
    task_id: str,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Görevle ilgili açık sorular var mı kontrol et (D-210 teslim kapısı).
    
    Args:
        task_id: görev ID
        data_dir: test için custom data dir
    
    Returns:
        {"engel": bool, "nedenler": [liste açık sorunların]}
    """
    satirlar = oku(task_id=task_id, data_dir=data_dir)
    
    # Açık sorunları filtrele
    acik_sorunlar = [s for s in satirlar if s.get("durum") == "acik"]
    
    engel = len(acik_sorunlar) > 0
    nedenler = [
        f"{s.get('sorun', '?')} (kimden: {s.get('kimden', '?')})"
        for s in acik_sorunlar
    ]
    
    return {
        "engel": engel,
        "nedenler": nedenler,
    }
