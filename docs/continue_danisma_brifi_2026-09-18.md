# Continue (Merve) Danışma Brifi — 2026-09-18

> **Bu bir görev değil.** `AGENTS.md` D-49: Merve danışman; dosya yazmaz, görev almaz, komut çalıştırmaz, panoya girmez.
> Aşağıdaki sorulara **yalnız sohbet penceresinde yazılı cevap** beklenir.

## Bağlam

KAHİN (Ürün Sahibi) `docs/UX_AYARLAR_SAYFA_WIREFRAME_2026-09-18.md` belgesini onayladı.
Yeni sayfa yazılacak: `web_dashboard/tabs/admin_kullanici_ayarlari.py` — 3 bölüm: Hesap · Güvenlik · Tercihler.
Şifre değiştirme formu bugün sol-alt popover içinde; sayfaya taşınacak.

## Danışılacak 4 konu

### 1. Streamlit form + deep-link
Sayfa içinde `#sifre` çapasına dışarıdan gelince (profil menüsünden) Streamlit'te
form otomatik odaklanmıyor. Öneri: `st.query_params` + `st.tabs` index seçimi mi,
yoksa tek sayfa akış + `st.markdown` anchor mu? Hangisi daha az rerun üretir?

### 2. Şifre formu iki yerde kalırsa
Geçiş döneminde form hem popover'da hem sayfada bulunacak.
İki `st.form` aynı `key` ile çakışır. Ortak bir `render_sifre_degistir(token, form_key)`
imzası mı, yoksa popover'daki sürümü hemen kaldırmak mı daha az risk?

### 3. Misafir dalı
Misafirde Hesap + Güvenlik bölümleri hiç çizilmeyecek.
`SectionNav` bölüm listesini koşullu kısaltmak anchor tutarlılığını bozar mı?

### 4. Test yaklaşımı
Modül henüz yokken test yazılıyor (cline'a atandı).
AST tabanlı yapısal test mi, `pytest.importorskip` mi daha sağlam?
Mevcut `tests/test_sayfa_iskeleti.py` ve `tests/test_sekme_kapsama.py` desenleriyle uyum önemli.

## Cevap formatı

Her soruya: **tercih + tek cümle gerekçe + varsa risk.** Kod bloğu isteğe bağlı, kısa tutulsun.
