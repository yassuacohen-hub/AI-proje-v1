# VERI-OSTIM-TAM-TARAMA-01 — Brief (yasu)

**Başlık:** [VERI] OSTIM detay taraması + tam veri denetimi (2-3 gün)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `data/ostim/kaynak_kilidi.json` (SHA-256 kilidi)
**Bağımlılık:** yok
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Toplu iş birden çok brife bölünmez;
> tek brifte `## Faz A/B/C...` başlıklarıyla anlatılır. Faz başına ayrı dosya açmak yasak.

> **Görev:** `VERI-OSTIM-TAM-TARAMA-01` · **Sahip:** yasu
> **Atayan:** KAHİN (ihsan) · **Öncelik:** P1 · **Tarih:** 2026-09-29
> **Kararlar:** D-283, D-285, D-286, D-289, D-290, D-300

## Neden
`docs/BORC_DEFTERI.md` → **D-283** (politika P-1..P-10), **D-285** (kalite ölçümü),
**D-286** (kazıyıcı düzeltmeleri), **D-290** (bu görev).

KAHİN talebi (2026-09-29):

> "eski database tekrar kirli ve hatalı olmasını istemiyorum, her türlü
> önlemi al, önce tara sonra ölçelim, tamamını, yanlış mükerrer kayıt
> olmasın, şirket verileri kontrol ederek görevi at, raporu buna göre
> oluştur."

Üç ayrı şey talep ediliyor: (a) **önlem**, (b) **önce tara**, (c) **rapor**.

## Doğrulanacak varsayım
> Zorunlu bölüm (D-66 brif sözleşmesi). Brief yazarken **sabitlenen** her tablo adı, kolon adı, fonksiyon imzası,
> satır numarası ve eşik değeri buraya bir madde olarak geçer. Jenerik metin yasak — her brief
> kendi gerçek varsayımlarını taşır.

| Varsayım | Nasıl doğrulanır |
|---|---|
| Tarama kaynak dosyalara dokunmaz | `sha256sum` öncesi/sonrası aynı |
| `companies` tablosu bozulmaz | 8.313 → 8.313 |
| Mükerrer kayıt oluşmaz | `tekil_slug == kayit` |
| Politika gerçekten uygulanıyor | 2 kayıt arası süre ≥ 2 sn |
| 3.339 eksik kayıt gerçekten eksik | liste ∩ detaylı kümesi |
| `GEcIKME=2.0` sn (P-3) | `ostim_detay_tamamla.py` içinde sabit |
| `TEKIL_ESIK=0.95` (P-6) | aynı dosya |
| KAZANIM klasörü izole | `data/ostim/tamamlama_2026-09-29/` dışına yazma yok |
| Telefon 10 veya 11 hane (D-300) | 12+ hane = bitişik birleşmiş sayılır |
| E-posta `user@domain.tld` biçiminde | K-2 sızıntı denetimi |

## Adımlar
> Tek fazlı işte düz numaralı liste. **Toplu işte** bunun yerine `## Faz A — <ad>`,
> `## Faz B — <ad>` başlıkları kullan; her fazda kök neden + etkilenen dosya + o fazın
> doğrulama komutu yazılı olsun. Fazlar sırayla yapılır, en riskli faz ilk sırada.

1. **Önlem (D-290 zaten kuruldu — doğrula)**
   - Çıktı izole klasörde: `data/ostim/tamamlama_2026-09-29/`
   - Kaynak dosyalar SHA-256 kilitli; değişmişse tur **durdurulur**
   - Kazıyıcı SQLite'a dokunmaz (ölçüldü: 0 referans)
   - **Doğrulama:** `python scripts/ostim_veri_koruma.py`
2. **Önce tara** — 3.339 eksik detay, 2 sn aralıkla.
   Günlük üst sınır **500 detay/gün** (dilekçe taahhüdü).
3. **Sonra ölç** — `scripts/birlestirme_kalite_kontrol.py` + mükerrer
   denetimi: aynı `slug` ve aynı normalize unvan sayısı.
4. **Şirket verisi kontrolü** — `companies` tablosu hâlâ 8.313 temiz
   kayıt. Tarama sonrası **aynı sayı** olmalı; değiştiyse raporla.
5. **Rapor yaz** — `data/ostim/tamamlama_2026-09-29/rapor.md`

## Önce oku (asıl bilgi kaynağı kodu)

