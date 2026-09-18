# ProfileMenu (Sağ-Alt Profil Popover) — Wireframe / UX / UI (2026-09-18)

> Görev: `ADMIN-UX-PROFILMENU-01` (P0)
> Durum: **wireframe — onay bekliyor. Kod yazılmadı.**
> Bağlı dosyalar (uygulama fazında): `src/company_master/ui/components/profil_menu.py` (yeni), `src/company_master/ui/styles.py`, `app.py`
> Üst doküman: `docs/UX_MENU_AGACI_WIREFRAME_2026-09-18.md` §2 satır 100, §3 satır 137, §4 satır 146

---

## 1. Amaç — tek cümle

Admin kendi hesabıyla ilgili her şeyi (kim olduğu, ayarları, çıkış) **tek bir yerden** yapsın; sol menü iş içeriğine ayrılsın.

---

## 2. Mevcut durum (AS-IS)

Kaynak: `app.py::_hesap_karti_popover()` (satır 369-399)

```
┌─ SIDEBAR (sol) ─────────────┐
│ 🦅 Huginn                   │
│ ─────────────────────────── │
│ 🏠 Ana Kontrol              │
│ 🔍 Keşif                    │
│ 📊 Analiz                   │
│ ⚙️ Sistem                   │
│ 🎛️ Ayarlar      ← menüde!   │
│                             │
│ ─────────────────────────── │
│ 👤 admin@huginn.local   ▾   │ ← SOL-ALT, emoji ikon
└─────────────────────────────┘
        │ tıkla
        ▼
   ┌──────────────────────────┐
   │ Rol: admin               │
   │ [Şifre Değiştir][Çıkış]  │ ← 2 buton yan yana
   └──────────────────────────┘
```

### Tespit edilen 5 problem

| # | Problem | Sınıf |
|---|---------|-------|
| 1 | Popover **sol-altta**; sektör standardı (Linear, Vercel, Stripe, Notion) sağ-alt veya sağ-üst | 🟡 |
| 2 | İkon **emoji 👤** — tema/kontrast kontrolü yok, platforma göre farklı çiziliyor | 🟡 |
| 3 | `Şifre Değiştir` popover **içinde form açıyor** — popover dar, form taşıyor | 🔴 |
| 4 | `Ayarlar` hem sol menüde hem hesap alanında olmalıydı; şu an **sadece menüde** | 🟡 |
| 5 | Kod `app.py` içinde gömülü — test edilebilir bileşen değil | 🔵 |

Toplam: 1 kırmızı (%20), 3 sarı (%60), 1 mavi (%20).

---

## 3. Hedef (TO-BE)

### 3.1 Kapalı durum

```
┌─ SIDEBAR ───────────────────┐
│ 🦅 Huginn                   │
│ ─────────────────────────── │
│ Ana Kontrol                 │
│ Keşif                       │
│ Analiz                      │
│ Sistem                      │
│                             │  ← Ayarlar menüden KALKTI
│         (boşluk)            │     (ADMIN-UX-MENUTREE-01)
│ ─────────────────────────── │
│              ┌────────────┐ │
│              │ (A) admin ⌄│ │ ← SAĞ-ALT, monokrom avatar
│              └────────────┘ │
└─────────────────────────────┘
```

- `(A)` = baş harf rozeti (avatar). Emoji yok. Tek renk daire + harf.
- Etiket: e-posta yerel kısmı (`admin@huginn.local` → `admin`). 12 karakterden uzunsa kısaltma + tooltip tam adres.

### 3.2 Açık durum

```
   ┌───────────────────────────────┐
   │ (A)  admin@huginn.local       │  ← başlık bloğu
   │      Rol: admin               │
   ├───────────────────────────────┤
   │  Hesap Ayarları            →  │  ← deep-link
   │  Şifre Değiştir            →  │  ← deep-link (aynı sayfa, #sifre)
   ├───────────────────────────────┤
   │  Tema: ● Karanlık ○ Aydınlık  │  ← anında etkili
   ├───────────────────────────────┤
   │  Çıkış Yap                    │  ← tek aksiyon, tehlike rengi
   └───────────────────────────────┘
```

**Kural: popover içinde FORM YOK.** Form gerektiren her şey deep-link ile Ayarlar sayfasına gider. Popover yalnız: kimlik göster + yönlendir + çıkış.

### 3.3 Misafir (token yok) durumu

```
   ┌───────────────────────────────┐
   │ (?)  Misafir                  │
   ├───────────────────────────────┤
   │  Giriş Yap                    │  → AUTH-GATE-01 modalı
   └───────────────────────────────┘
```

---

## 4. Değişim tablosu

| Özellik | AS-IS | TO-BE |
|---------|-------|-------|
| Konum | sol-alt | sağ-alt |
| İkon | emoji 👤 | monokrom baş-harf rozeti |
| Şifre değiştir | popover içinde form | deep-link → Ayarlar sayfası |
| Hesap ayarları | yok | deep-link → Ayarlar sayfası |
| Tema | yalnız Streamlit ayarı | popover içinde 2 tıkla |
| Çıkış | 2 sütunlu buton | tam genişlik, tehlike rengi |
| Kod yeri | `app.py` gömülü | `ui/components/profil_menu.py` |
| Sol menüde Ayarlar | var | yok |

