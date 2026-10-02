# VERI-TOBB2B-BUYUTME-01 — Brief (yasu)

**Başlık:** [VERI] TOBB2B pilotunu büyüt → daha geniş Id taraması (tobb2b.org.tr, ücretsiz)
**Öncelik:** P2 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `data/pilots/VERI-TOBB2B-BUYUTME-01/teklifler.json`
**Bağımlılık:** VERI-TOBB2B-KESISIM-01 (tamamlandı — pilot temeli)
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14)

> **Tek brif kuralı (D-217):** Bir görev = bir brif.

> **Görev:** `VERI-TOBB2B-BUYUTME-01` · **Sahip:** yasu
> **Atayan:** KAHİN (ihsan) · **Kararlar:** D-307 (pilot), **D-319 (bu büyütme — tobb2b.org.tr ücretsiz onayı)**

## Neden

KAHİN onayı: *"K4 + tobb2b.org.tr (ücretsiz) ile başla, F5 ve pilot büyütme görevlerini aç."*

`VERI-TOBB2B-KESISIM-01` pilotu (tamamlandı) 50 `Id` denedi, 20'si doluydu (%40), 11/20
teklif kendi OSB verimizle eşleşti → 1.575 firma. Bu görev **aynı yöntemi** daha geniş bir
`Id` aralığında tekrarlar — ücretsiz/plain-`http://` erişim onaylandığı için ölçek büyütülebilir.

| Kanıt | Yer |
|---|---|
| Pilot ölçümü (20/50 Id dolu, 11/20 eşleşti, 1.575 firma) | `data/pilots/VERI-TOBB2B-KESISIM-01/ozet.json` |
| Pilot brifi (yöntem, risk R1-R7) | `plans/brief_yasu_VERI-TOBB2B-KESISIM-01.md` |
| tobb2b.org.tr erişim onayı (`http://`, `teklif_goster.php?Id=N`) | aynı brif, Neden bölümü |

## Doğrulanacak varsayım

- Pilotun 50 Id aralığı varsayıldı (bilinmiyor hangi aralık taranmıştı — `data/pilots/VERI-TOBB2B-KESISIM-01/teklifler.json`'dan kontrol et). Yeni taramada **farklı/daha geniş** bir Id aralığı kullan, aynı Id'leri tekrar çekme.
- %40 doluluk oranının büyük ölçekte de geçerli olacağı varsayıldı. Doğrulanmamışsa ölçümle kontrol et, sapma varsa chat'e yaz.
- R1 riski (toplu tarama izni yok) pilotta "20 teklif ile sınırlı" önlemiyle kapatılmıştı. Bu görevde ölçek büyüse de **agresif/otomatik toplu tarama yapılmaz** — istek arası bekleme (rate limit) uygulanır, aksi "dur" sebebidir.
- Tek yazma hedefi: `data/pilots/VERI-TOBB2B-BUYUTME-01/teklifler.json` (pilotunkini **ezme**, ayrı dosya).

## Adımlar

### Faz A — Toplama
1. Pilotta denenmemiş yeni bir Id aralığı seç (örn. pilotun üst sınırından devam), rate-limit'li şekilde çek.
2. Alanları ayrıştır: no, tarih, ülke, NACE/sektör metni, açıklama, `ortak_arayan` işareti (pilotla aynı yöntem).
3. Doluluk oranını ölç, pilotun %40'ı ile karşılaştır, sapma varsa not et.

### Faz B — Eşleştirme
4. NACE **bölüm kodu** ile kendi OSB sektörlerimize bağla (pilotla aynı yöntem — `scripts/veri_tobb2b_kesisim.py` referans alınır).
5. Eşleşen teklif/firma sayısını ölç, pilotun 11/20 / 1.575 firma rakamıyla kıyasla.

### Faz C — Rapor
6. Bulguyu raporla, review'a teslim et.
7. Ölçek kararı gereken noktaları (daha da büyütülsün mü, ticari kullanım) ihsan'a yaz.

## Kabul kriteri

- [ ] Pilotta denenmeyen en az 100 yeni Id denendi.
- [ ] Doluluk oranı ölçüldü, pilotun %40'ıyla karşılaştırıldı.
- [ ] NACE bölüm kodu eşleştirmesi yapıldı, eşleşen firma sayısı ölçüldü.
- [ ] Rate-limit uygulandığı kanıtlandı (istek arası bekleme kodda görünür).
- [ ] Sonuç `data/pilots/VERI-TOBB2B-BUYUTME-01/ozet.json`'a yazıldı (pilotunkiyle aynı şema).
- [ ] Rapor + review teslim.

## Kurallar (VERI-KİT · D-196)

- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir (D-260).
- **Teslimden önce** `hubs/OSINT_VERI_TOPLAMA_HUB.md` "Kapanan işler" bölümüne yaz (B-14).
- **D-306 bildirme kuralı:** ölçüm/bulgu/karar → chat'e.
- Agresif/otomatik toplu tarama yasak — rate-limit zorunlu (R1 önlemi büyütülmüş ölçekte de geçerli).
- tobb2b.org.tr dışında yeni kaynak açma (sanayi.org.tr/lonca.gov.tr tarama denemeleri pilotta ölçüldü ve reddedildi — tekrar deneme).

## ⚠️ Riskler (pilottan taşınan + yeni)

| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | Toplu tarama izni yok | Yasal risk | Rate-limit + makul üst sınır (örn. 500 Id) |
| R2 | TOBB2B üye içeriği | Sözleşme riski | Ticari kullanım kararı KAHİN |
| R3 | NACE eşleştirme kaba | Yanlış eşleşme | Bölüm kodu kullan, pilotla aynı doğrulama |
| R8 | Ölçek büyüyünce IP engeli | Veri toplama durur | İlk 50-100 denemede engel kontrolü, engellenirse **dur**, chat'e yaz |

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/ajan_chat.py ac yasu VERI-TOBB2B-BUYUTME-01 "<bulgu>" --cozum "<öneri>"
python scripts/chat_gonder.py --to ihsan --type koordinasyon --task-id VERI-TOBB2B-BUYUTME-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id VERI-TOBB2B-BUYUTME-01 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312).**

```bash
python scripts/gorev_kutusu.py bak --ajan yasu
python scripts/ajan_chat.py oku --son 10
```

- Mesaj varsa → cevapla. Yeni görev varsa → `al` ile al. İkisi de boşsa → `basla --ajan yasu`.

## Önce oku

- `scripts/veri_tobb2b_kesisim.py` → pilot analiz yöntemi
- `data/pilots/VERI-TOBB2B-KESISIM-01/ozet.json` → pilot ölçüm sonucu
- `data/pilots/VERI-TOBB2B-KESISIM-01/lonca_nace_kodlari.json` → 254 NACE kodu referansı
- `plans/brief_yasu_VERI-TOBB2B-KESISIM-01.md` → tam pilot brifi

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]] (D-306, D-307, D-319)
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/plans/brief_yasu_VERI-TOBB2B-KESISIM-01]]
- [[plans/_brief_sablon]]
