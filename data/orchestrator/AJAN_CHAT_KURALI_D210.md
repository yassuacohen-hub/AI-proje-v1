# Ajan Chat Sistemi Kuralı — D-210

> **Ürün Sahibi (KAHİN) için NOT:** Chat sistemi ajanlar arasında problemleri açıp çözmek için tasarlanmıştır. Siz Ürün Sahibi kimliğiyle mesaj gönderebilirsiniz, fakat **kimlik gerekir** — gönderen `kahin` sabit adıyla kaydedilir. Aşağıdaki kurallar ajanların birbirlerine yanıt vermesini zorunlu kılar.

## Bölüm 1: Kimlik ve Rol

### KAHİN (Ürün Sahibi) Kimliği
- **Sistem Sabiti**: `KAHIN_AJAN = "kahin"`
- **Gönderici Adı**: Ürün sahibi tarafından gönderilen tüm mesajlar `kimden="kahin"` olarak kaydedilir
- **Mesaj Gönderme API'si**: `chat.kahin_gonder(mesaj, task_id="", onem="orta")`
  - Mesaj türü: 1–500 karakter
  - Önem seviyesi: `kritik` | `yuksek` | `orta` | `dusuk`
  - Task ID isteğe bağlı (boşsa genel sorun)

### Ajanlar (Alıcılar)
- **Kanonik adlar**: `ihsan` (orkestratör) · `utku` (üretim) · `salih` (test) · `yasu` (denetim)
- **Görev Sahibi**: Her görev bir ajana atanır; atanmış ajan **sorumlu alandır**

## Bölüm 2: Olay Tabanlı SLA (Zaman Yerine)

> **Değişim Notu (D-210):** Sabit zaman SLA'sı (P0: 5-10 dakika vb.) kaldırıldı. Ajanlar (LLM) gerçek zamanlı saati takip edemez. Yerine: **görev akışına bağlı kontrol noktaları** kullanılır.

### SLA Akışı
1. **BAŞLATMA (cmd_basla)**
   - Ajan görevleri alır (`cmd_basla`)
   - **Check:** Açık sorular var mı?
   - Varsa ekrana liste yazılır, cevap beklenir
   - Sorular kapatılmadan çalışma başlamaz (kapı 1)

2. **ÇALIŞMA (al → iş → teslim)**
   - Ajan kendi hızında çalışır
   - SLA süresi değişkendi; şimdi **görev bitişine bağlı**

3. **TESLİM (cmd_teslim)**
   - Ajan görevleri teslim eder
   - **Check:** Açık sorular var mı?
   - Varsa teslim **BAŞARISIZ** — sorular kapatılana kadar bekle (kapı 2)
   - Sorular kapatılıp teslim yeniden çalıştırılır

### Sonuç
- **Önem seviyesi artık `basla`/`teslim` kapılarında engelleyici değil** — açık sorular engel
- Önem seviyesi yalnız chat mesajını hızlandırmak için kullanılır (kritik = aciliyet işareti)

## Bölüm 3: Chat Zorunluluğu ve @Mention

### Kural
- **Adına açılan sorun**: Ajan o sorunun sahibi adına atanmış ise cevaplamak **zorunludur**
- **Sonuç**: Açık sorun = önemli iş engeli
- **Yetki**: Ajan sorunu "çökundurmuş" durumuna getirerek erteleyebilir, "çözüldü" diyemez

### @Mention (KAHİN İçin)
- Belirli ajana hitap ederken: `@utku problemi X ile var` → `chat.kahin_gonder(..., ajan="utku", ...)`
- **Kural**: @mention edilmiş ajana mesaj zorunlu olarak **kütüphaneye yazılır** ve ajan bundan haberdar edilir

## Bölüm 4: Komut Entegrasyonu (basla/teslim Kapıları)

### cmd_basla — Başlatma Kapısı
```python
def cmd_basla(...):
    # ... zincir göster ...
    acik_sorunlar = chat.ajan_acik_sorulari(ajan)
    if acik_sorunlar:
        print(f"\n⚠️  AÇIK SORULAR (cevapla, sonra basla yeniden calistir):")
        for s in acik_sorunlar:
            print(f"  - {s['task_id']}: {s['sorun']} (kimden: {s['kimden']})")
        print()
        return 0  # Çalışma başlamaz
    # ... devam et ...
```

