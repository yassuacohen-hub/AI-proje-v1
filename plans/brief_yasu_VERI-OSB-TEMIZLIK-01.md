# VERI-OSB-TEMIZLIK-01 — Brief (yasu)

**Başlık:** [VERI-KİT] OSB firma dosyalarındaki 647 kimliksiz + 44 mükerrer kaydı temizle (1 gün)
**Öncelik:** P0 · **Kit:** `VERI-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `data/osb/`
**Bağımlılık:** `VERI-OSB-Tazelik-01`
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden

`VERI-OSB-Tazelik-01` raporunda (`data/orchestrator/osb_rapor_2026-09-29.md`)
*"Slug tekrarları: 0"* yazıyor. **Bu beyan ölçümle çürütüldü** (D-260: beyan ≠ kanıt).
Kalıcı denetim kapısı `scripts/osb_veri_denetim.py` ilk koşuşunda şunu buldu:

```
TOPLAM kayit     : 8987   ✅ rapordaki sayı doğru
TEKIL company_slug: 8296
MUKERRER         : 44     ❌ raporda "0" yazıyor
KIMLIKSIZ satir  : 647    ❌ raporda hiç geçmiyor
MOJIBAKE ad      : 0      ✅ dosyalar temiz (önceki şüphe konsol kodlamasıydı)
```

Klasör bazlı kimliksiz dağılımı (`scripts/osb_veri_denetim.py` çıktısı):

| Klasör | Kayıt | Kimliksiz |
|---|---|---|
| `ostim` | 8296 | 0 ✅ |
| `baskent` | 481 | **481** (tamamı) |
| `kazan_hab` | 111 | 91 |
| `anadolu` | 48 | 25 |
| `aso` | 16 | 16 (tamamı) |
| `polatli` | 13 | 13 (tamamı) |
| `polatli_ticaret` | 8 | 8 (tamamı) |
| `cubuk` | 7 | 7 (tamamı) |
| `aso2` | 3 | 3 (tamamı) |
| `dokumcu` | 2 | 2 (tamamı) |
| `sereflikochisar` | 1 | 1 (tamamı) |
| `elmadag` | 1 | 0 ✅ |

**Neden Supabase'e yazmadan önce:** D-262'de bir kez yaşandı — `NULL`, `UNIQUE`
kısıtının kör noktasıdır. 647 kimliksiz satır veritabanına girerse "aynı firma iki
kez girmesin" kilidi **sessizce devre dışı kalır**. Ürün Sahibi kararı (2026-10-01):
*"önce temizlesin, zaten temelde temiz veri istiyoruz, neden kirletelim."*

## Doğrulanacak varsayım

Her maddeyi **ölçerek** doğrula, sonucu rapora yaz. Doğrulanmayan varsayımla kod yazma.

1. Kimlik alanı adı `company_slug` (`slug` DEĞİL). 17 alanlı şema:
   `legal_name, adres, phones, emails, website_domain, sektor, tax_number, parsel,
   company_slug, source_name, source_type, social_media, osb_slug, source_file,
   status, is_ankara, is_osb_member`
2. `ostim` klasöründe slug **nasıl üretilmiş?** — `legal_name`'den mi türetilmiş,
   kaynak siteden mi geliyor? Üretim kuralını (küçültme, Türkçe harf eşlemesi,
   ayraç karakteri) **örnekleyerek** çıkar; aynı kuralı diğer 11 klasöre uygula.
3. 44 mükerrer slug **gerçek ikiz mi, yoksa aynı unvanlı ayrı firma mı?**
   `adres` + `tax_number` + `parsel` alanlarını karşılaştır. Ayrı firmaysa
   **silme yasak** — slug'a ayırt edici ek gerekir. D-260: silmeden önce ayırt et.
4. Kimliksiz 647 satırın `legal_name` alanı dolu mu? Boşsa slug üretilemez —
   o satırları ayrı say ve raporda **"kaynak eksik"** olarak işaretle, uydurma.

## Adımlar

1. `python scripts/osb_veri_denetim.py --kontrol 8987` koş, çıktıyı rapora başlangıç
   ölçümü olarak yaz (D-238: kanıt beyan değildir).
2. `ostim` slug üretim kuralını çıkar (varsayım 2). Kuralı tek fonksiyonda yaz —
   kalıcı dosyaya, geçici script **yasak** (R1).
3. Kimliksiz 647 satıra kuralı uygula. `legal_name` boş olanları atla, sayısını not et.
4. 44 mükerreri sınıflandır (varsayım 3): gerçek ikiz → tek kayda indir;
   ayrı firma → slug'a ayırt edici ek (ör. `-2`) ve **gerekçesini rapora yaz**.
5. `python scripts/osb_veri_denetim.py --self` ve `--kontrol <yeni toplam>` koş.
   Toplam 8987'den düştüyse **her düşen kaydın gerekçesi** rapora yazılır.
6. Raporu `data/orchestrator/osb_temizlik_raporu_2026-10-01.md` olarak yaz:
   öncesi/sonrası tablo + mükerrer sınıflandırma + atlanan satırlar.

**Supabase'e yazma bu brifin kapsamı DIŞI.** Ürün Sahibi: *"ondan sonra sen yaz"* —
yazma işi İhsan'a ait. Sen sadece dosyaları temizle ve raporla.

## Kabul kriteri

Tek komutla doğrulanır:

```bash
python scripts/osb_veri_denetim.py --kontrol <yeni_toplam>
```

Çıktıda **hepsi birlikte**:

- `KIMLIKSIZ satir  : 0` (veya `legal_name` boş olan N satır — N rapora yazılı)
- `MUKERRER         : 0`
- `MOJIBAKE ad      : 0`
- `TEKIL company_slug` = `TOPLAM kayit` − (gerekçeli atlanan satır)
- `python scripts/osb_veri_denetim.py --self` → `self-check OK` (exit 0)
- Rapor dosyası var: `data/orchestrator/osb_temizlik_raporu_2026-10-01.md`

## Kurallar (VERI-KİT · D-196)

- **R1 — geçici script yasak.** Temizlik mantığı kalıcı dosyada yaşar.
- **D-260 — beyan ≠ kanıt.** "Slug tekrarı 0" demek yetmez; komut çıktısı yapıştır.
- **D-262 — silmeden önce referans taşı.** Kayıt silinecekse neyin kaybolduğu yazılı.
- **D-86 — Windows cmd.exe:** `head` yok → `findstr`. Çok satırlı `python -c`
  sessizce boş çıktı verir → betik yaz. Türkçe karakterli çıktı için
  `set PYTHONIOENCODING=utf-8 && python ...`
- **D-236 — tüketicisi olmayan çıktı üretilmez.** Ürettiğin her alanı kim okuyacak?

## Ajan chat zorunlu (D-210 · D-217)

```bash
# Başlarken (koordinasyon):
python scripts/chat_gonder.py --kimden yasu --to ihsan --type koordinasyon \
  --task-id VERI-OSB-TEMIZLIK-01 --mesaj "Basladim. Olculen ilk durum: ..."

