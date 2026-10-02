# VERI-RISK-MOTORU-01 — Brief (utku)

**Başlık:** [VERI] Sekiz risk skoru tablosunu yaz → 0046_risk_skorlari.sql (4s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/schema/migrations/0046_risk_skorlari.sql`
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Fazlar aşağıda `## Faz A/B/C` olarak yazılı.

## Neden

SSOT yol haritasının **Faz 2 — Risk Motoru** adımı, ürünün var oluş sebebi olan 7 müşteri sorusunun
4'üne tek başına cevap veriyor. Bugün tablo bile yok.

| Kanıt | Yer |
|---|---|
| 8 skorun resmî adı ve 0-100 aralığı | `yedekler/Huginn Data Insights (HUGIns).txt:791-822` |
| Müşterinin 7 sorusu | `yedekler/Huginn Data Insights (HUGIns).txt:11-17` |
| Nihai çıktı: Güven Skoru + 4 öneri kademesi | `yedekler/Huginn Data Insights (HUGIns).txt:824-849` |
| Faz 2 = Risk Motoru (sıradaki faz) | `yedekler/Huginn Data Insights (HUGIns).txt:850-873` |

**Skor adları SSOT'tan birebir alınacak — yeni ad uydurma yasak (D-260):**

| # | Skor adı (SSOT verbatim) | Kolon adı | SSOT satırı |
|---|---|---|---|
| 1 | Kurumsallık Skoru | `corporateness_score` | 792 |
| 2 | Güvenilirlik Skoru | `reliability_score` | 796 |
| 3 | İtibar Skoru | `reputation_score` | 800 |
| 4 | Siber Güvenlik Skoru | `cyber_security_score` | 804 |
| 5 | Operasyonel Güç Skoru | `operational_power_score` | 808 |
| 6 | Şeffaflık Skoru | `transparency_score` | 812 |
| 7 | Fraud Risk Skoru | `fraud_risk_score` | 816 |
| 8 | Genel Güven Skoru | `overall_trust_score` | 820 |

4 öneri kademesi (SSOT:824-849): **Çalışılabilir · Dikkatli çalışılmalı · Ek inceleme gerekli · Yüksek riskli**

## Doğrulanacak varsayım

- Son göç `0045_tender_cekilme_tarihi_rename.sql` varsayıldı → yeni göç numarası **0046**. Diskte 0046 varsa **dur**, `ajan_chat.py ac` ile sorun aç.
- `schema_versions.json` göç defteridir ve her yeni göç oraya satır ekler varsayıldı (D-253). Şema farklıysa **dur**.
- Tek puan kapısı `src/company_master/etl/quality_recalc.py` varsayıldı (D-256/1). Başka yazıcı bulursan **dur**, panoya sorun aç — ikinci yol açmak yasak.
- `companies` tablosunda birincil anahtar `id` varsayıldı. Farklıysa **dur**.
- Skor tipi `NUMERIC(5,2)` ve **varsayılan NULL** varsayıldı. `DEFAULT 0` yazmak **yasaktır** (D-249: "veri yok" ≠ "0 puan").

## Faz A — Şema (en riskli, ilk sırada)

1. `0046_risk_skorlari.sql` yaz: `company_risk_scores` tablosu — `company_id` FK + 8 skor kolonu + `recommendation_tier TEXT` + `calculated_at TIMESTAMPTZ` + `score_version TEXT`.
2. Her kolona `COMMENT` ekle: SSOT satır numarası + Türkçe resmî ad (D-259/1 deseni: pasif/aktif ayrımı COMMENT ile yazılır).
3. `recommendation_tier` için `CHECK` kısıtı: yalnız 4 kademenin biri veya NULL.
4. `down/0046_risk_skorlari.sql` geri alma dosyasını yaz (`test_migration_down_files_content` bunu arar).
5. `schema_versions.json`'a satır ekle.

## Faz B — Hesaplayıcı iskeleti

6. `src/company_master/risk/skorlar.py` yaz: her skor için bir fonksiyon, **girdisi yoksa `None` döner** (0 dönmez).
7. Tek yazma kapısı: `risk_recalc()` — tabloya yazan **tek** fonksiyon. Döngü içinde ikinci `UPDATE` yazmak yasak.
8. `overall_trust_score`: diğer 7'nin ağırlıklı ortalaması; **ölçülmemiş skor paydadan düşer**, 0 sayılmaz.
9. `recommendation_tier`: `overall_trust_score` NULL ise tier de NULL.

## Faz C — Mandal (D-256/4: kırılarak doğrulanır)

10. `tests/test_risk_skorlari.py` yaz. En az şu 5 assert:
    - 8 kolonun tamamı göç dosyasında geçiyor (ad kontrolü).
    - `DEFAULT 0` dizgisi göç dosyasında **yok**.
    - girdisi boş firma → skor `None`, tier `None`.
    - 7 skordan 3'ü NULL ise ortalama kalan 4'ten hesaplanıyor (payda düzeltmesi).
    - `recommendation_tier` 4 kademenin dışında bir değerle çağrılırsa hata veriyor.
11. Mandalı **kır**: bir assert'i geçici ters çevir, kırmızı gördüğünü teslim özetine yaz. Yeşili geri al.

## Kabul kriteri

- [ ] `0046_risk_skorlari.sql` + `down/0046_risk_skorlari.sql` diskte, `schema_versions.json` güncel.
- [ ] `python -m pytest tests/test_schema_validation.py tests/test_risk_skorlari.py` yeşil.
- [ ] 8 kolon adı SSOT satır numarasıyla birlikte COMMENT'te yazılı.
- [ ] Hiçbir skor kolonunda `DEFAULT 0` yok (D-249).
- [ ] Tabloya yazan tek fonksiyon `risk_recalc()`; grep ile ikinci yazıcı yok (D-256/2).
- [ ] Mandal kırılarak doğrulandı; kırmızı çıktı teslim özetinde.

## Kurallar (VERI-KİT · D-196)

- **Görev başında** SSOT oku: `yedekler/Huginn Data Insights (HUGIns).txt:780-850`.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir (D-260).
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Hesaplama bu görevde çalıştırılmaz** — canlı DB'ye veri yazmak ayrı görevdir (D-238). Bu iş şema + fonksiyon + mandal ile biter.
- **Teslimden önce** `hubs/VERI_KALITESI_HUB.md` "Kapanan işler" bölümüne `VERI-RISK-MOTORU-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Varsayım tutmazsa **uydurma, durma — yaz**:

```bash
python scripts/ajan_chat.py ac utku VERI-RISK-MOTORU-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-RISK-MOTORU-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id VERI-RISK-MOTORU-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-RISK-MOTORU-01 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312).**

```bash
python scripts/gorev_kutusu.py bak --ajan utku
python scripts/ajan_chat.py oku --son 10
```

- Mesaj varsa → cevapla. Yeni görev varsa → `al` ile al. İkisi de boşsa → `basla --ajan utku`.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]] (D-249, D-253, D-256, D-260)
- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
- [[plans/_brief_sablon]]
