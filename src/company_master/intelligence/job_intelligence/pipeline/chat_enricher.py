# -*- coding: utf-8 -*-
"""Job Intelligence — Chat tabanlı ilan zenginleştirme (9R-03).

9Router ``chat()`` ile bir iş ilanından sektör / pozisyon / yetenek (skill)
çıkarır. 9Router kurulu değilse ya da çağrı hata verirse, aynı sözleşmeyle
yanıt üreten **regex/kural tabanlı fallback** devreye girer. Böylece boru
hattı (pipeline) her koşulda çalışır — API kapalıyken regex skorlayıcı
korunur (docs/9ROUTER_SEMANTIK_KATMAN_MIMARISI.md → 9R-03).

Girdi sözleşmesi: başlık ``title``, açıklama ``description | body | content``.
KVKK notu: ilan açıklaması prompt'a gönderilmeden önce karakter sınırına
(``max_desc_chars``) kesilir; kişisel veri içermeyen ilan metinleri hedeflenir.

Çıktı sözleşmesi: ``EnrichResult.to_dict()`` →
    {"sektor": str, "pozisyon": str, "skills": [str, ...],
     "kaynak": "chat" | "fallback", "hata": str}
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# 9Router istemcisi opsiyonel; hem src.company_master hem company_master
# import path'i denenir (embedder.py ile aynı çift-import deseni).
try:  # src kökü sys.path'te ise
    from src.company_master.gateway.ninerouter_client import NineRouterError  # noqa: F401
    from src.company_master.gateway.ninerouter_client import get_client

    _ISTEMCI_IMPORT_OK = True
except ImportError:  # src doğrudan sys.path'te ise (analyzer testleri gibi)
    try:
        from company_master.gateway.ninerouter_client import NineRouterError  # noqa: F401
        from company_master.gateway.ninerouter_client import get_client

        _ISTEMCI_IMPORT_OK = True
    except ImportError:
        NineRouterError = Exception  # type: ignore[misc]
        get_client = None  # type: ignore[assignment]
        _ISTEMCI_IMPORT_OK = False

# Regex fallback için sektör siparişli anahtar listesi (ilk eşleşen kazanır).
SEKTOR_MAP: list[tuple[str, tuple[str, ...]]] = [
    (
        "BİLİŞİM",
        (
            "yazılım", "developer", "software", "mühendis", "engineer",
            "siber güvenlik", "cyber", "data", "devops", "cloud", "backend",
            "frontend", "fullstack", "full stack", "test", "qa", "product",
            "scrum", "agile", "mobil", "ios", "android", "yapay zeka", "ai",
            "makine öğren", "big data", "büyük veri", "dijital", "web",
            "devrel", "site reliability", "sre", "ux", "ui", "tasarımcı",
            "veri", "analist",
        ),
    ),
    (
        "SAVUNMA & HAVACILIK",
        ("savunma", "uzay", "havacılık", "avionics", "radar", "hidrolik",
         "elektronik harp", "aselsan", "roketsan", "tai", "insansız", "uçak",
         "f-35", "milli muharip"),
    ),
    (
        "ÜRETİM & İMALAT",
        ("üretim", "imalat", "operatör", "makine", "kalite", "kaynak",
         "cnc", "tekniker", "tesis", "fabrika", "montaj", "depo", "ürün",
         "proses", "süreç", "kalıp", "sac", "plc", "scada"),
    ),
    (
        "SATIŞ & PAZARLAMA",
        ("satış", "pazarlama", "marketing", "sales", "ihracat", "bölge",
         "bayi", "müşteri temsilcisi", "call center", "çağrı", "key account",
         "channel", "perakende", "retail", "ticari", "temsilci", "temsilcilik"),
    ),
    (
        "FİNANS & MUHASEBE",
        ("finans", "muhasebe", "accountant", "finance", "mali", "muhasebec",
         "bütçe", "vergi", "denetim", "audit", "banka", "risk yönetim",
         "iç denetim", "kredi", "tahsilat"),
    ),
    (
        "İNSAN KAYNAKLARI",
        ("insan kaynakları", "hr", "ik uzmanı", "işe alım", "recruiting",
         "organizasyonel", "eğitim", "yetiştirme", "kariyer", "iş sağlığı",
         "özlük", "bordro", "maaş"),
    ),
    (
        "LOJİSTİK & DEPO",
        ("lojistik", "nakliye", "kurye", "depo", "stok", "gümrük", "sevkiyat",
         "zincir", "supply", "tedarik", "satın alma", "transport", "kargo"),
    ),
    (
        "SAĞLIK",
        ("sağlık", "hemşire", "doktor", "eczacı", "klinik", "hasta", "tıbbi",
         "medikal", "fizyoterap", "laboratuvar", "diş", "veteriner"),
    ),
    (
        "ENERJİ",
        ("enerji", "elektrik", "güneş", "rüzgar", "jeneratör", "türbin",
         "panel", "inverter", "elektrik mühendis", "güç"),
    ),
    (
        "TARIM & GIDA",
        ("tarım", "ziraat", "agri", "hayvancılık", "sulama", "gıda",
         "besin", "üretim gıda", "gıda mühendis", "fidancılık"),
    ),
]

# Regex fallback için pratik yetenek anahtar listesi (MODERN_TECH_KEYWORDS
# analizörden alınır, üzerine mesleki beceriler eklenir).
EXTRA_SKILL_KEYWORDS: list[str] = [
    "python", "javascript", "typescript", "java", "c#", "c++", "sql", "go",
    "rust", "php", "excel", "powerpoint", "word", "sap", "erp", "crm",
    "satış", "pazarlama", "müzakere", "ihracat", "muhasebe", "bordro",
    "raporlama", "finans", "lojistik", "depo", "stok", "envanter", "kalite",
    "iso", "smm", "rms", "görüntü işleme", "bilgisayar görüsü", "nlp",
    "doğal dil", "otomasyon", "veri analizi", "veri görselleştirme",
]

BELIRSIZ_SEKTOR = "GENEL / BELİRSİZ"

# ``client`` için sentinel: ``ChatEnricher()`` otomatik olarak ``get_client``
# kullanır; ``ChatEnricher(client=None)`` ise net olarak "istemci yok"dur.
_OTOMATIK: Any = object()

_SISTEM_PROMPT = (
    "Sen kurumsal bir işgücü verisi sınıflandırma asistanısın. "
    "Verilen iş ilanını analiz et ve SADECE geçerli tek bir JSON objesi döndür. "
    "Başka hiçbir metin yazma."
)

_KULLANICI_SABLON = (
    "İlan başlığı: {title}\n"
    "İlan açıklaması:\n{desc}\n\n"
    "Şu JSON şemasına göre çıktı üret:\n"
    '{{"sektor": "tek sektör kategorisi (örn. BİLİŞİM, İMALAT, SATIŞ & PAZARLAMA, FİNANS & MUHASEBE, LOJİSTİK & DEPO, SAVUNMA & HAVACILIK, SAĞLIK, ENERJİ, GENEL / BELİRSİZ)", '
    '"pozisyon": "kısa ve anlaşılır pozisyon adı", '
    '"skills": ["beceri_1", "beceri_2"]}}'
)


@dataclass
class EnrichResult:
    """Bir ilanın zenginleştirme sonucu."""

    sektor: str = BELIRSIZ_SEKTOR
    pozisyon: str = ""
    skills: list[str] = field(default_factory=list)
    kaynak: str = "fallback"
    hata: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serileştirilebilir sözlük döndürür (DB/jsonl uyumlu)."""
        return {
            "sektor": self.sektor,
            "pozisyon": self.pozisyon,
            "skills": list(self.skills),
            "kaynak": self.kaynak,
            "hata": self.hata,
        }


