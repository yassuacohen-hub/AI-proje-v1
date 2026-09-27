# REV-MVP-KD-01 — Karar Defteri Ekranı İnceleme Raporu

- **İnceleyen:** cline (tarih: 2026-09-15)
- **İncelenen teslim (kilo):** MVP-KD-01 — `web_dashboard/tabs/admin_panel.py` (`render_decision_tab`), `tests/test_admin_panel_tab.py`
- **Karar önerisi:** **DUZELTME GEREKLI (tek madde)** — teslimin kendisi kaliteli ve plan maddeleri birebir uygulanmış; ancak teslim, eski P7-46 kaynak-kural testini kırdı (bkz. B-1). Tek düzeltme sonrası onaya hazır.

## 1. Plan maddeleri (`plans/MVP_ADMIN_minimum_canli.md`) doğrulaması

| # | Plan maddesi | Durum |
|---|---|---|
| 1 | `PageHeader("Karar Defteri", ust_etiket="İş · Yönetim", ikon="📒")` + kısa giriş | ✔ (satır 71-74, `giris=` ile) |
| 2 | Filtre satırı: Karar Veren selectbox ("Hepsi" + benzersiz decider), Etiket multiselect, Ara (title/decision/reason) | ✔ (satır 89-118) |
| 3 | Liste: son 50, en yeni üstte, `st.dataframe` | ✔ (`filtrelenmis[-50:]` + dataframe; `read_decisions(limit=50)` varsayılanı ile uyumlu) |
| 4 | "➕ Yeni karar" form: başlık, karar, gerekçe, etiketler (virgül) → `log_decision(...)`, decider = aktif kullanıcı; success + rerun | ✔ (satır 152-167; imza uyumu teyitli: `log_decision(title, decision, decider, reason, tags)`) |
| 5 | Boş durum `st.info("Henüz karar kaydı yok")` | ✔ (satır 125-127) |

Bonus: zorunlu alan kontrolü (`Başlık`/`Karar` boşsa `st.error`) plan dışı olumlu ek.

## 2. Kabul kapısı sonuçları

| Kapı | Sonuç |
|---|---|
| `pytest tests/ -q --continue-on-collection-errors` | **1 failed, 3317 passed, 3 skipped** — koleksiyon hatası 0; **yeşil şartı kırılıyor (bkz. B-1)** |
| `tests/test_admin_panel_tab.py` + `tests/test_sayfa_iskeleti.py` | **83 passed** (6 admin_panel testi: 2 eski + 4 yeni) |
| `python scripts/kodlama_denetim.py` | **EXIT 0** — temiz |
| Ekran doğrulaması (`streamlit run app.py`) | **HTTP 200** — uygulama çöksüz açılıyor (headless ortam; sekme içi etkileşim statik inceleme + 83 test ile doğrulandı; gerçek tıklama doğrulaması UI'da yapılamadı — ortam kısıtı) |

## 3. Bulgular

| ID | Seviye | Bulgu |
|---|---|---|
| B-1 | **Orta (bloke edici)** | `tests/test_user_settings.py::test_panel_formu_sema_uzerinden_uretir` (P7-46, satır 313) dosya-geneli `kaynak.count("st.selectbox(") <= 1` kuralı; kilo'nun karar-defteri "Karar Veren" selectbox'ı (satır 91, plan maddesi 2 — **meşru ve zorunlu**) sayıyı 2'ye çıkardı → tam regresyon kırmızı. **Kuralın niyeti** (P7-46: ayarlar panelinde elle selectbox yığını yerine şema-döngü) korunarak sayım `_form_degeri`–`render_ayarlar_tab` bölgesiyle sınırlandırılmalı. Önerilen yama: |
| | | ```python\ndef test_panel_formu_sema_uzerinden_uretir():\n    kaynak = _panel_kaynak()\n    assert "for tanim in grup_haritasi[" in kaynak\n    bolge = kaynak[kaynak.index("def _form_degeri"):kaynak.index("def render_ayarlar_tab")]\n    assert bolge.count("st.selectbox(") <= 1\n    assert bolge.count("st.checkbox(") <= 1\n``` |
| D-1 | Bilgi | `decider = aktif_kullanici()` → oturum yoksa fallback **"misafir"** (P7-46 sabiti `MISAFIR_KIMLIK`); plan "yoksa 'admin'" dedi. Davranış makul ve P7-46 ile tutarlı; plan metni ile küçük sapma — roo notu. |
| D-2 | Bilgi | `from scripts.decision_log import ...` namespace-package importu (`scripts/__init__.py` yok); çalışıyor (pytest rootdir repo kökü), klasik paketleşme ileride düşünülebilir. |

## 4. ONAY / RET

**DUZELTME GEREKLI (tek madde B-1).** Önerilen yama uygulandıktan sonra tam regresyon yeşile döner; diğer tüm kapılar yeşil olduğundan yeniden teslimde ek inceleme gerektirmeyecektir.

## BULGU NOTU (kapsam dışı)

Kapsam dışı bug gözlenmedi; `data/orchestrator/REV-MVP-KD-01_bulgular_2026-09-15_cline.md` bu nedenle oluşturulmadı. Not: MVP-KUL-01 (kilo) hâlâ `plan` durumunda; REV-MVP-KUL-01 incelemesi teslim sonrası yapılacak. UI-SIDEBAR-02 `blocked`.
