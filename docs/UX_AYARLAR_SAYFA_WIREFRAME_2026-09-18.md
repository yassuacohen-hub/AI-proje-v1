# Kullanıcı Ayarları Sayfası — Wireframe (2026-09-18)

> **Görev:** `ADMIN-UX-AYARLAR-SAYFA-01` (P1)
> **Hedef dosya:** `web_dashboard/tabs/admin_kullanici_ayarlari.py`
> **Belge düzeni:** D-56 — 4 ana başlık
> **Durum:** 🟡 onay bekliyor (kod yazılmadı)

---

## 1. Şu an ne var (AS-IS)

### 1.1 Mevcut ekran

Sayfa: `web_dashboard/tabs/admin_panel.py::render_ayarlar_tab()` (satır 246-333)

```
┌─ Kullanıcı Ayarları ────────────────────────────┐
│ ⚙️  Sistem · Ayarlar                            │
│ Panel davranışını kendi kimliğinize göre...     │
├─────────────────────────────────────────────────┤
│ [ℹ️ Sekme rehberi]   Ayarlar bu kullanıcıya özel│
├─────────────────────────────────────────────────┤
│  🎛️ Ayar Grupları  ·  ↩️ Sıfırlama              │
├─────────────────────────────────────────────────┤
│  [Görünüm][Veri][Bildirim][Bölgesel]            │
│   ▸ tema:      [karanlık ▾]                     │
│   ▸ satır:     [  50   ]                        │
│   ▸ ...                                         │
│                            [💾 Kaydet]          │
├─────────────────────────────────────────────────┤
│  ↩️ Varsayılanlara dön                          │
└─────────────────────────────────────────────────┘
```

### 1.2 Şifre işlemleri nerede? (dağınık)

| İşlem | Şu anki yeri | Sorun |
|---|---|---|
| Şifre değiştir | Sol-alt profil balonu içinde | 🔴 Ayarlarda yok, balonda saklı |
| Şifre unuttum | Yalnız giriş ekranında | 🟡 Oturum açıkken ulaşılamaz |
| E-posta / rol görme | Hiçbir yerde net değil | 🟡 Yalnız balon başlığında |

### 1.3 Tespit edilen problemler

| # | Problem | Sınıf |
|---|---|---|
| P1 | Şifre değiştirme formu **balon içinde** — dar alan, kapanınca kaybolur | 🔴 |
| P2 | Hesap bilgisi (e-posta, rol) gösterilmiyor | 🟡 |
| P3 | Şifre sıfırlama oturum açıkken erişilemez | 🟡 |
| P4 | Ayarlar sayfası **yalnız panel tercihleri** — hesap yok | 🟡 |
| P5 | Kod `admin_panel.py` içinde, karar defteriyle aynı dosyada | 🔵 |

**Oran:** 1 kırmızı %20 · 3 sarı %60 · 1 mavi %20

---

## 2. Ne olacak (TO-BE)

### 2.1 Yeni sayfa düzeni

```
┌─ Kullanıcı Ayarları ────────────────────────────┐
│ ⚙️  Sistem · Ayarlar                            │
├─────────────────────────────────────────────────┤
│  👤 Hesap   ·   🔐 Güvenlik   ·   🎛️ Tercihler  │  ← 3 bölüm
├─────────────────────────────────────────────────┤
│                                                 │
│  👤 HESAP                                       │
│  ┌───────────────────────────────────────────┐  │
│  │  E-posta   admin@huginn.local             │  │
│  │  Rol       admin                          │  │
│  │  Oturum    açık                           │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  🔐 GÜVENLİK                            #sifre  │  ← deep-link hedefi
│  ┌───────────────────────────────────────────┐  │
│  │  Şifre Değiştir                           │  │
│  │   Mevcut şifre   [••••••••]               │  │
│  │   Yeni şifre     [••••••••]               │  │
│  │   Yeni (tekrar)  [••••••••]               │  │
│  │                        [🔑 Değiştir]      │  │
│  ├───────────────────────────────────────────┤  │
│  │  ▸ Şifremi unuttum (e-posta ile sıfırla)  │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  🎛️ TERCİHLER                                   │
│  ┌───────────────────────────────────────────┐  │
│  │  [Görünüm][Veri][Bildirim][Bölgesel]      │  │
│  │   ▸ tema:   [karanlık ▾]                  │  │
│  │   ▸ satır:  [  50   ]                     │  │
│  │                        [💾 Kaydet]        │  │
│  ├───────────────────────────────────────────┤  │
│  │  ↩️ Varsayılanlara dön                    │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 2.2 Misafir (oturum kapalı) görünümü

```
┌─ Kullanıcı Ayarları ────────────────────────────┐
│  ℹ️ Ayarları kaydetmek için giriş yapın         │
│                                                 │
│  🎛️ TERCİHLER  (salt okunur)                    │
│   ▸ tema: karanlık                              │
│   ▸ satır: 50                                   │
└─────────────────────────────────────────────────┘
```
**Hesap ve Güvenlik bölümleri misafirde hiç çizilmez.**

### 2.3 Değişim tablosu

| Ne | Önce | Sonra |
|---|---|---|
| Bölüm sayısı | 2 (Gruplar, Sıfırlama) | **3** (Hesap, Güvenlik, Tercihler) |
| Şifre değiştir | Profil balonunda | **Sayfada, tam genişlik** |
| Şifre unuttum | Yalnız giriş ekranı | **Ayarlarda da var** |
| Hesap bilgisi | Yok | **E-posta + rol + oturum** |
| Dosya | `admin_panel.py` (335 satır, 2 iş) | **`admin_kullanici_ayarlari.py`** (tek iş) |
| Menüdeki yeri | Sol menüde "Ayarlar" | Menüden kalkar → profil balonundan açılır |

### 2.4 Kazanım

| Ölçüt | Önce | Sonra | Değişim |
|---|---|---|---|
| Şifre değiştirmeye tıklama | 3 (balon → buton → form) | **2** (balon → Şifre Değiştir) | **%33 azalma** |
| Hesap bilgisi görünürlüğü | %0 | **%100** | — |
| `admin_panel.py` satır | 335 | ~245 | **%27 azalma** |

---

## 3. Nasıl yapılacak

### 3.1 Dosya sözleşmesi

```python
# web_dashboard/tabs/admin_kullanici_ayarlari.py