# Varsayım çürüdüyse (ZORUNLU — tahminle devam etme):
python scripts/chat_gonder.py --kimden yasu --to ihsan --type soru \
  --task-id VERI-OSB-TEMIZLIK-01 --mesaj "Varsayim N yanlis cikti: ..."

# Bitirirken (rapor):
python scripts/chat_gonder.py --kimden yasu --to ihsan --type rapor \
  --task-id VERI-OSB-TEMIZLIK-01 --mesaj "Oncesi/sonrasi: ..."
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id VERI-OSB-TEMIZLIK-01 \
  --ozet "647 kimliksiz + 44 mukerrer temizlendi, rapor: data/orchestrator/osb_temizlik_raporu_2026-10-01.md"
python scripts/gorev_kutusu.py bak --ajan yasu      # posta: yeni gorev var mi?
python scripts/ajan_chat.py oku --son 10            # chat: cevap bekleyen mesaj var mi?
```

**D-312 — teslim ≠ bitiş.** Teslimden sonra posta ve chat kontrolü ZORUNLU.
Yeni görev varsa al ve başla; chat'te sana sorulan varsa cevapla. Bu döngü
insan müdahalesi olmadan sonsuza kadar tekrarlanır.

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/data/orchestrator/osb_rapor_2026-09-29]]