### cmd_teslim — Teslim Kapısı
```python
def cmd_teslim(...):
    # ... mevcut kontroller ...
    engeller = chat.teslim_kontrol_et(args.task_id)
    if engeller["engel"]:
        print(f"HATA: Teslim reddedildi — açık sorular var:")
        for neden in engeller["nedenler"]:
            print(f"  - {neden}")
        print("\nSoruları cevapla, sonra teslim yeniden calistir.")
        return 1
    # ... teslim et ...
```

## Bölüm 5: Chat API Referansı

### 1. Sorun Aç — `ac(...)`
```python
chat.ac(ajan="utku", task_id="UI-5", sorun="Button renginde bug var",
        cozum="CSS'te #ff0000 yerine #ff0055 yap", kimden="kahin", onem="yuksek")
```

### 2. Sorun Güncelle — `guncelle(...)`
```python
chat.guncelle(task_id="UI-5", sorun_index=0, cozum_guncel="CSS değişti, test et",
              durum="cokundurmus")
```

### 3. Sorun Kapat — `kapat(...)`
```python
chat.kapat(task_id="UI-5", sorun_index=0, karar="CSS fix'i merged")
```

### 4. Mesaj Oku — `oku(...)`
```python
sorunlar = chat.oku(task_id="UI-5")  # UI-5'teki tüm sorunlar
son_10 = chat.oku(son=10)             # son 10 sorun (tüm görevler)
```

### 5. KAHİN Gönder — `kahin_gonder(...)` [YENİ]
```python
chat.kahin_gonder(mesaj="Tasarım değişti, şu hissiyatı test et",
                  task_id="UI-5", onem="yuksek", kimden="kahin")
```

### 6. Ajana Yöneltilmiş Açık Sorular — `ajan_acik_sorulari(...)` [YENİ]
```python
sorunlar = chat.ajan_acik_sorulari("utku")  # utku'ya hitap eden açık sorunlar
```

### 7. Teslim Kontrol — `teslim_kontrol_et(...)` [YENİ]
```python
engeller = chat.teslim_kontrol_et("UI-5")
# Sonuç: {"engel": bool, "nedenler": [...]}
```

## Bölüm 6: Ceza Sistemi (Kaldırıldı)

> **Değişim Notu (D-210):** Zamanlamaya dayalı otomatik cezalar kaldırıldı. Sebep: Ajanlar (LLM) belirli saatlerde yanıt veremez. **Yerine**: Açık sorunlar = kendiliğinden engel (kapı mekanizması).
>
> **Manuel Müdahale**: KAHİN sorunu elle kapatsın veya ajana özel talimat verssin.

## Bölüm 7: Örnek Senaryo

### Senaryo: KAHİN "Yeni gereksinim" sorusu açıyor
1. KAHİN: `chat.kahin_gonder("API'ye cache layer ekle", task_id="API-12", onem="yuksek")`
2. Sistem: "API-12"'nin sahibi utku; chat log'una yazılır
3. utku `cmd_basla` çalıştırır:
   - Açık sorular listesi ekrana çıkar
   - utku soruyu oku
4. utku `chat.guncelle("API-12", 0, cozum_guncel="Redis cache ekledim", durum="cokundurmus")`
5. utku `cmd_teslim` çalıştırır:
   - `teslim_kontrol_et` check — sorun "cokundurmus" ise pass (engel yok)
   - Teslim kabul edilir, KAHİN'e rapor gönderilir

---

## Kurallar (Özet)

| Kural | Açıklama |
|-------|----------|
| **D-210-1** | KAHİN "kahin" kimliğiyle gönderici olarak kaydedilir |
| **D-210-2** | Olay tabanlı SLA: zaman yerine `basla`/`teslim` kapıları kontrol eder |
| **D-210-3** | Açık sorunlar = görev başlatma/teslim engelleyici |
| **D-210-4** | Ceza sistemi kaldırıldı; yerine otomatik kapılar |
| **D-210-5** | Posta-chat entegrasyonu: `bekleyen_tetikler()` chat durumu döndürür |

---

**Kaynaklar:**
- [[D-192]] — Ajan Chat Sistemi (Kütüphane)
- [[AGENTS.md]] — D-210 Karar Defteri
- `src/company_master/chat.py` — Kütüphane uygulaması
- `scripts/gorev_kutusu.py` — `cmd_basla()`, `cmd_teslim()` kapıları