def _text_snipper(desc: str, limit: int) -> str:
    """Açıklama metnini verilen karaktere keser (KVKK / maliyet kontrolü)."""
    desc = desc.strip()
    if len(desc) <= limit:
        return desc
    return desc[:limit] + " …[kesildi]"


def _metin_icerir(text: str, kw: str) -> bool:
    """Anahtar kelime araması; 2 karakterli tokenlarda tam eşleşme ister."""
    low = text.lower()
    if len(kw) >= 3:
        return kw in low
    # 2 harfli (örn. "ai", "ml") yanlış pozitifi engelle: word boundary.
    return any(tok == kw for tok in low.replace("-", " ").replace("/", " ").split())


def _temizle_karakterler(s: str) -> str:
    """Yazdırılamaz kontrol karakterlerini atar (C0 hariç, C1 dahil).

    LLM çıktısında bazen C1 kontrol karakterleri (U+0080-U+009F) ya da
    garip baytlar oluşur; bunlar cp1254 konsolda UnicodeEncodeError üretir
    ve veri bütünlüğünü bozar. ASCII yazdırılabilir + Unicode harfler/sayılar
    korunur; NBSP de normalize edilir.
    """
    return "".join(
        c for c in s
        if ord(c) >= 32 and not 0x7F <= ord(c) <= 0x9F
    )


