# -*- coding: utf-8 -*-
"""AI-CHAT-01 — MIMIR sohbet motoru (Odin ⚡ katmanı).

S11 kararı: görünen ad **MIMIR** (Odin'in bilgelik kuyusu); ``abrakadabra``
ise sohbet içindeki **kilit sözü** — ayrıcalıklı işlemler (teklif uygulama)
yalnızca kilit sözü verilince açılır ve modele asla sızdırılmaz.

Karar: [[D-182]] — Orkestratör Asistanı İki Seviye (2026-09-21)
Test: [[tests/test_d182_mimir.py]]

Streamlit'ten bağımsız saf iş mantığı:

* **9Router üzerinden sohbet** (BK4): UCRUZ/hızlı model varsayılanı
  ``gpt-4o-mini``; sağlayıcı düşerse **fallback zinciri** (K6) sırayla denenir.
* **Pano/posta okuma araçları**: görev panosu ve tetik posta kutusu özetleri
  modele bağlam olarak verilir (salt okunur).
* **TEKLİF → ONAY akışı**: model doğrudan pano yazmaz. Yanıt içindeki
  ``TEKLIF: <komut> <argümanlar>`` satırları ayıklanır; UI'da onay butonu
  ile ``teklif_uygula`` çağrılır. Bilinmeyen komutlar reddedilir.
* **Admin token zorunlu**: ``sohbet()`` token boşsa çağrı yapmaz.

Kurulum (.env)::

    NINEROUTER_URL=http://localhost:20128
    NINEROUTER_KEY=sk-...
    MIMIR_MODELS=gpt-4o-mini,gemini-2.0-flash,claude-3-5-haiku,yasu-9router
    MIMIR_KILIT_SOZU=abrakadabra   # varsayılan; üretimde değiştirilebilir

Model adları **yalnızca env ile** izlenir/değiştirilir (``MIMIR_MODELS``;
eski ``ABRAKADABRA_MODELS`` geri uyumlu okunur). NOT: ilk canlı 9Router
testi sonrası zincir sırası/temperature/max_tokens optimizasyonu gerekebilir.
"""
from __future__ import annotations

import os
import re
import shlex
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

import requests

from company_master.gateway.ninerouter_client import NineRouter, NineRouterError
from company_master.odin_ai import arac_dongusu as ad
from company_master.orchestrator import task_board as tb
from company_master.orchestrator import trigger as tr

__all__ = [
    "AiChatHatasi",
    "Mesaj",
    "Teklif",
    "VARSAYILAN_MODELLER",
    "GORUNEN_AD",
    "GORUNEN_AD_SEVIYE1",
    "gorunen_ad",
    "kilit_sozu",
    "kilit_acik",
    "kilit_maskele",
    "model_zinciri",
    "pano_ozeti",
    "posta_ozeti",
    "baglam_metni",
    "teklif_ayikla",
    "teklif_uygula",
    "sohbet",
]

#: S11 — kullanıcıya görünen asistan adı (Seviye 0, öntanımlı).
GORUNEN_AD = "MIMIR"

#: D-182 — anahtar dönüşümü sonrası Seviye 1 adı. MIMIR bilgelik kuyusu,
#: yetki devrinden sonra ODIN olur (aynı varlık, yükselmiş yetki).
GORUNEN_AD_SEVIYE1 = "ODIN"


def gorunen_ad(seviye: int = 0) -> str:
    """Seviyeye göre görünen ad: 0 → MIMIR (asistan), 1 → ODIN (orkestratör)."""
    return GORUNEN_AD_SEVIYE1 if seviye == 1 else GORUNEN_AD

#: Kilit sözü env anahtarı ve varsayılanı (sahip ritüeliyle aynı sözcük).
KILIT_ENV = "MIMIR_KILIT_SOZU"
VARSAYILAN_KILIT = "abrakadabra"

#: Model zinciri env anahtarları (yeni → eski, geri uyumlu).
MODEL_ENV_ANAHTARLARI: tuple[str, ...] = ("MIMIR_MODELS", "ABRAKADABRA_MODELS")

#: K6 — sağlayıcı düşerse sırayla denenecek modeller (9Router combo adları).
#: F0-b ölçümü (2026-10-03): eski zincir 3/3 ölüydü
#: (meta-llama/mixtral → 404 "No active credentials", gpt-3.5-turbo → 429 "no credits").
#:  1. mimir-dis — claude-haiku-4-5 üstünde 9Router combo; ~2.850 token gömülü prompt (BORÇ)
#:  2. claude_sadece — yedek combo
#:  3. fullclaude — son yedek combo
#: ponytail: fiyat optimizasyonu yapılmadı; ürün sahibi "yedek araç şart, combo yaparız" dedi.
#: Add when: 9Router usage'dan fiyat okunabilince zincir maliyete göre yeniden sıralanır.
VARSAYILAN_MODELLER: tuple[str, ...] = (
    "mimir-dis",
    "claude_sadece",
    "fullclaude",
)