---

## 5. Bileşen sözleşmesi (uygulama fazında yazılacak)

`src/company_master/ui/components/profil_menu.py`

```
profil_menu(
    email: str | None,      # None => misafir
    rol: str = "admin",
    ayarlar_url: str = "/ayarlar",
) -> str | None
```

Dönüş = kullanıcının seçtiği aksiyon anahtarı: `"cikis"` · `"ayarlar"` · `"sifre"` · `"tema"` · `"giris"` · `None`.

**Kritik kural (ADMIN-UX-LOGOUT-01 dersi):** bileşen **state değiştirmez**, sadece seçimi döner. Çıkış işini çağıran taraf (`app.py`) `admin_cikis()` ile yapar. Render fonksiyonu çağırmak aksiyon yürütmez.

---

## 6. Görsel tokenlar

Kaynak: `src/company_master/ui/tokens.py`, enjeksiyon `styles.py::stil_enjekte()` (satır 498)

| Öğe | Token |
|-----|-------|
| Avatar zemin | `RENKLER["yuzey_3"]` |
| Avatar yazı | `RENKLER["metin_1"]` |
| Popover zemin | `RENKLER["yuzey_2"]` |
| Ayraç | `RENKLER["kenar"]` |
| Çıkış yazı | `RENKLER["hata"]` |
| İç boşluk | `BOSLUKLAR["m"]` |
| Köşe | `YARICAPLAR["m"]`, avatar `%50` |
| Gölge | `GOLGELER["m"]` |
| Geçiş | `GECISLER["hizli"]` |

Yeni renk **eklenmez**; mevcut token seti yeter.

---

## 7. Erişilebilirlik (kabul kriteri)

| Kriter | Hedef |
|--------|-------|
| Sekme sırası | `topbar → sidebar → içerik → profil popover` (menü ağacı §4 ile aynı) |
| Klavye | `Enter`/`Space` açar, `Esc` kapatır, `↑↓` öğeler arası |
| Kontrast | metin/zemin ≥ 4.5:1 — karanlık **ve** aydınlık temada |
| Dokunma alanı | her satır ≥ 40px yükseklik |
| Ekran okuyucu | avatar `aria-label="Hesap menüsü, admin@huginn.local"` |
| Renk tek başına | çıkış yalnız renkle değil, **metinle** de belli |

---

## 8. Bağımlılıklar 🔴

| Bağımlılık | Görev | Neden |
|-----------|-------|-------|
| Ayarlar sayfası var olmalı | `ADMIN-UX-AYARLAR-SAYFA-01` (P1) | deep-link hedefi yoksa menü ölü bağlantı olur |
| Ayarlar sekmesi menüden kalkmalı | `ADMIN-UX-MENUTREE-01` (P1) | aynı şey iki yerde durursa IA bozulur |

**Sonuç:** bu P0 görev, iki P1 göreve bağımlı. KAHİN onayıyla uygulama sırası:

1. `ADMIN-UX-AYARLAR-SAYFA-01` — hedef sayfa oluşur
2. `ADMIN-UX-MENUTREE-01` — Ayarlar menüden kalkar
3. `ADMIN-UX-PROFILMENU-01` — popover bağlanır

---

## 9. Kabul kriterleri (test edilecek)

| # | Kriter | Test tipi |
|---|--------|-----------|
| 1 | `profil_menu()` state mutasyonu yapmaz, yalnız anahtar döner | AST + birim |
| 2 | Popover içinde `st.form` / `st.text_input` yok | AST |
| 3 | Misafir durumunda yalnız `giris` seçeneği | birim |
| 4 | Admin durumunda 4 seçenek (ayarlar, sifre, tema, cikis) | birim |
| 5 | `app.py` içinde `_hesap_karti_popover` kalmaz, bileşen çağrılır | AST |
| 6 | `admin_cikis()` çağrısı korunur (`render_admin_cikis` değil) | AST — mevcut regresyon testi |
| 7 | `ayarlar` kaydı `SECTIONS`'ta sidebar'da görünmez | birim |

---

## 10. KAHİN'e özet

| Konu | Durum |
|------|-------|
| Ne değişiyor | Hesap menüsü sol-alttan sağ-alta taşınıyor, sadeleşiyor |
| Kullanıcıya faydası | Hesapla ilgili her şey tek yerde; sol menü %17 daha kısa (6→5 üst öğe) |
| Risk | 🟢 Düşük — yalnız görsel + yönlendirme; iş mantığı değişmiyor |
| Blokaj | 🔴 Ayarlar sayfası henüz yok; önce o yapılmalı |
| Kod yazıldı mı | ❌ Hayır — bu doküman onay içindir |
| Sonraki adım | Onay → Ayarlar sayfası → menü ağacı → ProfileMenu |
