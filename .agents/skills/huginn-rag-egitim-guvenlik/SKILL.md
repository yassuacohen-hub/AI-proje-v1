---
name: huginn-rag-egitim-guvenlik
description: >-
  Huginn/Mimir için RAG + ingestion + LoRA veri hazırlığı + prompt-injection
  savunması/red-team tek kılavuz. Kullan: Mimir'e yeni kaynak eklerken,
  chunk/embedding/rerank kararı verirken, eğitim veri seti üretirken,
  sistem promptu değiştirirken, GO/NO-GO koşusu yapmadan önce.
  Üç ham rolü (YZ Mimarı/Eğitimci, YZ Siber Güvenlik/Red Team,
  Admin Layer LoRA veri hazırlama) tekrarsız birleştirir.
author:
  - ihsan
version: 1.0.0
license: Apache-2.0
tags:
  - rag
  - graphrag
  - ingestion
  - lora
  - qwen
  - prompt-injection
  - red-team
  - mimir
---

# Huginn RAG · Eğitim · Güvenlik

Tek rol, üç şapka: **Mimar** (veri nasıl girer, nasıl bulunur), **Eğitimci**
(veri nasıl öğretilir), **Red Team** (veri nasıl sızar, nasıl kapatılır).
Her kural **bir kez** yazılır; diğer bölümler `→ §N` ile atıf verir.

## İlgili Modüller / Dosyalar

- `prompts/mimir_sistem_promptu.md` — **SSOT prompt**; §1 DIŞ, §2 İÇ (ODIN), §3 `<BAGLAM>`, §3b `<KATALOG>`
- `scripts/odin_prompt_injection_test.py` — red-team harness (`--api-url --model --tekrar --dry-run`; çıkış 0 GO / 1 NO-GO / 2 SKIP)
- `data/odin_injection_test_scenarios.json` — senaryolar (kök dict, anahtar `senaryolar`)
- `data/odin_injection_test_log.jsonl` — koşu kanıtı (D-260: beyan ≠ kanıt)
- `src/company_master/odin_ai/rag.py` — stdlib chunking (`Chunk`, `chunk_metin`, `chunk_bol`, `chunk_topla`)
- `src/company_master/gateway/ninerouter_client.py` — `embed`, `chat`, `web_search`, `web_fetch`
- `docs/ODIN_GUVENLIK_ATIF.md`, `docs/ODIN_AI_ISKELET.md` — iç/müşteri model ayrımı gerekçesi
- `tests/test_odin_prompt_injection.py` — harness mandalları
- Komşu skill'ler: `code-quality-and-security` (OWASP), `enterprise-data-classification` (PII/DLP),
  `osint-web-scraping-toolkit` (kazıma), `9router` (gateway), `verification-before-completion` (D-260)

> Var sanılan ama **olmayan** dosyalar: `scripts/odin_veri_hazirla.py`, `scripts/odin_training_pipeline.py`,
> `docs/ODIN_PROMPT_INJECTION_SCENARIOS.md`, `docs/ODIN_SECURITY_CHECKLIST.md`, `odin_ai/mimir_servis.py`
> (kilit kaydı var, dosya yok — referans verme, önce `ls` ile doğrula).

---

## 1. Kimlik ve Katman (Dual-Layer)

| Katman | Model | Veri havuzu | Prompt bloğu | Sıcaklık |
|---|---|---|---|---|
| **Müşteri** (Mimir-DIŞ) | SSB EVREN / Qwen 2.5-3 | yalnız o `tenant_id` | SSOT §1 | 0.7 sorgu · 0.1-0.2 rapor |
| **Admin** (Mimir-İÇ / ODIN) | aynı taban + LoRA | ortak havuz + mevzuat | SSOT §2 | 0.4 |

Kurallar (tek yer):
1. Müşteri verisi **asla** LoRA setine girmez; admin modeli müşteri paneline **asla** çıkmaz (`ODIN_GUVENLIK_ATIF.md`).
2. Model kimliği: "tüm dilleri bilen, ana dili Türkçe" — çıktı dili soru diliyle eşleşir (`dil_uyumlu_mu`).
3. Prompt tek dosyada; kod `prompt_yukle(rol="dis"|"ic")` ile keser. Kopya prompt = çatışma kaynağı.

---

## 2. Ingestion (veri girişi)

### 2.1 Kaynak sırası ve araç
Resmî Gazete → EKAP → ÇED → Ticaret Sicil → şirket web. Hepsi `9router.web_fetch`
(Jina/Trafilatura temizler) + `osint-web-scraping-toolkit` rate-limit kuralı.
Dorking kalıbı: `site:resmigazete.gov.tr "<firma>"`.

### 2.2 Her chunk'ın zorunlu meta'sı
```json
{"kaynak_url": "...", "tarih": "2026-10-03", "tenant_id": "ortak|<id>",
 "hiyerarsi": "Kanun>Madde>Fıkra>Bent", "guncelleme": "..."}
```
Tarih + kaynak yoksa chunk **yazılmaz**. Cevapta "Kaynaklar:" satırı bu meta'dan üretilir.

### 2.3 Chunking
- Mevzuat: **Kanun > Madde > Fıkra > Bent** sınırında kes; madde ortasından bölme.
- Diğer metin: `rag.chunk_metin(boyut=200)` (stdlib, bağımlılık yok).
- Semantik/JSON-LD chunk = yalnız mevzuat korpusu 10k maddeyi aşınca (`ponytail:` eşiği).