BOLUMLER: tuple[Section, ...]   # Hesap · Güvenlik · Tercihler

def render_kullanici_ayarlari_tab(kullanici_id: str | None = None) -> None
```

Navigasyon kaydı (`web_dashboard/tabs/__init__.py`) güncellenir:
`modul` → `web_dashboard.tabs.admin_kullanici_ayarlari`
`fonksiyon` → `render_kullanici_ayarlari_tab`

### 3.2 Yeniden kullanılan mevcut kod (yeni kod yazılmaz)

| Parça | Nereden geliyor |
|---|---|
| Şifre değiştirme formu | `admin_auth.py::render_sifre_degistir()` |
| Şifre sıfırlama akışı | `admin_auth.py::render_sifre_unuttum()` |
| Oturum kimliği | `admin_auth.py::get_admin_token()` |
| Ayar formu üretimi | `admin_panel.py::_form_degeri()` → taşınır |
| Ayar okuma/yazma | `company_master.settings` |
| Sayfa iskeleti | `PageHeader` · `SectionNav` · `Section` |

🟢 **Yeni iş mantığı yazılmaz.** Yalnız düzen + taşıma.

### 3.3 Görsel tokenlar

Yeni renk **eklenmez**. `src/company_master/ui/tokens.py`:

| Öğe | Token |
|---|---|
| Kart zemin | `RENKLER["yuzey_2"]` |
| Ayraç | `RENKLER["kenar"]` |
| Bölüm boşluğu | `BOSLUKLAR["l"]` |
| Kart köşe | `YARICAPLAR["m"]` |

### 3.4 Erişilebilirlik

- Bölüm sırası sabit: Hesap → Güvenlik → Tercihler
- `#sifre` bağlantısı Güvenlik bölümüne iner
- Şifre alanları `type="password"`
- Hata mesajı alanın **hemen altında**, yalnız renkle değil metinle de belli
- Kaydet hepsi-ya-hiç davranışı korunur

### 3.5 Güvenlik kısıtı 🔴

- Mevcut şifre doğrulaması **zorunlu** kalır — kaldırılmaz
- Misafir kimlikte Güvenlik bölümü **hiç çizilmez** (form bile oluşturulmaz)
- Şifre sıfırlama tetikleyen e-posta akışı değişmez

---

## 4. Onay için özet

### 4.1 Bağımlılıklar

| Bağımlılık | Durum |
|---|---|
| `ADMIN-UX-MENUTREE-01` — Ayarlar menüden kalkar | 🟡 sonra yapılacak |
| `ADMIN-UX-PROFILMENU-01` — balondan deep-link | 🟡 sonra yapılacak |
| Bu iş tek başına çalışır mı? | 🟢 **Evet** — menüde kalarak da çalışır |

### 4.2 Kabul kriterleri (test edilecek)

| # | Kriter |
|---|---|
| 1 | Sayfa 3 bölüm çizer (Hesap, Güvenlik, Tercihler) |
| 2 | Misafirde Hesap + Güvenlik çizilmez |
| 3 | Şifre değiştirme mevcut şifre ister |
| 4 | Ayar kaydetme hepsi-ya-hiç davranışı korunur |
| 5 | `admin_panel.py`'de `render_ayarlar_tab` kalmaz |
| 6 | Navigasyon kaydı yeni modüle işaret eder |
| 7 | Mevcut ayar testleri geçmeye devam eder |

### 4.3 Risk

| Risk | Sınıf | Önlem |
|---|---|---|
| Mevcut ayar testleri kırılır | 🟡 | Fonksiyon adı taşınırken eski ad `admin_panel.py`'de ince sarmalayıcı olarak bırakılabilir |
| Şifre formu iki yerde kalır | 🔵 | Balondan form kalkar (`ADMIN-UX-PROFILMENU-01`) |

### 4.4 Karar

**Onay:** Bu düzeni uygulayalım mı?

- 🟢 **Evet** → kod yazılır, test eklenir, panel yeniden başlatılır
- 🟡 **Değişiklikle** → hangi bölüm değişsin belirt
- 🔴 **Hayır** → dur

---

### Belgeyi açma

`Ctrl+P` → `UX_AYARLAR_SAYFA` → `Enter` → `Ctrl+Shift+V`