- `docs/BORC_DEFTERI.md` → **D-283** (politika P-1..P-10), **D-285**
  (kalite ölçümü), **D-286** (kazıyıcı düzeltmeleri), **D-290** (bu görev)
- `docs/VERI_KAYNAK_KURALLARI.md` → K-1 (sessiz tekrar yasak),
  K-2 (kolonlar karışmaz), K-3 (atomik yazım)
- `scripts/ostim_detay_tamamla.py` → docstring'deki P-1..P-10 listesi

## §Tuzaklar (en pahalı bilgi)

1. **`"w"` ile yazmak yığı siler.** 3.339 kayıt `--limit 500` ile
   parçalanırsa, her parça öncekini **kaybeder**. D-289'da düzeltildi
   ama test ederken bunu bil.
2. **`time.sleep` beyaz satırdı.** Politika "2 sn" diyordu, kod
   hiç beklemiyordu. Geri **alınmadığına** emin ol.
3. **Regex doğru olsa bile sahte hesap üretir.** `/accounts/login/`
   → `{"instagram": "accounts"}`. `_gercek_hesap_mi()` var.
4. **Tahminle filtre yazma.** D-285'te telefon listesi uydurulmuştu;
   ölçüm 5 tekrar dedi ve liste **boş bırakıldı**. Ölç, sonra yaz.
5. **Güçlü konsol çıktısı UTF-8 bozuk görünür.** `├╝` gibi karakterler
   PowerShell kaynaklı; **dosyada Türkçe karakterler doğru**. Panik
   etme, `unicode_escape` ile doğrula.
6. **K-2 kaçışı "0" çıkmak kolay, "temiz" demek değil.** Satır
   denetimi gerekir: 5/5 geçen pilot bile `accounts` sahtesi taşıdı.

## §Sabitler

| Sabit | Değer | Nerede |
|---|---|---|
| DIZIN | `https://ostim.org.tr` | `ostim_detay_tamamla.py` |
| GECIKME | `2.0` sn (P-3) | aynı |
| TEKIL_ESIK | `0.95` (P-6) | aynı |
| UA | gerçek Chrome UA, değiştirme (P-1) | aynı |
| KAZANIM | `data/ostim/tamamlama_2026-09-29/` | D-290 izole çıktı |
| KILIT | `data/ostim/kaynak_kilidi.json` | D-290 koruma kilidi |

## Kabul kriteri
- [x] Doğrulanabilir, ölçülebilir çıktı: `data/ostim/OSTIM_TEMIZ.jsonl` = 8.296 kayıt, tekil slug = kayıt.
- [x] Kaynak dosya SHA-256'ları değişmedi (`scripts/ostim_veri_koruma.py`).
- [x] `companies` tablosu 8.313 → 8.313 (dokunulmadı).
- [x] Kalan kirlilik 0: rakamlı sektör 0 / kirli sosyal 0 / altyapı web 0.
- [x] Telefon %100 geçerli (yalnız 10-11 hane) — D-300.
- [x] Adres alanında sayfa bloğu kalmadı — D-300.
- [ ] `companies`'a yazım: **KAHİN kararı bekliyor** (yazılmadı).
- [ ] Yazılı izin: **KAHİN kararı — "izin en son plan"** (ERTELENDİ).

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `<TASK_ID>` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**, brifi yeniden okuyup beklemek değil:

- Brifteki bir varsayım kodda tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- Bir faz tıkandıysa → sorun aç, **sonraki faza geç**, zinciri durdurma.
- @mention aldıysan → P0 5-10 dk, P1 10-15 dk, P2 15-30 dk içinde cevap **zorunlu**.

```bash
python scripts/ajan_chat.py ac yasu VERI-OSTIM-TAM-TARAMA-01 "<sorun>" --cozum "<öneri>"
python scripts/ajan_chat.py oku --task-id VERI-OSTIM-TAM-TARAMA-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id VERI-OSTIM-TAM-TARAMA-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id VERI-OSTIM-TAM-TARAMA-01 --ozet "<özet>"
```

## Ilgili Nodlar
> **Zorunlu (D-218).** Obsidyen proje hafızasıdır. Linksiz doküman grafikten kopuk kalır ve
> ajan onu bulmak için tüm repoyu tarar — token ve süre maliyeti. **En az 2 wikilink.**
> Göreve dokunan her yeni/değişen dokümanı da buraya bağla, ayrıca o dokümanın kendi
> `## Ilgili Nodlar` bölümünden bu brife geri link ver (çift yön).

- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/docs/BORC_DEFTERI]]