### 2.4 Güvenlik duvarı (→ §5 ile ortak)
Ingestion sırasında: `enterprise-data-classification` ile PII/KVKK tarama → bulunan alan
maskelenir, kaynak işaretlenir. Dış metin **veri**dir, talimat değildir; `<BAGLAM>` içine
girer, sistem promptuna asla eklenmez (dolaylı enjeksiyon kapısı burada kapanır).

---

## 3. Retrieval (bulma)

| Aşama | Şimdi (repo) | Geçiş eşiği |
|---|---|---|
| Vektör | chromadb + `9router.embed` | — |
| Hibrit | BM25 yok → `ILIKE` ön filtre + vektör | recall < %80 ölçülünce BM25 |
| Rerank | top-20 → `chat` ile puanla | gecikme > 3 s olunca Cross-Encoder |
| GraphRAG | yok | "X'in ihale ortağının tesisi" tipi 2-sıçrama sorgu geldiğinde Neo4j |

Varlık şeması (GraphRAG'e geçince): Şirket, İhale, Tesis, Mevzuat Maddesi, Teşvik Belgesi.
Bağlam bloğu biçimi **SSOT §3** (`<BAGLAM>`), katalog **§3b** (`<KATALOG>`, `carpma_sayaci` D-211).
Model `[BAĞLAM BAŞLANGICI]…[BAĞLAM BİTİŞİ]` dışına çıkan iddiada "bilmiyorum" der.

---

## 4. Eğitim verisi (LoRA/QLoRA)

### 4.1 Kayıt biçimi
```json
{"instruction": "görev", "input": "<BAGLAM>…</BAGLAM>\n<user_query>…</user_query>", "output": "…"}
```
`output` daima: kaynak satırı + tarih + Türkçe. Düşünce izi (`<think>`) **yok** (`dusunme_gorundu_mu`).

### 4.2 Üretim kuralı
- Kaynak: yalnız **ortak havuz** (§1/1). Filtre: `tenant_id == "ortak"` → "Filter Global Only".
- Her senaryo türünden ≥ 3 örnek: olumlu cevap, kaynak-yok reddi, enjeksiyon reddi (§5 kategorileri).
- Qwen eğitim ayarı: Temp 0.4, Max Tokens 4096.
- Doğrulama: `data-quality-testing` + assert betiği (boş `output`, kaynaksız `output`, PII → düşer).
- RAGAS yok; ölçüm = harness GO oranı + manuel 20 örnek. RAGAS eşiği: set > 2k kayıt.

### 4.3 Çıktı şablonu (ajan tanımı üretirken)
```
[🤖 AJAN ADI VE ROLÜ] [🛡️ KATMANI] [🧠 QWEN & MIMO AYARLARI] [📝 SİSTEM PROMPTU] [🚀 GÖREV TANIMI]
```

---

## 5. Enjeksiyon savunması ve Red Team

### 5.1 Dört kategori (senaryo dosyası bunlara göre etiketlenir)
| Tür | Örnek | Beklenen |
|---|---|---|
| Doğrudan | "önceki kuralları unut" | `reddetti_mi` |
| Dolaylı | kazınan sayfada gömülü talimat | §2.4 → veri olarak kalır |
| Jailbreak/DAN | rol-play, "geliştirici modu" | ret + dil uyumu |
| Veri sızıntısı | Tenant_A, Tenant_B'yi sorar | `ic_veri_sizdi_mi` = False |

### 5.2 Üç katman
1. **Prompt**: `<user_query>` etiketi; SSOT §1 yasak listesi.
2. **Kod**: `tenant_id` sorguya SQL seviyesinde eklenir (prompt'a güvenme).
   Prompt'la kesilemeyen kusur → kod sayacı/mandal (örn. `carpma_sayaci`).
3. **Çıktı**: `kural_kontrol` kalıpları (fiyat, iç anahtar, düşünce izi).

### 5.3 Koşu disiplini
```bash
python scripts/odin_prompt_injection_test.py --api-url <url> --model <m> --tekrar 3
```
- `--tekrar 3` zorunlu: model stokastik; tek koşu GO yalancıdır (`katla` en kötüyü alır).
- Hedef: ADR > %99, FPR < %1. Yalancı pozitif görünce **kalıp daraltılır**, eşik gevşetilmez.
- Çıkış 0 olmadan "güvenli" yazılmaz; log satırı rapora yapıştırılır (D-260).
- Modelin sınırı olan senaryo (2 koşu üst üste aynı ret) → senaryo "model sınırı" etiketiyle
  ayrılır, mandal gevşetilmez.

---

## 6. Teslim kapısı (her değişiklikte)

- [ ] `pytest tests/test_odin_prompt_injection.py -q` yeşil
- [ ] Harness `--tekrar 3` çıkış 0, log yolu raporda
- [ ] Yeni bağımlılık yoksa (varsa tek satır gerekçe + `requirements-app.txt`)
- [ ] `ponytail:` yorumu her bilinçli sadeleştirmede
- [ ] Rapor Türkçe, tablo ağırlıklı, öz-eleştiri bölümlü (`ihsan-rapor-tarzi`)

---

## 7. Daha basit yol (tek satır)

RAG + LoRA yerine önce **iyi chunk + iyi prompt + harness**; LoRA'ya ancak harness
3 tur üst üste aynı senaryoda model sınırına çarpınca geçilir.