#: Onay kapısından geçebilen komutlar. Anahtar → (argüman sayısı, açıklama).
IZINLI_KOMUTLAR: dict[str, tuple[int, str]] = {
    "gorev_guncelle": (2, "gorev_guncelle <task_id> <durum>"),
    "tetik_ekle": (2, "tetik_ekle <task_id> <ajan> [talimat]"),
}

#: Pano özetinde gösterilen en fazla görev sayısı (token tasarrufu).
PANO_LIMIT = 12

SISTEM_PROMPT = (
    f"Sen {GORUNEN_AD}'sin: Huginn Data Insights projesinin Muninn (iç ekip) "
    "panelindeki orkestratör asistanısın. Türkçe, kısa ve somut yanıt ver. "
    "Görev panosunu ve posta kutusunu yalnızca sana verilen bağlamdan oku; "
    "uydurma. Panoda değişiklik gerekiyorsa DOĞRUDAN YAPMA — ayrı satırda "
    "'TEKLIF: <komut> <argümanlar>' biçiminde öner. İzinli komutlar: "
    + "; ".join(v[1] for v in IZINLI_KOMUTLAR.values())
    + ". Kullanıcı onaylamadan hiçbir komut uygulanmaz."
)

_TEKLIF_RX = re.compile(r"^\s*TEKL[İI]F\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


class AiChatHatasi(Exception):
    """Sohbet motoru hatası (yetki, tüm sağlayıcılar düştü, geçersiz teklif)."""


@dataclass(frozen=True)
class Mesaj:
    """Tek sohbet mesajı. ``rol`` → ``user`` | ``assistant``."""

    rol: str
    icerik: str

    def __post_init__(self) -> None:
        if self.rol not in ("user", "assistant"):
            raise ValueError(f"bilinmeyen rol: {self.rol!r}")


@dataclass(frozen=True)
class Teklif:
    """Modelin önerdiği, onay bekleyen pano komutu."""

    komut: str
    argumanlar: tuple[str, ...] = field(default_factory=tuple)

    @property
    def metin(self) -> str:
        return " ".join((self.komut, *self.argumanlar))


class SohbetIstemcisi(Protocol):
    """Test edilebilirlik için 9Router istemcisinin gereken alt kümesi."""

    def chat(self, prompt: str, model: str | None = None, system: str | None = None,
             temperature: float | None = None, max_tokens: int | None = 1024) -> str: ...


# ---------------------------------------------------------------------------
# Model zinciri
# ---------------------------------------------------------------------------


def model_zinciri(env_deger: str | None = None) -> tuple[str, ...]:
    """``MIMIR_MODELS`` (virgüllü; eski ``ABRAKADABRA_MODELS`` geri uyumlu) veya varsayılan zincir."""
    if env_deger is None:
        env_deger = next((v for k in MODEL_ENV_ANAHTARLARI if (v := os.getenv(k, "").strip())), "")
    modeller = tuple(m.strip() for m in env_deger.split(",") if m.strip())
    return modeller or VARSAYILAN_MODELLER


# ---------------------------------------------------------------------------
# Kilit sözü (sihirli anahtar kelime)
# ---------------------------------------------------------------------------


def kilit_sozu() -> str:
    """Env'den kilit sözünü okur; boşsa varsayılan ``abrakadabra``."""
    return (os.getenv(KILIT_ENV, "") or VARSAYILAN_KILIT).strip().lower()


def _kilit_rx() -> re.Pattern[str]:
    return re.compile(rf"(?<!\w){re.escape(kilit_sozu())}(?!\w)", re.IGNORECASE)


def kilit_acik(metin: str | None) -> bool:
    """Metin kilit sözünü **tam sözcük** olarak içeriyorsa True."""
    return bool(metin) and _kilit_rx().search(metin) is not None


def kilit_maskele(metin: str) -> str:
    """Kilit sözünü modele sızdırmamak için maskeler (``[KİLİT]``)."""
    return _kilit_rx().sub("[KİLİT]", metin or "")


# ---------------------------------------------------------------------------
# Salt okunur pano / posta araçları
# ---------------------------------------------------------------------------


def pano_ozeti(limit: int = PANO_LIMIT, durumlar: tuple[str, ...] = ("aktif", "review", "blocked", "bekliyor", "plan")) -> list[dict[str, Any]]:
    """Panodaki açık görevlerin kısa özeti (id, durum, sahip, öncelik, başlık)."""
    board = tb.gorev_listesi()
    acik = [g for g in board if g.get("durum") in durumlar]
    return [
        {
            "task_id": g.get("task_id"),
            "durum": g.get("durum"),
            "sahip": g.get("sahip"),
            "oncelik": g.get("oncelik"),
            "baslik": str(g.get("baslik", ""))[:80],
        }
        for g in acik[-limit:]
    ]


def posta_ozeti(ajan: str) -> list[dict[str, Any]]:
    """Ajanın bekleyen tetikleri (task_id, tarih, talimat kısaltılmış)."""
    return [
        {"task_id": k.get("task_id"), "tarih": k.get("tarih"),
         "talimat": str(k.get("talimat", ""))[:120]}
        for k in tr.bekleyen_tetikler(ajan)
    ]


def baglam_metni(ajan: str = "roo", limit: int = PANO_LIMIT) -> str:
    """Modele verilecek düz metin bağlam (pano + posta)."""
    satirlar = ["[GÖREV PANOSU]"]
    pano = pano_ozeti(limit)
    satirlar += [f"- {g['task_id']} | {g['durum']} | {g['sahip']} | {g['oncelik']} | {g['baslik']}"
                 for g in pano] or ["- (açık görev yok)"]
    satirlar.append(f"[POSTA KUTUSU: {ajan}]")
    posta = posta_ozeti(ajan)
    satirlar += [f"- {p['task_id']} | {p['tarih']} | {p['talimat']}" for p in posta] or ["- (bekleyen tetik yok)"]
    return "\n".join(satirlar)


# ---------------------------------------------------------------------------
# TEKLİF → ONAY
# ---------------------------------------------------------------------------


def teklif_ayikla(metin: str) -> list[Teklif]:
    """Yanıttaki ``TEKLIF:`` satırlarını güvenli biçimde ayıklar.

    Bilinmeyen komut veya eksik argüman içeren satırlar **sessizce atlanır**;
    böylece model uydurduğu komutlarla onay kapısına ulaşamaz.
    """
    teklifler: list[Teklif] = []
    for ham in _TEKLIF_RX.findall(metin or ""):
        try:
            parcalar = shlex.split(ham)
        except ValueError:
            continue
        if not parcalar:
            continue
        komut, *args = parcalar
        komut = komut.lower()
        kural = IZINLI_KOMUTLAR.get(komut)
        if kural is None or len(args) < kural[0]:
            continue
        teklifler.append(Teklif(komut, tuple(args)))
    return teklifler


def teklif_uygula(teklif: Teklif, onaylayan: str = "admin", kilit: str | None = None) -> dict[str, Any]:
    """Onaylanmış teklifi panoya işler. Yalnızca UI onay butonundan çağrılır.

    ``kilit`` içinde kilit sözü (varsayılan ``abrakadabra``) geçmiyorsa
    **hiçbir komut uygulanmaz** — ikinci güvenlik kapısı.
    """
    if not kilit_acik(kilit):
        raise AiChatHatasi("Kilit sözü doğrulanmadı — ayrıcalıklı işlem kapalı.")
    if teklif.komut not in IZINLI_KOMUTLAR:
        raise AiChatHatasi(f"izinsiz komut: {teklif.komut}")
    if teklif.komut == "gorev_guncelle":
        task_id, durum = teklif.argumanlar[:2]
        if durum == "done":
            raise AiChatHatasi("done yalnızca onay kuyruğundan verilir (ORCH-08)")
        sonuc = tb.gorev_guncelle(task_id, durum=durum, **{"not": f"{GORUNEN_AD} teklifi ({onaylayan})"})
        if sonuc is None:
            raise AiChatHatasi(f"görev bulunamadı: {task_id}")
        return {"komut": teklif.komut, "task_id": task_id, "durum": durum}
    task_id, ajan, *rest = teklif.argumanlar
    talimat = " ".join(rest)
    try:
        kayit = tr.tetik_ekle(task_id, ajan, talimat=talimat)
    except tr.TriggerError as exc:
        raise AiChatHatasi(str(exc)) from exc
    return {"komut": teklif.komut, "task_id": task_id, "ajan": ajan, "tarih": kayit.get("tarih")}


# ---------------------------------------------------------------------------
# Sohbet
# ---------------------------------------------------------------------------


def _gecmisi_katla(mesajlar: list[Mesaj], son_n: int = 8) -> str:
    """Geçmişi tek prompt'a katlar; kilit sözü modele gitmeden maskelenir."""
    etiket = {"user": "Kullanıcı", "assistant": GORUNEN_AD}
    return "\n".join(f"{etiket[m.rol]}: {kilit_maskele(m.icerik)}" for m in mesajlar[-son_n:])


def sohbet(
    mesajlar: list[Mesaj],
    admin_token: str | None,
    istemci: SohbetIstemcisi | None = None,
    modeller: tuple[str, ...] | None = None,
    baglam: str | None = None,
    ajan: str = "roo",
    hata_kaydi: Callable[[str, str], None] | None = None,
    araclar: bool = False,
) -> tuple[str, str]:
    """Sohbet turu çalıştırır; ``(yanit, kullanilan_model)`` döner.

    * Admin token yoksa çağrı yapılmaz (``AiChatHatasi``).
    * Modeller sırayla denenir; ``NineRouterError`` türevleri bir sonrakine
      düşürür. Hepsi düşerse ``AiChatHatasi`` (son hata mesajıyla).
    * ``hata_kaydi(model, hata)`` her düşüşte çağrılır (UI'da gösterim için).
    * ``araclar=True`` (yalnız İÇ/ODIN): sistem promptuna ``ARAC_PROTOKOLU``
      eklenir; model ``ARA:``/``GETIR:`` yazarsa :mod:`odin_ai.arac_dongusu`
      web aracını çalıştırıp aynı modele geri sorar (tavan ``MAKS_TUR``).
      Müşteri panelinde (DIŞ) bu bayrak **asla** açılmaz.
    """
    if not admin_token:
        raise AiChatHatasi("Admin token zorunlu — önce giriş yapın.")
    if not mesajlar or mesajlar[-1].rol != "user":
        raise AiChatHatasi("Son mesaj kullanıcıya ait olmalı.")

    istemci = istemci or NineRouter()
    zincir = modeller or model_zinciri()
    baglam = baglam if baglam is not None else baglam_metni(ajan)
    protokol = f"{ad.ARAC_PROTOKOLU}\n\n" if araclar else ""
    system = f"{SISTEM_PROMPT}\n\n{protokol}{baglam}"
    prompt = _gecmisi_katla(mesajlar)

    son_hata = "model zinciri boş"
    for model in zincir:
        try:
            yanit = istemci.chat(prompt, model=model, system=system, temperature=0.2)
        except NineRouterError as exc:
            son_hata = f"{model}: {exc}"
            if hata_kaydi:
                hata_kaydi(model, str(exc))
            continue
        if isinstance(yanit, str) and yanit.strip():
            if araclar and hasattr(istemci, "web_fetch"):
                # Araç turlarında aynı model kullanılır; tur içi düşüş zincire
                # geri dönmez (ponytail: tur ortasında model değişimi yok).
                sonuc = ad.arac_dongusu(
                    lambda p: istemci.chat(p, model=model, system=system, temperature=0.2),
                    prompt, yanit, istemci,  # type: ignore[arg-type]
                )
                return sonuc.yanit, model
            return yanit.strip(), model
        son_hata = f"{model}: boş yanıt"
        if hata_kaydi:
            hata_kaydi(model, "boş yanıt")

    # Fallback: NineRouter başarısız — OpenRouter'a doğrudan çağrı yap
    try:
        yanit_or = _openrouter_fallback(prompt, system)
        if yanit_or:
            return yanit_or, "openrouter-fallback"
    except Exception as fallback_exc:
        if hata_kaydi:
            hata_kaydi("openrouter-fallback", str(fallback_exc))

    raise AiChatHatasi(f"Tüm sağlayıcılar düştü — son hata: {son_hata}")


def _openrouter_fallback(prompt: str, system: str | None = None) -> str | None:
    """OpenRouter doğrudan API çağrısı fallback.

    NineRouter zinciri tümü başarısız olunca son çare olarak OpenRouter'a
    doğrudan HTTP POST ile gidilir. Hata durumunda None döner (istisna fırlatmaz).

    Args:
        prompt: İstemci soru metni (tarih + mesajlar birleştirilmiş)
        system: Sistem prompt'ı (opsiyonel)

    Returns:
        Yanıt metni ya da None (hata/timeout durumunda)
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "meta-llama/llama-3.1-70b-instruct",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
        }

        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()

        data = resp.json()
        yanit = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return yanit.strip() if yanit else None
    except Exception:
        return None
