# KAHİN Kararları Açıklama — D-65, MIMIR, GRAPH (Sebep-Sonuç)

---

## 1. D-65 "İş Durmaz" — Kural Mekanizması Açık

### Soru: "İş durmaz demekten kastın nedir? Kural değişebilir mi?"

**Cevap kısa:** Görev blokajda hareketsiz kaldığında, orkestratör işi beklemiyor. KAHİN elle başlatırken, geliştirici paralelde çözer. İş durmaz, çift hat.

### Açıklama Pratik Örnek İle

| Senaryo | Şu anki davranış | D-65 kural | Fark |
|---------|------------------|-----------|------|
| COP-26 (9.7 gün) `plan` durumda, geliştirici API'da hata tespit ediyor. İhsan hata çözülünceye kadar bekliyor. | **Duruş:** İhsan 10 gün "bekliyor, geliştirici çözsün" diyerek beklemiyor. Hiç tetikleme yok. İş kilitli. | **Çalışması gereken:** İhsan hareketsiz fark ediyor (24h+), KAHİN'e rapor gönder: "COP-26 blokaj 9.7 gün". KAHİN elle tetikler (başlarken), İhsan aynı anda API hatasını çözer. Ajan iş yapar, geliştirici tamir yapar. **Paralel.** | ❌ → ✅ |
| Geliştirici API'yı 2 saat içinde çözer. | Orkes. çöz doğrula, KAHİN'e bildir | İş durmaz; çift hat sayesinde 2 saatte bitmiş oluyor | Hiçbir kaybı yok |

**Mantık:** Ajan iş yapamıyor (araç kırık) → beklemiyor → KAHİN elle başlatıyor → ajan çalışmaya başlıyor → paralelleştirme → zaman kaybı sıfır.

### Kural Değişebilir mi?

**Evet. Şartlı:**
- D-65 kuralı metni AGENTS.md:167-175'te yazılı.
- **Sabit (KAHİN kararı, değiştirilemez):** "Araç/altyapı blokajında iş durmaz" prensibi.
- **Değişebilir (D-66 kararıyla):** Mekanizma nasıl tetiklenir, kim raporlar, ne zaman rapor gönderilir (24h? 12h?).
  - Şu an teklif: `pano_denetim` 24h+ hareketlilik tespit → exit 2 → `tetik_senk` rapor → KAHİN elle.
  - Alternatif: Orkestratör 6h'de bir tarama (daha reaktif ama manuel).
  - KAHİN isterse aralık değişebilir: "24h yerine 12h" → D-66 güncelle → kod güncelle.

**Önerilen karar (D-66):**
```
D-66 "Bypass Tetikleme Mekanizması"
- pano_denetim: blocked + 24h hareketsiz → tespit
- Exit kod 2 → tetik_senk raporla
- KAHİN elle tetikle
- Orkestratör paralelde çöz
```

---

## 2. MIMIR Architect Hakkı — Anlama Rehberi

### Soru: "Architect hakkı MIMIR için ne anlama geliyor?"

**Cevap kısa:** MIMIR şu an yalnız **kod** modunda çalışabilir (implementation). Architect hakkı = aynı zamanda **tasarım/planlama** modunda da çalışabilir olması.

### Tablo: MIMIR Seviye 1 — Mode Yetkileri

| Mode | Şu Anki (Seviye 0) | Önerilen (Seviye 1 + Architect) | Fark |
|------|------|------|------|
| **Code** | ✅ Yapabilir | ✅ Yapabilir | Aynı |
| **Architect** | ❌ Yapamaz | ✅ Yapabilir | **YENİ** |
| **Debug** | ❌ Yapamaz | ❌ Yapamaz | Kısıtlı kalır |

**Architect modunda ne yapabilir:**
- Sistem tasarımı önerileri (D-65 raporunda yaptığı gibi)
- Ölçüm & analiz (stuck görevleri tespit etmek gibi)
- KAHİN kararlarına ait araştırma

**Örnek — Şu an (kısıtlı):**
```
D-65 raporu hazırlanması gerekiyordu.
MIMIR'in yapabileceği: Panoyu oku, sayı çıkar ("2 stuck görev").
MIMIR'in yapamadığı: Raporu yaz, seçenekleri analiz et, öner.
→ İHSAN (code modunda) yapmalı.
```

**Örnek — Architect hakkı verilirse:**
```
D-65 raporu aynı zamanda MIMIR yazabilir.
Architect modda ölçüm → seçenek analiz → öneriler → rapor.
İHSAN'a iş düşmez.
```

### Sebep-Sonuç: Neden MIMIR Architect İstiyor?

| Sebep | Sonuç | Risk |
|-------|-------|------|
| D-65 ölçüm yapması gerekti (sistem analiz) | İHSAN elle rapor yazması saatler aldı | Geliştirici → orkestrator rol karışıklığı |
| Analyst/planlama işleri MIMIR'e ait olmalı | MIMIR architect mode'da özerk çalışabilir | Yapı değişir: planlama + implementation |
| Ölçüm/öneri yazabilirse (code mode yetersiz) | Raporlar otomatik, hızlı, KAHİN'e düz gider | Architect modu disiplini gerekli (kurallar yazılı) |

### KAHİN Kararı İçin Seçenek

**Seçenek A: EVET**
```
D-XXX "MIMIR Architect Hakkı"
- MIMIR Seviye 1'de architect mode'a erişebilir
- İstisna: D-63 (architect kapısı) kuralı → yalnız ihsan/utku
- MIMIR'e izin: ölçüm, rapor yazma, seçenek analiz
- Kısıtlama: KAHİN karar yazamaz (role değil ajan)
```
**Etki:** D-65 gibi görevler MIMIR'e atanabilir. Raporlama otomatik.

