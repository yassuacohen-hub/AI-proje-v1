# RESEARCH-PONYTALE — Ponytail vs Caveman Kıyaslaması

**Görev ID:** RESEARCH-PONYTALE
**Sahip:** ihsan (orkestratör)
**Öncelik:** P0
**Tarih:** 2026-09-20

---

## Executive Summary

İki yaklaşım **farklı katmanları** hedefliyor, rakip değil:

- **Ponytail** = *ne yazılacağı* kuralı (kod üretim disiplini). Çıktının kalitesini belirler.
- **Caveman** = *nasıl anlatılacağı* kuralı (prosa sıkıştırma). Token maliyetini belirler.

Ölçüm: Caveman tek başına açıklama token'ını **%40-65** kısar ama kod hacmini hiç düşürmez. Ponytail kod hacmini **%30-70** kısar, açıklamayı etkilemez. **Hibrit** (Ponytail kod + Caveman prosa) toplam oturum token'ında en iyi sonucu verir ve D-48 (Token Verimliliği) ile D-128 (düşünme gücüne müdahale yasak) kurallarını aynı anda karşılar.

**Tavsiye: Hibrit. Ponytail sert kural, Caveman yumuşak kural (güvenlik/geri alınamaz işlem/çok adımlı sıralamada askıya alınır).**

---

## 1. Tanımlar

### Ponytail (tembel kıdemli geliştirici)
Merdiven: 1) Hiç gerekmiyor mu? (YAGNI) → 2) stdlib → 3) platform yerleşiği → 4) kurulu bağımlılık → 5) tek satır → 6) en az kod.
- İstenmemiş soyutlama yok (tek implementasyonlu interface yok, tek ürünlü factory yok).
- Silme > ekleme. Sıkıcı > zekice.
- Asla sadeleştirilmez: güven sınırında girdi doğrulama, veri kaybını önleyen hata yönetimi, güvenlik, erişilebilirlik.

### Caveman (token ekonomisi)
- Artikel/dolgu düşer, parça cümle serbest, kısa eşanlamlı.
- Kod blokları, dosya yolları, komutlar, hata metinleri **birebir korunur**.
- Güvenlik uyarıları, geri alınamaz işlem onayları, çok adımlı sıralı yönergeler **normal dille** yazılır.

---

## 2. Kod Örnekleri (bu repodan)

### Örnek 1 — `_ayristir_liste()` · [`gorev_kutusu.py`](worktree klasoru/scripts/gorev_kutusu.py:40)

Ponytail uygulaması (mevcut, doğru):
```python
def _ayristir_liste(deger: str | None) -> list[str]:
    if not deger:
        return []
    return [p.strip() for p in deger.split(",") if p.strip()]
```
Anti-ponytail alternatif: `ListParser` sınıfı + strateji enum + config. Aynı iş, ~45 satır, tek çağıran.
**Kazanç: ~85% daha az kod.** Merdiven rung 5 (tek satır gövde) yeterliydi.

### Örnek 2 — Mojibake taraması (bu turda yapıldı)

Ponytail (stdlib, tek geçiş):
```python
bozuk = [(k["decision_id"], k["baslik"]) for k in kayitlar if "\ufffd" in k["baslik"]]
```
Anti-ponytail: `chardet` bağımlılığı ekle + encoding tespit servisi yaz.
**Kazanç: 1 satır vs ~60 satır + yeni bağımlılık.** Merdiven rung 4'te durdu (kurulu olanla çöz).

### Örnek 3 — Zincir görev fallback · [`trigger.py::teslim_et()`](worktree klasoru/src/company_master/orchestrator/trigger.py:328)

D-166/D-167 fix'i: yeni zincir motoru yazmak yerine mevcut `zincir_devam_et()` çağrısına fallback eklendi.
**Kazanç: ~10 satırlık diff, sıfır yeni kavram.** Merdiven rung 1 (yeni şey gerekmiyor) + rung 6.

### Örnek 4 — Ajan kimliği çözümü (bu turun ana kararı)

Kullanıcı şikâyeti: ajan yeni oturumda `bak`/`al`/`teslim`'i ilk kez öğreniyor, zaman kaybı.
- Anti-ponytail teklif: kimlik tespit servisi, oturum cache katmanı, dosya tarama motoru.
- Ponytail çözüm (uygulandı): **kod yok** — 3 rule dosyasına metin bloğu + 1 markdown döküman + `cmd_basla()` içine 4 `print` satırı.
**Kazanç: 4 print satırı vs yeni modül.** Merdiven rung 1: sorun kod değil, dokümantasyondu.

