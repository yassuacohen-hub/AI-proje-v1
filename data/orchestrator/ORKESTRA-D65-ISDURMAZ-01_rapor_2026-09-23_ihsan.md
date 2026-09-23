# ORKESTRA-D65-ISDURMAZ-01 — İş Durmaz (Blokaj Bypass) Ölçüm & Öneriler

**Brief:** D-65 kuralı "araç/altyapı hatası bloke ediyorsa, orkestratör işi bekletmez" diyor. Fiilen uygulanıyor mu?

**Sonuç:** Olumsuz. 2 P1 görev 3-10 gün hareketsiz, bypass mekanizması yok.

---

## 1. Ölçüm Sonuçları

- **Toplam görev:** 376
- **Blocked + Plan durumu:** 4
- **Stuck (≥24h hareketsiz):** 2

| Task ID | Durum | Sahip | P | Hareketsiz Gün |
|---------|-------|-------|---|---|
| COP-26 | plan | ihsan | P1 | 9.7 |
| ORKESTRA-DECISION-LOG-03 | plan | ihsan | P1 | 3.1 |

---

## 2. D-65 Kural Metni vs Mevcut Davranış

### Kural (AGENTS.md:167-175)

> **D-65 "İş Durmaz":** Araç/altyapı hatası bloke ediyorsa, orkestratör işi bekletmez.
> 1. KAHİN'e elle tetikleme metni gönder (görev ID + brief + iş maddeleri + test komut).
> 2. KAHİN elle tetikler, ajan başlar.
> 3. Orkestratör paralelde hatayı çözer; çözünce doğrular, KAHİN'e bildirir.

### Mevcut Davranış

| Senaryoda | Kural Saydığı | Mevcut Kod | Fark |
|----------|---|-----------|------|
| Görev `blocked` durumu | İş durmaz; KAHİN'e bildir | Hiçbir tetikleme yok | ❌ Tetikleme mekanizması yoktur |
| Görev `plan` durumu | İş durmaz; KAHİN'e bildir | Hiçbir eskalasyon yok | ❌ Eskalasyon kodu yok |
| N saat hareketsiz | KAHİN elle başlatır | Uyarı sadece pano_denetim'de | ❌ Otomatik tetikleme yok |
| Orkestratör çözer | Çöz → doğrula → bildir | Hiçbir bypass akışı yok | ❌ Yapısal boşluk |

**Bulgu:** D-65 kuralı tamamen uygulanmamış. Kod hiçbir bypass tetikleme, eskalasyon veya KAHİN bildirim mekanizması içermez.

---

## 3. Önerilen Mekanizma

**Seçim: Seçenek (a) — pano_denetim'e bypass + exit kodu**

Gerekçe:
- Minimal yapısal değişim
- Mevcut denetim döngüsüyle uyumlu (haftalık `basla` çağrısı var)
- KAHİN'e bildir ve elle tetikle (iş durmaz)

**Uygulama:**
1. `pano_denetim.tara()` → `blocked` + hareketsiz ≥24h tespit
2. Exit kod 2 (bypass gerekli) döner
3. `tetik_senk.py` / orkestratör weekly job exit 2 gördüğünde:
   - KAHİN'e rapor gönder (görev ID, durum, sahibi, gün sayısı)
   - Elle tetikleme talimatı ekle
4. KAHİN elle `basla` yapar
5. Orkestratör paralelde hatayı çözer

---

## 4. KAHİN Karar Taslağı

```
## D-66 "Bypass Tetikleme" (KAHİN kararı [tarih])

**Amaç:** D-65 "İş Durmaz" kuralını uygula. Araç blokajı nedeniyle hareketsiz kalan P1 görevler otomatik olarak KAHİN'e escalate edilir. KAHİN elle başlatır, orkestratör paralelde çözer.

**Uygulama:**
- pano_denetim.tara() blocked + ≥24h tespit → exit 2
- tetik_senk.py / weekly job exit 2 aldığında:
  - AGENT_SYNC.md'ye rapor satırı ekle: "BYPASS_GEREKLI: task_id durum sahip gün"
  - KAHİN'e Slack/email bildir
- KAHİN elle tetikleme komutu yazıp çalıştırır
- Orkestratör paralelde çözer, çözünce raporla

**Yaşam döngüsü:**
- blocked → (≥24h) → exit 2 → KAHİN rapport → elle basla → (paralel çözüm) → done

**Sorumlu:** orkestrator, tetik_senk, pano_denetim, KAHİN
**Testi:** test_d65_bypass_tetikleme.py (exit 2 tespit, rapor, elle başlatma)
```

---

## 5. Seçilmemiş Seçenekler ve Gerekçeleri

**(b) gorev_kutusu bakim'de otomatik blocked→plan düşürme:**
- Bypass değil, problem gizleme (iş yine duruyor)
- Kural ihlali

**(c) orkestratör oturum açılışında zorunlu rapor:**
- Reactive, proactive değil
- 24h delay tahammül edilemez

---

## 6. Dosyalar

- `scripts/pano_denetim.py` — tara() exit 2 ekle
- `scripts/tetik_senk.py` — exit 2 handling + rapor
- `tests/test_d65_bypass_tetikleme.py` — yeni, 4 test
- `AGENTS.md` — D-66 karar ekle

---

## Sonuç

D-65 kuralı metni kodda yok. Stuck görevler 3+ gün hareketsiz, otomatik tetikleme yok. Seçenek (a) ile uygula: pano_denetim exit 2 → tetik_senk rapor → KAHİN elle tetikle.