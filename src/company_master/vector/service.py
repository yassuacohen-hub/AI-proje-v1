# -*- coding: utf-8 -*-
"""9R-02: VectorService — yuksek seviye semantik islemler.

Firma kayitlarini vektorlestirip store'a yazar ve benzerlik/dublikasyon
sorgulari yapar. Bu katman `entity_resolution/matcher.py` tarafindan
vektor skoru saglamak icin kullanilir.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Iterable

from .embedder import Embedder
from .store import EmbeddedVectorStore, SearchHit, VectorDoc

logger = logging.getLogger(__name__)

# OpenTelemetry tracing
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

if OTEL_AVAILABLE:
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    jaeger_host = os.getenv("JAEGER_HOST", "localhost")
    jaeger_port = int(os.getenv("JAEGER_PORT", "6831"))
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=jaeger_port,
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    RequestsInstrumentor().instrument()
else:
    tracer = None

# --- VERI-RAG-KORPUS-01: korpus beyaz listesi (D-247) -------------------
#
# Siyah liste DEGIL, beyaz liste: yeni kolon eklendiginde otomatik olarak
# korpusa girmez. Kisisel veri (TCKN, telefon, e-posta, adres) hicbir yolla
# metne yazilmaz.
#
# OLÇÜM (canli DB, 2026-10-02) — bu liste varsayımla degil ölçümle kuruldu:
#   * `description` CİKARILDI: 632 dolu kaydin 624'ü (%98.7) adres deseni.
#     Kolonun adi "description" ama icerigi adres; korpusa koymak D-247
#     ihlaliydi. Faaliyet tairifi yerine `sector_name` kullanilir
#     (7595 dolu, adres deseni 0).
#   * `tax_number` zaten yok: D-248 gereği TCKN de bu kolona yazılabiliyor.
#   * `legal_name` icindeki 33 adres-deseni eslesmesi YANLIS POZITIF
#     (MAHIR, MAHMUT, KAPTAN, "CADDE KEBAP", "BLOK TUĞLA").
#
# Alan sirasi metin okunabilirligi icin onemsiz; her alan " | " ile ayrilir.
KORPUS_ALANLARI: tuple[str, ...] = (
    "legal_name",          # firma adi (zorunlu)
    "nace_code",           # NACE kodu -> aciilimla birlikte yazilir
    "nace_source",         # kodun KAYNAGI (D-252: kayitli / tahmin ayrimi)
    "nace_validity",       # dogrulama durumu
    "sector_name",         # faaliyet tairifi (adres degil)
    "employee_count",      # calisan sayisi bandi
    "is_ankara",           # bolge
    "is_osb_member",       # OSB uyeligi
    "source_name",         # kaynak adi
    "updated_at",          # son guncelleme
)

# Bos deger sayilanlar (metne "None" yazmamak icin)
_BOS_DEGERLER = frozenset(("-", "yok", "none", "n/a", "null", "bilinmiyor"))

# Kisisel veri desenleri — metin uretimi sonrasi taranir (D-247).
#
# TCKN deseni HEX-DUYARLIDIR: sinirlar [0-9A-Fa-f] disinda bir karakter
# ister. Aksi halde kunyedeki UUID'nin hex kuyrugu 11 haneli sayi gibi
# gorunur. Canli olcumde bu hata 44 GERCEK kaydi reddediyordu
# (orn. `...-b413-a05368782388` -> `05368782388`); duzeltildi.
# Dogrulama: gecerli UUID eslesmez, gercek TCKN `12345678901` eslesir.
KORPUS_KISISEL_DESENLER: dict[str, re.Pattern[str]] = {
    "TCKN": re.compile(r"(?<![0-9A-Fa-f])\d{11}(?![0-9A-Fa-f])"),
    "telefon": re.compile(
        r"(?<![0-9A-Za-z])(?:\+90|0)[\s-]?(?:5\d{2}|2\d{2}|3\d{3})"
        r"[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}(?![0-9A-Za-z])"
    ),
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
}

# Kaynak kunyesi ayiraci. Kuyne bu ayracla metnin SONUNDA durur.
KUNYE_AYRAC = " | Kaynak: "


class KorpusHatasi(ValueError):
    """Korpus metni uretilemedi (kimlik alani yok)."""


@dataclass(frozen=True)
class KorpusKaydi:
    """Indekslenebilir tek firma kaydi: metin + kaynak kunyesi.

    `metin` alani KUNYEYI ICERIR. Kuynesiz kayit uretilemez; uretilirse
    `metin_siz()` kontrolu ile yakalanir.
    """

    firma_id: str
    metin: str
    kunye: str
    nace_kod: str | None
    nace_kaynak: str | None
    sahis_firmasi: bool = False

    def metin_siz(self) -> bool:
        """Kunye metnin icinde gercekten var mi (dogrulanabilir test)."""
        return KUNYE_AYRAC in self.metin and self.kunye in self.metin


def korpus_kunyesi(
    firma_id: str, kaynak_adi: str | None, guncelleme: str | None
) -> str:
    """Kaynak kunyesi: `firma_id · kaynak_adi · guncelleme`.

    Kuyne bos olamaz: Mimir kaynak satiri yazamaz, prompt kurali 3 coker
    (brif adim 3). Eksik parca yerine acik metin yazilir — utku, "bilinmiyor"
    demek siradan az bilgidir, sessizlik yalandir.
    """
    return " · ".join(
        [
            str(firma_id or "firma_id-yok"),
            str(kaynak_adi).strip() if kaynak_adi else "kaynak-yok",
            str(guncelleme)[:19] if guncelleme else "tarih-yok",
        ]
    )


def _nace_acilimi(kod: str | None, nace_sozlugu: dict[str, str] | None) -> str:
    """NACE kodunu aciilimiyla birlikte yazar (D-252: hiyerarsi korunur).

    Kod sozlukte yoksa yalniz kod yazilir; sahte aciLIM uydurulmaz.
    """
    if not kod:
        return ""
    kod = str(kod).strip()
    if nace_sozlugu and kod in nace_sozlugu:
        return f"{kod} ({nace_sozlugu[kod]})"
    return kod


def firma_korpus_metni(
    row: dict[str, Any],
    nace_sozlugu: dict[str, str] | None = None,
) -> tuple[str, str]:
    """Firma satirindan korpus metni + kunye dondurur.

    Yalniz `KORPUS_ALANLARI` okunur; listeye disinda alan tasmaz.

    Returns:
        (metin, kunye)

    Raises:
        KorpusHatasi: `legal_name` bos ise. Kimliksiz metin indekslenmez.
    """
    ad = str(row.get("legal_name") or "").strip()
    if not ad:
        raise KorpusHatasi("legal_name bos; korpus metni uretilemez")

    parcalar: list[str] = [ad]
    for alan in KORPUS_ALANLARI[1:]:
        ham = row.get(alan)
        if ham is None:
            continue
        if alan == "nace_code":
            deger = _nace_acilimi(ham, nace_sozlugu)
        else:
            deger = str(ham).strip()
        if not deger or deger.lower() in _BOS_DEGERLER:
            continue
        parcalar.append(deger)

    kunye = korpus_kunyesi(
        str(row.get("company_id") or ""),
        row.get("source_name"),
        row.get("updated_at"),
    )
    metin = " | ".join(parcalar) + KUNYE_AYRAC + kunye
    return metin, kunye


def korpus_kaydi(
    row: dict[str, Any],
    nace_sozlugu: dict[str, str] | None = None,
) -> KorpusKaydi:
    """Tek satirdan indekslenebilir kayit uretir."""
    metin, kunye = firma_korpus_metni(row, nace_sozlugu)
    return KorpusKaydi(
        firma_id=str(row.get("company_id") or ""),
        metin=metin,
        kunye=kunye,
        nace_kod=str(row["nace_code"]) if row.get("nace_code") else None,
        nace_kaynak=str(row["nace_source"]) if row.get("nace_source") else None,
        sahis_firmasi=sahis_firmasi_tagi(row),
    )


def kisisel_veri_tara(metin: str) -> list[str]:
    """Metinde kisisel veri deseni var mi? (D-247)

    Donen liste bos ise metin indekslenebilir. Kuyruk `bilinmiyor`
    icermez; desen adlari doner.
    """
    return [ad for ad, des in KORPUS_KISISEL_DESENLER.items() if des.search(metin)]


# --- Chunk karari: olcumle, varsayimla degil ----------------------------
#
# Canli DB olcumu (9412 firma, 2026-10-02):
#   medyan 275 krk | en uzun 448 krk | 200+ krk 9216 kayit (%98.4)
#
# Ilk 50 satirlik olcum "0/50 >200 krk" demişti ve CHUNK YOK denmisdi.
# O olcum HATALIYDI: NACE sozlugunu yalnizca `level=4` (306 kod) ile
# kurmustu, uretimdeki join ise 3319 kod kullanir. Acilimlar metne
# eklenince metin buyudü. D-255/4: olcumun kapsami kararin kapsamini
# belirlemez.
#
# Karar olcutu "200 karakter" degil, EMBEDDER PENCERESIDIR:
#   * vector/embedder.py -> text-embedding-3-small, `truncation` YOK
#     => kisa metin kırpılmaz, hata da vermez. Pencere 8191 token.
#   * odin_ai.Embedder -> yerel SHA-256 vektorleyici, pencere YOK.
#   * en uzun korpus metni 448 krk ~= 130 token = pencerenin %1.6'si.
#
# Sonuc: chunk GEREKMIYOR. Ve chunk_metin(boyut=200) %50 ortusmeyle
# 275 krk metni ~4 parcaya bolup vektor sayisini ~3.5x katlardi; benzerlik
# aramasinda oertusen kopyalari kirlestirir. Tek kayit/firma daha saglam.
EMBEDDER_TOKEN_LIMITASI = 8191
KRKR_BASINA_TOKEN_TAHMINI = 3.5  # TR/ASCII karisim ortalama


# --- Sahis firmasi tespiti (KAHİN karari 2026-10-02) --------------------
#
# KAHİN: "Şahıs şirketlerinde LTD ŞTİ gibi ünvanlar geçmez. Kolonlarda
# isim soy isim VE vergi no kolonunda TC olarak yazılmışsa bu bir şahıs
# şirketidir, KVKK girer."
#
# Yani tespit iki bacaklıdır:
#   1. UNVAN YOK  — A.Ş./LTD/ŞTİ/KOL/KOM/HOLDİNG/GRUB/ŞİRKET/MOBİLYA...
#      Ünvanı olan bir kayıt tüzel kişidir; kisi adi taşısa bile şahıs
#      firması DEĞİLDİR ("MEHMET ÖZBEK LTD. ŞTİ." tüzel kuruluştur).
#   2. KİMLİK      — vergi no kolonunda GEÇERLİ TC, ya da unvansız isim
#      "İSİM SOYİSİM" kalıbında (2-4 kelime, hepsi alfabetik, rakam yok).
#
# Önceki sezgi (`kisi_adi_on_eki`, 910 kayıt) KAHİN'in tanımı DEĞİLDİ:
# o kural '-' ayracına bakıyordu ve unvanı olan kayıtları da yakalıyordu.
# KAHİN açıkça "şahıs şirketlerinde ünvan geçmez" dedi; ölçüm unvanı olan
# 7016 kaydın (tüzel) şahıs sayılmasını engelliyor. Sezgi KALDIRILDI.
#
# TESPİTTİR, KARAR DEĞİLDİR. Bayrak `KorpusKaydi.sahis_firmasi` üzerinde
# taşınır; kayıt korpusta kalır. Silmek geri alınamaz ve %25.5'e varan
# bir veri kaybıdır — karar orkestratöründür (D-260: karar ölçümle,
# varsayımla değil).

# --- Şahıs işletmesi tespiti: TEK KAPI (D-211) -------------------------
#
# Aşağıdaki üç yardımcı burada DEĞİLDİR, `etl/firma_turu.py`'de yaşar:
# `_UNVAN_DESENI` (geniş tüzel eleme), `_tc_gecerli_mi` (TCKN sağlama),
# `isim_soyisim_kalibi` (isim+soyisim kalıbı), `sahis_firmasi_tagi`.
#
# Neden: aynı soruyu ikinci bir yerde cevaplamak ikizdir. İkizden biri
# düzeltilir, diğeri bayatlar ve ikisi de "doğru" görünür.
#
# Buradaki import **tekrar tanım değildir** — yönlendirmedir. Kanıt:
# `tests/test_ikiz_tanim_yok.py` bu dosyada ikinci bir regex/fonksiyon
# gövdesi bulamaz.
#
# Kuralın kendisi ve KAHİN'in 7 ticaret şirketi türü sözlüğü:
# `company_master.etl.firma_turu`
from ..etl.firma_turu import (  # noqa: F401  (yeniden dışa aktarım)
    ANONIM,
    KOLEKTIF,
    KOOPERATIF,
    LIMITED,
    SAHIS,
    TURLER,
    firma_turu,
    isim_soyisim_kalibi,
    kvkk_kapsaminda,
    sahis_isletmesi_mi,
    tc_gecerli_mi,
)

# Eski iç ad; tek tanım yukarıdan gelir (D-211 ikiz yasağı).
_tc_gecerli_mi = tc_gecerli_mi

# Korpus katmanındaki adlandırma korunur (57 test buna bağlı):
sahis_firmasi_tagi = sahis_isletmesi_mi


def chunk_gerekli(
    metinler: Iterable[str], token_limitasi: int = EMBEDDER_TOKEN_LIMITASI
) -> tuple[bool, int, float]:
    """Chunk'a ihtiyac var mi? Olcumle karar verir.

    Args:
        metinler: korpus metinleri.
        token_limitasi: embedder pencere limiti (token).

    Returns:
        (gerekli_mi, en_uzun_karakter, en_uzun_token_orani)

    `orani >= 1.0` ise metin pencereye sigmaz -> chunk zorunludur.
    """
    en_uzun = max((len(m) for m in metinler), default=0)
    token_tahmini = int(en_uzun / KRKR_BASINA_TOKEN_TAHMINI)
    oran = token_tahmini / token_limitasi if token_limitasi else 1.0
    return oran >= 1.0, en_uzun, oran



def korpus_icerigi(kayit_metin: str) -> str:
    """Kunye ayiklanmis icerik: kisisel veri taramasi SADECE bunu gorur.

    Neden: kunye makine uretilmistir (UUID + kaynak adi + tarih) ve
    alanlarin hicbiri kisisel veri degildir. Oyleyse taramak yalnizca
    YANLIIS POZITIF uretir — canli olcumde UUID kuyrugu 11 haneli
    ("...a05368782388") ve 12 haneli ("...-033034123829") dizileri
    TCKN/telefon sanildi. Icerik taranir, kunye insa ile dogrulanir.
    """
    if KUNYE_AYRAC in kayit_metin:
        return kayit_metin.split(KUNYE_AYRAC, 1)[0]
    return kayit_metin


def korpus_kayitlarini_uret(
    rows: Iterable[dict[str, Any]],
    nace_sozlugu: dict[str, str] | None = None,
) -> tuple[list[KorpusKaydi], list[tuple[str, str]]]:
    """Satirlari toplu indekslenebilir kayitlara cevirir (hata toleransli).

    Returns:
        (basarili_kayitlar, hatalar) — hatalar `(firma_id, sebep)`.
        basarisiz kayit SESSIZCE dusurulmez; listelenir (brif adim 5).

    Sahis firmasi olan kayit SILINMEZ; `KorpusKaydi.sahis_firmasi=True`
    isaretlenir. cagiran `sum(k.sahis_firmasi for k in basarili)` ile
    sayar. Silme karari orkestratorundur (KAHİN 2026-10-02 tespit karari).
    """
    basarili: list[KorpusKaydi] = []
    hatalar: list[tuple[str, str]] = []

    for row in rows:
        fid = str(row.get("company_id") or "satir-kimligi-yok")
        try:
            kayit = korpus_kaydi(row, nace_sozlugu)
        except KorpusHatasi as exc:
            hatalar.append((fid, str(exc)))
            continue
        except Exception as exc:  # pragma: no cover - beklenmeyen alan tipi
            hatalar.append((fid, f"beklenmeyen: {exc}"))
            continue

        sizinti = kisisel_veri_tara(korpus_icerigi(kayit.metin))
        if sizinti:
            hatalar.append((fid, f"kisisel veri deseni: {','.join(sizinti)}"))
            continue
        if not kayit.metin_siz():
            hatalar.append((fid, "kaynak kunyesi eksik; indekslenmedi"))
            continue
        basarili.append(kayit)

    return basarili, hatalar


# Firma metnine cevrilecek kayit alanlari (varsa)
_FIRMA_ALANLARI = (
    "legal_name", "unvan", "firma_adi", "company_name", "name",
    "faaliyet_konusu", "faaliyet", "description", "is_alani", "sektor",
    "nace_kodu", "nace_code",
)


def firma_metni(row: dict[str, Any]) -> str:
    """Firma kaydindan semantik arama icin tek metin uretir."""
    parts: list[str] = []
    for key in _FIRMA_ALANLARI:
        val = row.get(key)
        if val is None:
            continue
        if isinstance(val, (list, tuple)):
            val = ", ".join(str(v) for v in val if v)
        val = str(val).strip()
        if val and val.lower() not in ("-", "yok", "none", "n/a"):
            parts.append(val)
    return " | ".join(parts)


@dataclass
class DuplicateGroup:
    """Ayni VKN / benzer unvanli firma grubu."""
    vkn: str
    ids: list[str]
    scores: list[float]
    texts: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "vkn": self.vkn,
            "ids": self.ids,
            "scores": [round(s, 6) for s in self.scores],
            "texts": self.texts,
        }


class VectorService:
    """Embed + store + benzerlik sorgusu tek noktasi."""

    def __init__(
        self,
        embedder: Embedder | None = None,
        store: EmbeddedVectorStore | None = None,
    ) -> None:
        self.embedder = embedder or Embedder()
        self.store = store or EmbeddedVectorStore()
        self.tracer = tracer

    def embed_document(self, doc: VectorDoc) -> None:
        """Tek dokumani vektorle ve store'a yaz."""
        if self.tracer is not None:
            with self.tracer.start_as_current_span("embed_document") as span:
                result = self.embedder.embed([doc.metadata.get("text", "") or "firma"])
                if not result.embeddings:
                    return
                doc.vector = result.embeddings[0]
                self.store.upsert([doc])
        else:
            result = self.embedder.embed([doc.metadata.get("text", "") or "firma"])
            if not result.embeddings:
                return
            doc.vector = result.embeddings[0]
            self.store.upsert([doc])

    def index_firmalar(
        self,
        rows: Iterable[dict[str, Any]],
        id_key: str = "company_id",
    ) -> int:
        """Firma satirlarini embed + store'a toplu yazar.

        Her satir icin id = row[id_key] (yoksa index). metadata'ya
        firma bilgileri + indexlenmis text konur.
        """
        if self.tracer is not None:
            with self.tracer.start_as_current_span("index_firmalar") as span:
                items = list(rows)
                metinler = [firma_metni(r) for r in items]
                result = self.embedder.embed(metinler)
                if not result.embeddings:
                    logger.warning("Embed sonucu bos; hicbir firma indexlenmedi. %s",
                                   result.to_dict())
                    return 0

                docs: list[VectorDoc] = []
                for i, row in enumerate(items):
                    fid = str(row.get(id_key) or row.get("id") or f"row-{i}")
                    meta = {
                        "firm_id": fid,
                        "text": metinler[i],
                        "nace_code": row.get("nace_code") or row.get("nace_kodu") or "",
                        "osb_region": row.get("osb_region") or row.get("bolge") or "",
                        "verification_status": row.get("verification_status") or "unknown",
                        "last_updated": row.get("last_updated") or "",
                    }
                    for k, v in row.items():
                        if k not in meta and not isinstance(v, (dict, list)):
                            meta[k] = str(v)[:200]
                    docs.append(VectorDoc(id=fid, vector=result.embeddings[i], metadata=meta))

                self.store.upsert(docs)
                logger.info("%d firma indexlendi (model=%s)", len(docs), result.model)
                return len(docs)
        else:
            items = list(rows)
            metinler = [firma_metni(r) for r in items]
            result = self.embedder.embed(metinler)
            if not result.embeddings:
                logger.warning("Embed sonucu bos; hicbir firma indexlenmedi. %s",
                               result.to_dict())
                return 0

            docs: list[VectorDoc] = []
            for i, row in enumerate(items):
                fid = str(row.get(id_key) or row.get("id") or f"row-{i}")
                meta = {
                    "firm_id": fid,
                    "text": metinler[i],
                    "nace_code": row.get("nace_code") or row.get("nace_kodu") or "",
                    "osb_region": row.get("osb_region") or row.get("bolge") or "",
                    "verification_status": row.get("verification_status") or "unknown",
                    "last_updated": row.get("last_updated") or "",
                }
                for k, v in row.items():
                    if k not in meta and not isinstance(v, (dict, list)):
                        meta[k] = str(v)[:200]
                docs.append(VectorDoc(id=fid, vector=result.embeddings[i], metadata=meta))

            self.store.upsert(docs)
            logger.info("%d firma indexlendi (model=%s)", len(docs), result.model)
            return len(docs)

    def find_similar(
        self,
        text: str,
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        """Metin sorgusunu embedleyip en benzer firmalari dondurur."""
        if self.tracer is not None:
            with self.tracer.start_as_current_span("find_similar") as span:
                result = self.embedder.embed([text])
                if not result.embeddings:
                    return []
                return self.store.query(result.embeddings[0], top_k=top_k, where=where)
        else:
            result = self.embedder.embed([text])
            if not result.embeddings:
                return []
            return self.store.query(result.embeddings[0], top_k=top_k, where=where)

    def deduplicate_by_vkn(
        self,
        rows: Iterable[dict[str, Any]],
        id_key: str = "company_id",
        vkn_key: str = "vkn",
    ) -> list[DuplicateGroup]:
        """Ayni VKN'yi paylasan firmalari gruplar ve semantik skorlar.

        Geri donus: her grup icin o grup icindeki tum ciftlerin ortalama
        cosine benzerligi (score) — boylece 'ayni VKN ama farkli firma'
        olanlar dusuk skorla, gercek dupliketler yuksek skorla cikar.
        """
        if self.tracer is not None:
            with self.tracer.start_as_current_span("deduplicate_by_vkn") as span:
                groups: dict[str, list[dict[str, Any]]] = {}
                for row in rows:
                    vkn = str(row.get(vkn_key) or "").strip()
                    if not vkn:
                        continue
                    groups.setdefault(vkn, []).append(row)

                out: list[DuplicateGroup] = []
                for vkn, grup in groups.items():
                    if len(grup) < 2:
                        continue
                    # once index (grup icin sadece embed)
                    metinler = [firma_metni(r) for r in grup]
                    result = self.embedder.embed(metinler)
                    if not result.embeddings:
                        continue
                    ids = [
                        str(r.get(id_key) or r.get("id") or f"row-{i}")
                        for i, r in enumerate(grup)
                    ]
                    scores = _cift_skorlari(result.embeddings)
                    out.append(
                        DuplicateGroup(
                            vkn=vkn, ids=ids, scores=scores, texts=metinler
                        )
                    )
                return out
        else:
            groups: dict[str, list[dict[str, Any]]] = {}
            for row in rows:
                vkn = str(row.get(vkn_key) or "").strip()
                if not vkn:
                    continue
                groups.setdefault(vkn, []).append(row)

            out: list[DuplicateGroup] = []
            for vkn, grup in groups.items():
                if len(grup) < 2:
                    continue
                # once index (grup icin sadece embed)
                metinler = [firma_metni(r) for r in grup]
                result = self.embedder.embed(metinler)
                if not result.embeddings:
                    continue
                ids = [
                    str(r.get(id_key) or r.get("id") or f"row-{i}")
                    for i, r in enumerate(grup)
                ]
                scores = _cift_skorlari(result.embeddings)
                out.append(
                    DuplicateGroup(
                        vkn=vkn, ids=ids, scores=scores, texts=metinler
                    )
                )
            return out


def _cift_skorlari(vecs: list[list[float]]) -> list[float]:
    """Grup vektorlerinin tum cift cosine skorlarini dondurur (sirali)."""
    from .store import _cosine

    scores: list[float] = []
    n = len(vecs)
    for a in range(n):
        for b in range(a + 1, n):
            scores.append(_cosine(vecs[a], vecs[b]))
    scores.sort(reverse=True)
    return scores
