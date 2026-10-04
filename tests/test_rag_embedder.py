#!/usr/bin/env python3
"""ALTYAPI-RAG-EMBEDDER-01 — sahte hash embedder mandalı.

Kontrol edilenler:
  (a) `odin_ai.rag` içinde `hashlib` YOK  — sahte embedder silindi
  (b) `odin_ai.rag.Embedder` ile `vector.embedder.Embedder` AYNI NESNE
      (D-211 ikiz yapı yasağı, D-230 gövde kopyası yasağı)
  (c) varsayılan model EVREN'e bağlı ve koda GÖMÜLMEZ (`.env` okunur)

AĞ GEREKMEZ: testler sahte istemci kullanır. Canlı ölçüm teslim özetindedir
(ölçüldü: 4096 boyut, k(demir,metal)=0.8428 > k(demir,gıda)=0.6767).

KÖPRÜ (D-184): kod src/company_master/odin_ai/rag.py +
src/company_master/vector/embedder.py · görev plans/brief_yasu_ALTYAPI-RAG-EMBEDDER-01.md
· hub hubs/TOOLS_SCRIPTS_HUB.md
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import company_master.odin_ai.rag as rag  # noqa: E402
from company_master.vector import embedder as vec  # noqa: E402


# --- (a) hashlib kalıntısı yok ------------------------------------------------
def test_rag_hicbir_hashlib_yok():
    kaynak = Path(rag.__file__).read_text(encoding="utf-8")
    assert "hashlib" not in kaynak, (
        "odin_ai/rag.py icinde hashlib var — sahte embedder geri gelmis"
    )
    assert "sha256" not in kaynak, "sha256 kalintisi var"


# --- (b) tek embedder: ayni nesne --------------------------------------------
def test_embedder_ayni_nesne():
    assert rag.Embedder is vec.Embedder, (
        "odin_ai.rag.Embedder ayri bir sinif — D-211 ikiz yapi"
    )
    assert rag.EmbeddingResult is vec.EmbeddingResult, "EmbeddingResult ikizi var"
    assert rag.embed_texts is vec.embed_texts, "embed_texts ikizi var"


# --- geriye donuk isimler korunmus ------------------------------------------
def test_geriye_donuk_isimler_korunmus():
    for ad in ("Embedder", "EmbeddingResult", "embed_texts",
               "Chunk", "chunk_metin", "chunk_bol", "chunk_topla"):
        assert hasattr(rag, ad), f"geriye donuk isim kayboldu: {ad}"


# --- chunk fonksiyonlari saglam kalmali (brif adim 2) -----------------------
def test_chunk_davranisi_degismedi():
    parcalar = rag.chunk_metin("bu bir test metnidir", boyut=10)
    assert parcalar and all(c.boyut <= 10 for c in parcalar)
    assert rag.chunk_bol("a\n\nb\n\n") == ["a", "b"]
    assert rag.chunk_topla([]) == ""
    c1 = rag.Chunk("abc", 0, 3, 3, "abc")
    c2 = rag.Chunk("def", 3, 6, 3, "def")
    assert rag.chunk_topla([c2, c1]) == "abcdef"


# --- (c) varsayilan model EVREN ve gomulu degil ------------------------------
def test_varsayilan_model_evren_ve_koda_gomulu_degil():
    assert vec.DEFAULT_EMBED_MODEL == "qwen3-embedding-8b", (
        f"beklenen qwen3-embedding-8b, bulundu {vec.DEFAULT_EMBED_MODEL}"
    )
    kaynak = Path(vec.__file__).read_text(encoding="utf-8")
    assert "EVREN_EMBED_MODEL" in kaynak, (
        "model koda gomulmus — .env uzerinden okunmali (brif adim 4)"
    )


# --- Evren istemcisi sahte vektor dondurur (ag gerekmez) --------------------
class _SahteEvren:
    """4096 boyutlu sahte vektor dondurur; ag cagrisi yapmaz."""

    def __init__(self, *a, **kw) -> None:
        pass

    def embed(self, texts, model):
        return [[0.1 * i] * 4096 for i, _ in enumerate(texts)]


def test_embed_sahte_istemciyle_calisir():
    e = vec.Embedder(client=_SahteEvren())
    sonuc = e.embed(["bir", "iki", "uc"])
    assert sonuc.ok_count == 3, f"beklenen 3, {sonuc.ok_count}"
    assert sonuc.failed_count == 0
    assert len(sonuc.embeddings[0]) == 4096


def test_bos_metin_atlanir():
    e = vec.Embedder(client=_SahteEvren())
    sonuc = e.embed(["", "   ", "gecerli"])
    assert sonuc.ok_count == 1, f"bos metinler atlanmali, {sonuc.ok_count} alindi"


if __name__ == "__main__":
    testler = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in testler:
        t()
        print(f"[PASS] {t.__name__}")
    print(f"\n[TUM TESTLER GECTI] {len(testler)} test")