def _titizlestir(v: Any) -> str:
    """Sektör/pozisyon değerini normalleştirir (kontrol karakterleri atılır)."""
    s = str(v or "").strip()
    s = _temizle_karakterler(s)
    return " ".join(s.split()).replace("\xa0", " ")


def _bilesik_metin(posting: dict[str, Any]) -> tuple[str, str]:
    """Postingden başlık ve açıklama alanlarını çeker."""
    title = _titizlestir(posting.get("title"))
    desc_raw = next(
        (posting.get(k) for k in ("description", "body", "content", "text")
         if posting.get(k)),
        "",
    )
    desc = _titizlestir(desc_raw)
    return title, desc


class ChatEnricher:
    """9Router ``chat()`` ile ilan zenginleştirme; hata/eksiklikte fallback.

    Parametreler:
        client: NineRouter istemcisi (opsiyonel; None = yalnız fallback).
        model: chat modeli (varsayılan: istemcinin default_model'i).
        max_desc_chars: prompt'a gönderilecek azami açıklama uzunluğu.
        strict: True ise chat hatalarında fallback yerine hata yükseltilir.
    """

    def __init__(
        self,
        client: Any | None = _OTOMATIK,
        model: str | None = None,
        max_desc_chars: int = 2000,
        strict: bool = False,
        skill_keywords: list[str] | None = None,
        sektor_map: list[tuple[str, tuple[str, ...]]] | None = None,
    ) -> None:
        # Sentinel ile "otomatik get_client" ile "istemci yok (fallback-only)"
        # net biçimde ayrışır. Otomatik dalda fonksiyonun KENDİSİ değil,
        # çağrılmış istemci örneği tutulur (get_client fonksiyonunu saklamak
        # 'function' object has no attribute 'chat' hatasına yol açar).
        if client is _OTOMATIK:
            client = get_client() if callable(get_client) else None
        self._client = client
        self._model = model
        self._max_desc_chars = max(200, int(max_desc_chars))
        self._strict = bool(strict)
        # Fallback sözlükleri enjeksiyonla kolayca test edilebilir.
        self._skill_keywords = list(
            skill_keywords if skill_keywords is not None else EXTRA_SKILL_KEYWORDS
        )
        self._sektor_map = list(sektor_map or SEKTOR_MAP)

    @property
    def available(self) -> bool:
        """9Router istemcisi kurulu mu (ağ çağrısı yapmaz)."""
        # hasattr koruması: yanlışlıkla fonksiyon geçilirse (get_client)
        # chat yeteneği yokmuş gibi davran → fallback kullan.
        return self._client is not None and hasattr(self._client, "chat")

    # ---- genel kullanım ----

    def enrich(self, posting: dict[str, Any]) -> EnrichResult:
        """Tek ilanı zenginleştirir (chat → fallback öncelik sırası)."""
        title, desc = _bilesik_metin(posting)
        if not title:
            return EnrichResult(
                pozisyon="",
                hata="title boş: zenginleştirme yapılamadı",
            )
        if self._client is None:
            return self._fallback(title, desc)

        try:
            prompt = _KULLANICI_SABLON.format(
                title=title,
                desc=_text_snipper(desc or "—", self._max_desc_chars),
            )
            raw = self._client.chat(
                prompt,
                model=self._model,
                system=_SISTEM_PROMPT,
                temperature=0.1,
                max_tokens=256,
            )
        except Exception as exc:  # noqa: BLE001 — ağ/API her tür hata verebilir
            if self._strict:
                raise
            logger.warning(
                "ChatEnricher: chat çağrısı başarısız, fallback kullanılıyor (%s)",
                _kisa_hata(exc),
            )
            result = self._fallback(title, desc)
            result.hata = f"chat_hatasi: {_kisa_hata(exc)}"
            return result

        parsed = _json_cevir(raw)
        if parsed is None:
            if self._strict:
                raise NineRouterError(
                    "ChatEnricher: JSON çıktı ayrıştırılamadı: %s" % raw[:300]
                )
            logger.warning(
                "ChatEnricher: JSON ayrıştırılamadı, fallback kullanılıyor (%s)",
                raw[:200],
            )
            result = self._fallback(title, desc)
            result.hata = "chat_json_parse_hatasi"
            return result

        return self._chat_sonuc(parsed)

    def enrich_many(
        self,
        postings: list[dict[str, Any]],
        limit: int | None = None,
    ) -> list[EnrichResult]:
        """Birden çok ilanı zenginleştirir (opsiyonel azami adet)."""
        hedef = postings if limit is None else postings[: limit]
        return [self.enrich(p) for p in hedef]

    # ---- iç yardımcılar ----

    def _chat_sonuc(self, parsed: dict[str, Any]) -> EnrichResult:
        """LLM JSON çıktısını EnrichResult'a normalize eder."""
        sektor = _titizlestir(parsed.get("sektor")).upper() or BELIRSIZ_SEKTOR
        pozisyon = _titizlestir(parsed.get("pozisyon"))
        skills = parsed.get("skills") or []
        if isinstance(skills, str):
            skills = [skills]
        skill_lista = [
            _titizlestir(s)
            for s in skills
            if _titizlestir(s)
        ]
        return EnrichResult(
            sektor=sektor,
            pozisyon=pozisyon,
            skills=skill_lista,
            kaynak="chat",
        )

    def _fallback(self, title: str, desc: str) -> EnrichResult:
        """Regex/kural tabanlı deterministik zenginleştirme (API yoksa)."""
        sektor = self._sektor_bul(title, desc)
        pozisyon = title or ""
        skills = self._skills_bul(title, desc)
        return EnrichResult(
            sektor=sektor,
            pozisyon=pozisyon,
            skills=skills,
            kaynak="fallback",
        )

    def _sektor_bul(self, title: str, desc: str) -> str:
        """İlk eşleşen sektör kategorisini döndürür; bulamazsa belirsiz."""
        metin = f"{title} {desc}".lower()
        for sektor, anahtarlar in self._sektor_map:
            if any(_metin_icerir(metin, k) for k in anahtarlar):
                return sektor
        return BELIRSIZ_SEKTOR

    def _skills_bul(self, title: str, desc: str) -> list[str]:
        """Başlık+açıklamada geçen yetenek anahtarlarını sıralı toplar."""
        metin = f"{title} {desc}".lower()
        bulunan: list[str] = []
        for kw in self._skill_keywords:
            if _metin_icerir(metin, kw) and kw not in bulunan:
                bulunan.append(kw)
        return bulunan


