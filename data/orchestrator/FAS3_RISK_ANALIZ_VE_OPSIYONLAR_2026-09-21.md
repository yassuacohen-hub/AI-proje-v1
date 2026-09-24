# FAS 3 Risk Analiz & Opsiyonlar (2026-09-21)

## Hazır Durumda — Backlink Uygulaması

70 hedef dosyaya [[hub]] backlink eklenecek (70 Ekle), 2 dosya zaten var (Atlandı).
DRY-RUN doğrulandı. Uygulamaya hazır: `python data/_tmp/_hub_backlink_uygula.py --uygula`

| Dosya Sayısı | Hub Sayısı | Durum |
|---|---|---|
| 63 | 1 | Tek hub referansi |
| 7 | 2+ | Coklu hub (ortak konular) |
| 2 | var | Zaten backlink |

**Ortak konular (7 dosya):**
- `01_koordinator_ajan` <- ORKESTRASYON + VERI_KALITESI (neden: test danismanlik)
- `05_kalite_ajan` <- ORKESTRASYON + VERI_KALITESI (neden: rol tanimi)
- `06_web_kazima_uzmani` <- OSINT + ORKESTRASYON (neden: web yetkinligi)
- `09_osint_rol_tanimi` <- OSINT + ORKESTRASYON
- `01_kalite_skoru_ek_metrikleri` <- OSINT + VERI_KALITESI (neden: metrik paylas)
- `Orkestrator` <- OSINT + ORKESTRASYON
- `kalite` wiki <- ORKESTRASYON + VERI_KALITESI

Graph'ta cok-yollu baglanti olusturur, hub-arasinda semantik iliskiye isaretcidir.

## Risk 1: Bağ Yönü Tamamlanmış ✓
Hub -> Hedef -> Hub (dairesel).
Graph'ta hub artik biri-merkezli (hub-and-spoke) değil, çifte tarafli net.
Orphan oranı 671->85 %86 azalsa bile, kalan 85'in kaynagi hedeflerin hic wikilink olmamasi.
Backlink bu riski çözmez, ama hub'u searchable/discoverable yapar.

## Risk 2: İkiz Dosya Senkron Dışı ⚠️

`AI proje v1/PROJECT_ROADMAP.md`:
- Canonical değil → `Huginn Data Insights/PROJECT_ROADMAP.md` canonical (updated)
- Hâlâ emoji başlıklı (PO emri = emoji yok)
- Backlink uygulanırsa ikiz'e de ekle?
  - Evet: veri tutarlı ama senkron iş yükü artır (elle)
  - Hayır: canonical tutsak ama ikiz sorunlu

**Benzer durum:** `AI proje v1/V10/wiki/agents/*` vs `Huginn Data Insights/.kilo/worktrees/*/wiki/agents/*`

## Risk 3: Kapsam Eksikliği
Konu hub yok:
- **Müşteri Paneli / Huginn** (kullanici eki, dash, raporlama)
- **Güvenlik / Auth** (OIDC, şifre, KVKK, veri politika)
- **Marka / Brand** (positioning, persona, logo, prompts)

Backlink uygulanırsa bu hub'lar için hedefler orphan kalabilir. İkinci dalga + ölçüm gerekir.

---

## Opsiyonlar

### Seçenek A: Backlink Uygula + Rapor + İkinci Dalga Planı
**Maliyet:** 10 dk (backlink), 15 dk (rapor)
**Fayda:** Acil bağlanma, karar öncesi PO görüşü
**Risk:** Risk 2/3 hala açık; Sprint kapanması uzar (ikinci dalga gerekir)

**Süreç:**
1. `python data/_tmp/_hub_backlink_uygula.py --uygula` (FAS 3 commit)
2. Orphan ölçümü tekrar
3. "FAS 3 Rapor + FAS 4 Opsiyonları" (ikinci dalga hub'ları + ikiz temizliği)
4. PO onay

### Seçenek B: Backlink Uygula + İkiz Canonical Fix + Rapor
**Maliyet:** 10 dk (backlink) + 30 dk (ikiz fix) + 15 dk (rapor)
**Fayda:** Senkron tutarlı, graph temiz, karar satırı net
**Risk:** Zaman basıncı; backlog backlink fail riski (script hata üretirse undo gerekir)

**Süreç:**
1. `AI proje v1/PROJECT_ROADMAP.md` canonical'e migrate (symlink veya delete)
2. `python data/_tmp/_hub_backlink_uygula.py --uygula`
3. Orphan ölçümü tekrar
4. "FAS 3 Rapor"

### Seçenek C (Tavsiye): Backlink Uygula + Risk Kartı (PO Onayı)
**Maliyet:** 10 dk (backlink) + 20 dk (risk kartı)
**Fayda:** PO karar, sprint çerçevesi net, tekrar planlama yok
**Risk:** Minimal (PO tercihine bağlı)

**Süreç:**
1. `python data/_tmp/_hub_backlink_uygula.py --uygula`
2. Orphan ölçümü tekrar
3. "FAS 3 Rapor + Eleştiriler" yazılı form
4. **PO Karar Formu v2** (Risk 2/3 + Opsiyonlar)

---

## Tavsiye

**C seçeneği:** Backlink uygulanır, Risk 2/3 raporlandı, PO'ya ikinci dalga + ikiz temizliği için onay kültü. Bu sprint "pilot geçiş" olarak kapanır, ikinci sprint için kaynak tahsisi (saat) açık.

Gerekçe:
- Backlink = acil işi bitirir (70 dosya kurtarılır)
- Risk 2/3 = açık, rapor edilen, haritalı
- PO karar = sprint sonrası yönü belirler
- Taşma = Risk 2/3 çözmek seperate sprint'lere

---

## Adımlar (C seçeneği)

1. Backlink uygula: `python data/_tmp/_hub_backlink_uygula.py --uygula`
2. Doğrula: `python data/_tmp/_hub_link_dogrula.py`
3. Orphan ölçümü: Obsidian graph backup, elle orphan sayı
4. FAS 3 Rapor yazılır
5. PO Karar Formu (Risk 2/3 opsiyonları)
6. Sprint kapanış yapıldığında PO kararı Adım 5'ye eklenir