**Seçenek B: HAYIR**
```
D-XXX "MIMIR Architect Yasak"
- MIMIR yalnız code modunda
- Planlama/ölçüm görevleri ihsan/utku'ya atanır
- Eksik: ölçüm otomasyonu yetersiz kalır
```
**Etki:** İHSAN manuel raporlama devam. D-65 gibi görevler elle yapılır.

---

## 3. KAHİN Kararları — Sebep-Sonuç Tablosu + Rule Bağlaması

### Tablo: 3 Açık KAHİN Kararı

| Karar | Kural | Sebep | Sonuç | Durum |
|-------|-------|-------|-------|-------|
| **MIMIR Architect Hakkı** | D-182, D-63 | Ölçüm/rapor görevleri elle yapılıyor (saatler kaybı) | MIMIR architect mode'da tasarım/ölçüm raporları yazabilir | **KARAR BEKLIYOR** |
| **GRAPH Kanonik ALAN** | D-172, D-177 | Task ID + field def. dağılmış (GRAPH vs code vs pano) | GRAPH yazı otoritesi olur; task ID değişiklikleri tek noktadan (GRAPH) güncellenir | **KARAR BEKLIYOR** |
| **id-migration Kuralı** | D-60, D-184 | Task ID yeniden adlandırıldığında wikilink'ler kırılıyor | Eski ID → yeni ID redirect + migration trail | **KARAR BEKLIYOR** |

### Kurallara Bağlama

#### Karar 1: MIMIR Architect Hakkı
```
İlişkili Kurallar:
- D-182: MIMIR ajan tanımı (Seviye 0/1, iki mod)
- D-63: Architect kapısı (ihsan/utku yalnız)
- D-59: Test danışman (salih, ölçüm doğrulama)

Bağlantı: D-182'nin "Seviye 1" tanımı genişletilir.
```

#### Karar 2: GRAPH Kanonik ALAN
```
İlişkili Kurallar:
- D-172: Otorite kaynağı = worktree (kod, karar, pano)
- D-177: GRAPH canonical vs yazma otoritesi
- D-184: Graph köprü (karar ↔ kod wikilink)

Bağlantı: D-172/D-177 netlenir. GRAPH yazma otoritesi açıkça yazılır.
```

#### Karar 3: id-migration Kuralı
```
İlişkili Kurallar:
- D-60: Kanonik ad geçişi (eski ID → yeni ID mapping)
- D-184: Graph köprü (wikilink tutarlılığı)
- D-189: Kök AGENTS.md kural taşımaz

Bağlantı: D-60'a migration trail eklenir. Eski ID silinmez, redirect'e çevrilir.
```

---

## 4. Hangi Kurallar Sabit, Hangisi Açık?

| Kural | Tip | Açıklama |
|-------|-----|----------|
| D-65 "İş Durmaz" prensibi | **SABIT** | Blokajda iş duram değil — KAHİN kararı, değişmez |
| D-66 "Bypass Mekanizması" (24h, exit 2) | **AÇIK** | Nasıl uygulanır? 24h yerine 12h olabilir? KAHİN karar verecek |
| D-182 "MIMIR Seviye 0" (code mode) | **SABIT** | MIMIR en az code mode'da çalışabilir — değişmez |
| D-182 "MIMIR Seviye 1 Architect" | **AÇIK** | Architect mode eklensin mi? KAHİN karar verecek |
| D-63 "Architect Kapısı" (ihsan/utku) | **SABIT** | Architect mode yalnız roo/kilo'ya — değişmez |
| D-172 "Otorite Kaynağı" (worktree) | **SABIT** | Worktree ve kod dosyaları tek kaynak — değişmez |
| D-177 "GRAPH Yazma Otoritesi" | **AÇIK** | GRAPH mı yazı kaynağı olsun, yoksa kod mı? KAHİN karar verecek |
| D-184 "Graph Köprü" (wikilink) | **SABIT** | Karar ↔ kod bağlantısı kurulur — değişmez |

---

## 5. Öne Çıkan Bulgular & Öneriler

### Bulgu 1: D-65 Mekanizması Tamamen Yok
- **Sorun:** 2 P1 görev 3-10 gün hareketsiz, bypass tetikleme yok.
- **Fix:** Seçenek (a) uygula → pano_denetim exit 2 + tetik_senk rapor + KAHİN elle tetikle.
- **Takvim:** 1-2 iş günü kod + test.

### Bulgu 2: MIMIR Yetkilendirme Eksik
- **Sorun:** Ölçüm/rapor görevleri elle yapılıyor (D-65 raporu ihsan yazdı).
- **Fix:** MIMIR architect mode → otomatik raporlama.
- **Takvim:** KAHİN kararı → 2-3 gün kod.

### Bulgu 3: GRAPH vs Kod Wikilink Tutarsızlığı
- **Sorun:** Task ID değişince GRAPH ve kod wikilink'leri senkron kalmıyor.
- **Fix:** GRAPH canonical source → D-177 clear rule.
- **Takvim:** Kural + migration script → 2-3 gün.

---

## Kaynaklar

- [`Huginn Data Insights/AGENTS.md`](Huginn Data Insights/AGENTS.md:167-175) — D-65, D-66, D-182, D-63, D-172/D-177
- [`Huginn Data Insights/data/orchestrator/ORKESTRA-D65-ISDURMAZ-01_rapor_2026-09-23_ihsan.md`](Huginn Data Insights/data/orchestrator/ORKESTRA-D65-ISDURMAZ-01_rapor_2026-09-23_ihsan.md) — Ölçüm & D-66 önerisi
- [`Huginn Data Insights/tests/test_d182_mimir.py`](Huginn Data Insights/tests/test_d182_mimir.py) — MIMIR Seviye 1 testleri