def _json_cevir(text: str) -> dict[str, Any] | None:
    """Model yanıtındaki ilk JSON objesini ayıklayıp sözlüğe çevirir."""
    if not text:
        return None
    t = text.strip()
    # ```json ... ``` blok sarımı varsa sıyır.
    if t.startswith("```"):
        t = t.strip("`")
        if t.lower().startswith("json"):
            t = t[4:]
    bas = t.find("{")
    son = t.rfind("}")
    if bas == -1 or son == -1 or son <= bas:
        return None
    try:
        veri = json.loads(t[bas : son + 1])
    except (json.JSONDecodeError, TypeError):
        return None
    return veri if isinstance(veri, dict) else None


def _kisa_hata(exc: Exception) -> str:
    """İstisna mesajını tek satıra sıkıştırır (log/kullanıcı güvenliği)."""
    msg = str(exc) or exc.__class__.__name__
    return " ".join(msg.split())[:200]


def build_default_enricher(
    model: str | None = None,
    skill_keywords: list[str] | None = None,
) -> ChatEnricher:
    """Kurulu istemciyle (ya da fallback için None ile) hazır enricher üretir.

    client parametresi bilerek geçilmez: ``_OTOMATIK`` sentineli kurulumu
    üstlenir ve ``get_client()`` (çağrılmış örnek) ile chat yeteneği kurar.
    """
    return ChatEnricher(
        model=model,
        skill_keywords=skill_keywords,
    )