# ALTYAPI-RAG-EMBEDDER-01 — Brief (yasu)

**Başlık:** [ALTYAPI] Sahte hash embedder'ı sil, EVREN qwen3-embedding-8b'ye bağla (2 saat)
**Öncelik:** P0 · **Kit:** `ALTYAPI-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/odin_ai/rag.py`
**Hub:** `hubs/TOOLS_SCRIPTS_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden

RAG'in temeli kırık. `odin_ai/rag.py` içindeki `Embedder` sınıfı `hashlib.sha256` ile **16 boyutlu** bir vektör üretiyor. Bu vektör anlamsal benzerlik taşımaz: "döküm" ile "metal işleme" arasında hiçbir yakınlık çıkmaz. Yani arama çalışıyor gibi görünür, **yanlış firmaları getirir**.

Aynı projede **gerçek** embedder zaten var: `src/company_master/vector/embedder.py` (9Router `NineRouter.embed()` sarmalayıcısı, batch + retry + `EmbeddingResult`). `vector/service.py` ve `intelligence/vector_search.py` bunu kullanıyor. **İki embedder = D-211 ikiz yapı ihlali.**

Ayrıca gerçek embedder'ın varsayılan modeli `openrouter/openai/text-embedding-3-small` — bizim ücretsiz kanalımız EVREN. EVREN'de canlı doğrulanmış tek embedding modeli: **`qwen3-embedding-8b`**.

## Doğrulanacak varsayım

| # | Varsayım | Nasıl ölçülür | Yanlışsa |
|---|---|---|---|
| 1 | `qwen3-embedding-8b` `/v1/embeddings` ucundan yanıt verir | 3 kısa Türkçe metinle gerçek çağrı; dönen vektör boyutunu **yazdır** | Brif durur, chat'e sorun aç — model adı/uç yanlış |
| 2 | Türkçe anlamsal yakınlık çalışıyor | "demir dökümü" ↔ "metal döküm" kosinüs > "demir dökümü" ↔ "gıda paketleme" | Model Türkçe'de zayıf; chat'e yaz, karar İhsan'a |
| 3 | `odin_ai/rag.Embedder`'ın başka çağıranı yok | `grep -r "odin_ai.rag import" src tests scripts` | Çağıran varsa tek tek `vector/embedder`'a çevir |

**Boyut sabit yazmayacaksın.** Modelin döndürdüğü boyut neyse o. "4096 olmalı" gibi varsayım kurma (D-260: beyan ≠ kanıt).

## Adımlar

1. **Ölç önce:** `qwen3-embedding-8b` ile 3 metin embed et, boyutu ve 2. varsayımın kosinüslerini yazdır. Çıkmazsa DUR.
2. `odin_ai/rag.py` içinden `Embedder` sınıfını ve `hashlib` importunu **sil**. `Chunk`, `chunk_metin`, `chunk_bol`, `chunk_topla` **kalacak** — bunlar sağlam.
3. `odin_ai/rag.py` başına tek satır yönlendirme: `from ..vector.embedder import Embedder, EmbeddingResult, embed_texts  # noqa: F401` (geriye dönük isim korunur, gövde kopyalanmaz — D-230).
4. `vector/embedder.py` içindeki `DEFAULT_EMBED_MODEL` değerini EVREN modeline çevir. Değeri **koda gömme**, `os.environ.get("EVREN_EMBED_MODEL", "qwen3-embedding-8b")` desenini kullan.
5. Mandal: `tests/test_rag_embedder.py` — (a) `odin_ai.rag` içinde `hashlib` **yok** assert'i, (b) `Embedder`'ın `vector.embedder.Embedder` ile **aynı nesne** olduğu assert'i. Mandalı **kırarak** doğrula (D-256/4): sahte sınıfı geçici geri koy, test kırmızı olmalı.
6. `python -m pytest tests/ -q` tam koşu — kırdığın bayat test varsa düzelt, sessizce atlama.

## Kabul kriteri

| # | Şart | Kanıt |
|---|---|---|
| 1 | Canlı embed çağrısı başarılı | Teslim özetinde dönen **boyut sayısı** |
| 2 | Türkçe yakınlık doğru sıralandı | 3 kosinüs değeri teslim özetinde |
| 3 | `odin_ai/rag.py`'de `hashlib` yok | `findstr hashlib` çıktısı boş |
| 4 | Mandal kırılarak doğrulandı | Kırmızı → yeşil ikilisi teslim özetinde |
| 5 | Tam test koşusu yeşil | `pytest tests/ -q` son satırı |

## Kurallar (ALTYAPI-KİT · D-196)

- D-211 ikiz yapı yasağı · D-230 gömülü gövde kopyası yasak · D-224 ölçülmeyen geçti sayılmaz · D-260 beyan ≠ kanıt.
- API anahtarını koda yazma. `.env` üzerinden oku.
- Geçici betik yazma (R1). Ölçümü kalıcı dosyaya koy ya da tek seferlik komutla yap.

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/ajan_chat.py sorun --ajan yasu --task-id ALTYAPI-RAG-EMBEDDER-01 --sorun "<engel>"
python scripts/ajan_chat.py elestiri --ajan yasu --konu "RAG embedder" --bulgu "<tasarım itirazın>"
python scripts/ajan_chat.py oku --son 10
```

Varsayım 1 veya 2 düşerse **zorunlu** sorun aç. Sessizce devam etme.

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id ALTYAPI-RAG-EMBEDDER-01 --ozet "<boyut + kosinüsler + mandal>"
python scripts/gorev_kutusu.py bak --ajan yasu      # posta: yeni gorev var mi?
python scripts/ajan_chat.py oku --son 10            # chat: cevap bekleyen mesaj var mi?
```

Yeni görev varsa al ve başla. Bu döngü sonsuzdur (D-312).

## Ilgili Nodlar

- [[AGENTS]]
- [[hubs/TOOLS_SCRIPTS_HUB]]
- [[prompts/mimir_sistem_promptu]]
