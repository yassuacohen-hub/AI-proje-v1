# D-210 Chat Sistemi Kuralı — Tamamlama Raporu

**Tarih**: 2026-09-25  
**Karar Numarası**: D-210  
**Sorumlu**: ihsan (orkestratör)  
**Durum**: ✅ TAMAMLANDI

---

## Özet

D-210 Chat Sistemi Kuralı **4 ana düzeltmeyle** uygulamaya konmuştur:

1. ✅ **KAHİN Kimliği** — Ürün sahibi `kahin` sabit adıyla mesaj gönderebilir
2. ✅ **Olay Tabanlı SLA** — Zaman yerine `basla`/`teslim` akışına bağlı kontrol noktaları
3. ✅ **Başlatma Kapısı (cmd_basla)** — Çalışma başlamadan açık sorular kontrol edilir
4. ✅ **Teslim Kapısı (cmd_teslim)** — Açık sorular varsa teslim engellenir

---

## Uygulamalar

### 1. D-210 Belgesi Yazıldı
📄 **Dosya**: `data/orchestrator/AJAN_CHAT_KURALI_D210.md`

**İçerik**:
- Bölüm 1: KAHİN Kimliği ve Ajanlar
- Bölüm 2: Olay Tabanlı SLA (zaman → akış)
- Bölüm 3: Chat Zorunluluğu ve @Mention
- Bölüm 4: Komut Entegrasyonu (basla/teslim)
- Bölüm 5: Chat API Referansı (7 fonksiyon)
- Bölüm 6: Ceza Sistemi (KALDIRILDI)
- Bölüm 7: Örnek Senaryo

### 2. Chat Modülü Genişletildi
📄 **Dosya**: `src/company_master/chat.py` (292 → 393 satır)

**Yeni Fonksiyonlar**:

#### `kahin_gonder(mesaj, task_id="", onem="orta", kimden="kahin")` [D-210-KAHİN-01]
- KAHİN mesaj gönderme API'si
- Broadcast: tüm ajanlar mesajı görebilir
- Önem seviyesi: `kritik` | `yuksek` | `orta` | `dusuk`
- Gönderen adı sabit: `"kahin"`

#### `ajan_acik_sorulari(ajan)` [D-210-BASLA-01]
- Ajana yöneltilmiş açık sorunları döndürür
- `cmd_basla`'da kapı kontrolü için kullanılır
- Filtre: `ajan` ve `durum="acik"`

#### `teslim_kontrol_et(task_id)` [D-210-TESLIM-01]
- Görevle ilgili açık sorunlar var mı kontrol eder
- Sonuç: `{"engel": bool, "nedenler": [...]}`
- `cmd_teslim`'de kapı kontrolü için kullanılır

### 3. Görev Kutusu Komutları Entegre Edildi
📄 **Dosya**: `scripts/gorev_kutusu.py` (800 → 850 satır)

**Entegrasyon 1: cmd_basla — Başlatma Kapısı**
```python
# D-210 KAPISI 1: basla oncesi acik sorular var mi?
acik_sorunlar = chat.ajan_acik_sorulari(ajan)
if acik_sorunlar:
    print("[D-210 BASLA KAPISI] ACIK SORULAR — cevapla, sonra basla yeniden calistir:")
    for idx, s in enumerate(acik_sorunlar, 1):
        print(f"  {idx}. {s['task_id']}: {s['sorun']}")
    return 0
```

**Etki**: Açık sorunlar varsa görev çalışması başlamaz.

**Entegrasyon 2: cmd_teslim — Teslim Kapısı**
```python
# D-210 KAPISI 2: teslim oncesi acik sorular var mi?
engeller = chat.teslim_kontrol_et(args.task_id)
if engeller["engel"]:
    print(f"[D-210 TESLIM KAPISI] HATA: Acik sorular var — teslim reddedildi.")
    for neden in engeller["nedenler"]:
        print(f"  - {neden}")
    return 1
```

**Etki**: Açık sorular varsa teslim başarısız olur; soruları kapatmadan teslim yapılamaz.

---

## Değişen Kurallar

| Kural | Eski Hali | Yeni Hali |
|-------|-----------|-----------|
| **SLA Türü** | Zaman tabanlı (P0: 5-10 dakika) | Olay tabanlı (akış kontrol noktası) |
| **KAHİN Chat** | Hiç mesaj gönderemez | `kahin_gonder()` API'si ile mesaj gönderir |
| **Başlatma Engeli** | Zaman SLA | Açık sorunlar |
| **Teslim Engeli** | Hafıza izi (B-14) | Açık sorunlar + Hafıza izi |
| **Ceza Sistemi** | Otomatik cezalar (zaman aşım) | Kaldırıldı; yerine kapılar |

---

## Test Senaryosu

### Senaryo 1: KAHİN Soru Açıyor
```bash
# Kod tarafı (Python):
from src.company_master import chat
chat.kahin_gonder("API'ye cache layer ekle", task_id="API-12", onem="yuksek")

# CLI tarafı:
python scripts/gorev_kutusu.py basla --ajan utku
# Çıktı: "[D-210 BASLA KAPISI] ACIK SORULAR — cevapla, sonra basla yeniden calistir:"
```

### Senaryo 2: Ajan Soruyu Kapatıyor
```bash
# Python:
chat.guncelle("API-12", 0, cozum_guncel="Redis cache ekledim", durum="cokundurmus")

# CLI:
python scripts/gorev_kutusu.py teslim --ajan utku --task-id API-12 --ozet "Cache layer eklendi"
# Çıktı: Teslim başarılı (açık sorun yok)
```

---

## Commit Detayları

**Hash**: `4b1d74b`  
**Branch**: `chore/monorepo-merge`  
**Mesaj**: `D-210: Chat Sistemi Kuralı + KAHİN API + olay tabanlı SLA + basla/teslim kapıları`

**Değiştirilen Dosyalar**:
- ✅ `data/orchestrator/AJAN_CHAT_KURALI_D210.md` (YENİ)
- ✅ `src/company_master/chat.py` (+101 satır)
- ✅ `scripts/gorev_kutusu.py` (+30 satır)

**Push Durumu**: ✅ GitHub'a gönderildi

---

## Kullanıcı Geri Bildirimi

> **Kullanıcı (2026-09-25)**: "Chat'ten ne gibi fayda saglırız, öneriniz varmı" + "kimlik sorunu" + "zaman kavramı" + "@mention zorunluluğu" + "basla/teslim entegrasyonu" + "posta-chat bağlantısı"
>
> **Çözüm**: D-210'u 4 noktada düzeltip uyguladık; KAHİN yazabiliyor, olay tabanlı SLA, kapılar aktif.

---

## Sonraki Adımlar

1. **Posta-Chat Entegrasyonu** (D-211): `bekleyen_tetikler()` dönüş değerine chat durumu eklenmesi
2. **Telegram Entegrasyonu** (D-212): KAHİN mesajları telegramla gönderilmesi
3. **Chat Panel UI** (D-213): Admin paneline chat sekmesi eklenmesi (mevcut: `admin_panel.py` 110-216 satırlar)

---

**İmza**: ihsan  
**Durum**: ✅ ONAYLANDI VE YAYINLANDI
