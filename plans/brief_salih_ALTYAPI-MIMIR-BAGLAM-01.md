# ALTYAPI-MIMIR-BAGLAM-01 — Brief (salih)

**Başlık:** [ALTYAPI] Mimir sohbet ucu: BAGLAM üret + qwen3.8-flash-next bağla (3 saat)
**Öncelik:** P1 · **Kit:** `ALTYAPI-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/odin_ai/mimir_servis.py`
**Bağımlılık:** `VERI-RAG-KORPUS-01`
**Hub:** `hubs/TOOLS_SCRIPTS_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden

Üç parça ayrı ayrı var, birbirine bağlı değil: (1) sistem promptu `prompts/mimir_sistem_promptu.md` dosyasında duruyor, (2) vektör arama `vector/service.py` içinde, (3) sohbet modeli `qwen3.8-flash-next` EVREN'de canlı ölçüldü (1.5s, 294 karakter Türkçe yanıt). Hiçbir şey bu üçünü birleştirmiyor — yani Mimir **hiç cevap vermiyor**.

Bu iş fine-tune **değil**. EVREN'de metin modeli eğitimi fiziken yok (iki bağımsız yoldan doğrulandı: 10/10 API ucu 404 + panelde "Metin" kilitli). Yaptığımız şey: soruyu al → ilgili firma parçalarını vektörden bul → `<BAGLAM>` bloğuna koy → sistem promptu + bağlam + soru olarak modele gönder.

**Kritik kısıt (D-230):** Sistem promptunu koda **kopyalamayacaksın**. `prompts/mimir_sistem_promptu.md` dosyasından okuyacaksın. Kopyalarsan prompt iki yerde yaşar, biri güncellenir öteki bayatlar — D-211/D-230 ihlali.

**Kritik kısıt (D-311):** İki ayrı prompt var — MİMİR-DIŞ (müşteri) ve MİMİR-İÇ (admin). Hangisinin yükleneceği **rol parametresiyle** seçilir. Varsayılan **DIŞ** olacak; yani yanlışlıkla parametre geçilmezse kısıtlı olan yüklenir, açık olan değil.

## Doğrulanacak varsayım

| # | Varsayım | Nasıl ölçülür | Yanlışsa |
|---|---|---|---|
| 1 | Prompt dosyası iki bölüme güvenilir şekilde ayrılabilir | Dosyayı oku, DIŞ/İÇ bölümlerini ayır, ikisinin de karakter sayısını yazdır (>500) | Ayırıcı belirsizse chat'e sorun aç; prompt dosyasına başlık mandalı koy |
| 2 | `qwen3.8-flash-next` uzun bağlamla Türkçe cevap veriyor | ~3.000 karakter `<BAGLAM>` + 1 soru gönder; süre + yanıt uzunluğu + `finish_reason` yazdır | Boş dönerse `mimo-v2.6-pro` yedeğini ölç (5.8s, çalıştığı doğrulanmış) |
| 3 | Bağlamda olmayan soruya model "veri tabanımızda yok" diyor | Korpusta kesin olmayan bir şey sor (örn. "X firmasının cirosu") | Uyduruyorsa prompt kuralı yetersiz; chat'e eleştiri aç, prompt sıkılaştırılacak |

**`finish_reason` yazdır (borç #38).** 3 model daha önce boş döndü, sebebi hâlâ ölçülmedi. Bu turda sebebi öğreniyoruz.

## Adımlar

1. **Ölç önce:** 2. ve 3. varsayımı tek seferlik gerçek çağrıyla ölç. Boş dönerse DUR, yedek modeli ölç, chat'e yaz.
2. `prompts/mimir_sistem_promptu.md` okuyucusu: `prompt_yukle(rol: str = "dis") -> str`. Rol `"dis"`/`"ic"`. Tanımsız rol → `ValueError` (sessiz varsayılan **yok**).
3. `<BAGLAM>` üreticisi: soruyu embed et → `vector/service.py` ile en yakın N chunk → her chunk kaynak künyesiyle (`firma_id · kaynak · tarih`) bloğa yaz. N'yi sabit gömme, `os.environ.get` + varsayılan.
4. Bağlam boşsa modeli **çağırma**. Doğrudan "Bu bilgi veri tabanımızda yok." dön. Boş bağlamla çağrı = token yakmak + halüsinasyon davetiyesi.
5. Sohbet çağrısı: `thinking` tuzağına dikkat — `(msg.get("content") or msg.get("reasoning_content") or "").strip()` deseni (borç #37).
6. Mandal: `tests/test_mimir_baglam.py` — (a) tanımsız rol `ValueError`, (b) varsayılan rolün **DIŞ** olduğu, (c) boş bağlamda model **çağrılmadığı** (sahte çağrı sayacı 0), (d) promptun dosyadan okunduğu (kaynak kodda prompt metni geçmiyor). Kırarak doğrula (D-256/4).
7. `python -m pytest tests/ -q` tam koşu.

## Kabul kriteri

| # | Şart | Kanıt |
|---|---|---|
| 1 | Uzun bağlamla canlı Türkçe yanıt alındı | Süre + karakter + `finish_reason` teslim özetinde |
| 2 | Bağlamda olmayan soruya "yok" dedi | Model yanıtının birebir metni |
| 3 | Boş bağlamda model çağrılmıyor | Mandal yeşil |
| 4 | Varsayılan rol DIŞ | Mandal yeşil |
| 5 | Prompt metni kodda yok | `findstr` çıktısı boş |
| 6 | Mandal kırılarak doğrulandı | Kırmızı → yeşil ikilisi |
| 7 | `pytest tests/ -q` yeşil | Son satır |

## Kurallar (ALTYAPI-KİT · D-196)

- D-230 gömülü gövde kopyası yasak · D-311 iç/müşteri ayrımı · D-224 ölçülmeyen geçti sayılmaz · D-247 kişisel veri tek kapıdan.
- `TEST-ODIN-PROMPT-INJECTION` senaryoları bu uca bağlanacak — `scripts/odin_prompt_injection_test.py --api-url` ile SKIP'ten çıkacak. Ucun adresini teslim özetine yaz.
- API anahtarını koda yazma. Geçici betik yazma (R1).

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/ajan_chat.py sorun --ajan salih --task-id ALTYAPI-MIMIR-BAGLAM-01 --sorun "<engel>"
python scripts/ajan_chat.py elestiri --ajan salih --konu "Mimir baglam" --bulgu "<tasarım itirazın>"
python scripts/ajan_chat.py oku --son 10
```

Model boş yanıt verirse veya uydurursa **zorunlu** sorun aç.

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan salih --task-id ALTYAPI-MIMIR-BAGLAM-01 --ozet "<sure + finish_reason + 'yok' yaniti + uc adresi>"
python scripts/gorev_kutusu.py bak --ajan salih      # posta: yeni gorev var mi?
python scripts/ajan_chat.py oku --son 10             # chat: cevap bekleyen mesaj var mi?
```

Yeni görev varsa al ve başla. Bu döngü sonsuzdur (D-312).

## Ilgili Nodlar

- [[AGENTS]]
- [[hubs/TOOLS_SCRIPTS_HUB]]
- [[prompts/mimir_sistem_promptu]]
- [[plans/brief_utku_VERI-RAG-KORPUS-01]]