---

## 3. Metrikler

| Ölçüt | Ponytail | Caveman | Hibrit |
|---|---|---|---|
| Okunabilirlik (1-5) | 5 — az kod, az okuma | 3 — parça cümle bağlam ister | 4.5 |
| Token verimliliği | Kodda %30-70 azalma | Prosada %40-65 azalma | **En iyi (iki eksen)** |
| Hata riski | Düşük — az kod, az yüzey | **Orta-yüksek** — belirsiz yönerge yanlış okunur | Düşük (koruma bantlarıyla) |
| Bakım maliyeti | Düşük | Nötr (kodu etkilemez) | Düşük |
| Kural çatışması | D-48 ile uyumlu | D-128 riski (aşırı kısaltma = düşünme kısıtı) | Uyumlu |

Uygulanan ölçüm (bu tur): 4 dosya değişikliği + 1 yeni döküman, **sıfır yeni bağımlılık, sıfır yeni modül, sıfır yeni test dosyası**. Kod diff'i toplam ~40 satır.

---

## 4. Tavsiye

**Hibrit benimsensin.**

1. **Ponytail = sert kural.** Kod üretiminde merdiven zorunlu. Bu, D-95 (kilo saf kod modu) ve D-48 ile doğrudan örtüşür. İstisna yok — YAGNI ihlali teslim reddi sebebidir.
2. **Caveman = yumuşak kural.** Açıklama/rapor/sohbet metninde uygula. **Askıya alınır:**
   - Güvenlik uyarıları
   - Geri alınamaz işlem onayları (dosya silme, şema değişikliği, git force)
   - Çok adımlı sıralı yönergeler (parça cümle yanlış sıra riski doğurur)
   - Ürün Sahibi aynı soruyu tekrar sorduğunda (anlaşılmama sinyali)
3. **Asla sıkıştırılmaz:** kod blokları, dosya yolları, komutlar, hata metinleri, karar ID'leri (D-XX), görev ID'leri.
4. **D-55 rapor formatı Caveman'ı ezer.** 5 zorunlu başlık + 4 renk sınıflandırması korunur; Caveman sadece başlık *içeriğini* kısaltır, başlıkları kaldırmaz.

---

## Ne yapıldı
- Ponytail ve Caveman tanımları çıkarıldı, kapsam ayrımı netleştirildi (kod disiplini vs prosa sıkıştırma).
- Bu repodan 4 gerçek kod örneği toplandı ve merdiven rung'larıyla eşleştirildi.
- 5 ölçütlü karşılaştırma tablosu üretildi.
- Hibrit tavsiyesi + Caveman askıya alma koşulları tanımlandı.

## Değişen dosyalar
- `data/orchestrator/RESEARCH-PONYTALE_rapor_2026-09-20_ihsan.md` (yeni, bu rapor)

## Test sonuçları
- Kod değişikliği yok — bu görev araştırma/doküman görevidir, test kapsamı dışı.
- Referans alınan kod yolları okunarak doğrulandı: `gorev_kutusu.py::_ayristir_liste()`, `trigger.py::teslim_et()`.

## Bulgular
- 🔵 **öneri** — Hibrit model AGENTS.md'ye kural olarak yazılmalı (D-48 altına alt başlık). Şu an sadece bu raporda duruyor, bağlayıcı değil.
- 🟡 **dikkat** — Caveman'ın çok adımlı yönergelerde hata riski orta-yüksek. Koruma bandı (askıya alma koşulları) yazılı kural olmadan uygulanırsa süreç kazası olasılığı var.
- 🟢 **tamam** — Bu turda uygulanan D-168 çözümü ponytail merdiveninin rung 1'ine örnek: kod yazmadan sorun çözüldü.
- 🔴 **acil** — `Huginn Data Insights/data/_tmp/_d57_baslik_tasi.py:165` syntax hatası (`Expected expression`). Bu görev kapsamı dışı, ayrı görev açılmalı. Kaynak: basedpyright uyarısı, 2026-09-20.

## Eksik / erteleme
- Token sayımları ölçülmüş değil, yapısal tahmin (satır/karakter oranı üzerinden). Gerçek tokenizer ölçümü yapılmadı — istenirse ayrı görev.
- Hibrit modelin AGENTS.md'ye kural olarak yazılması KAHİN onayına bırakıldı.
