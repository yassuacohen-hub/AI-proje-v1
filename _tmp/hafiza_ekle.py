# -*- coding: utf-8 -*-
"""KALDIĞIM YER bloğunun başına yeni konum satiri ekle (D-219: tek blok, uzerine yazilir)."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"Huginn Data Insights/ihsan_project_context.md"
with open(P, encoding="utf-8") as f:
    lines = f.readlines()

YENI = ("- **Konum (2026-10-14 17:25 — TESLİM DENETİMİ KIRMIZI: 12 GÖREV GERİ ÇEKİLDİ + KARAR (AGENTS.md) done=commit+kanıt+teslim kuyruğu + BİLO BELGE PAKETİ):** "
 "PO 'yasu her şeyi yaptım diyor, teslim al' + 'chatten uyarı yap, yaptırım uygula' dedi. "
 "Denetim (TÜM ajanlar, son 3 gün done, dosya-varlık taraması `_tmp/tum_ajan_denetim.py`): 10 şüpheli + 5 rollout kanıtsız. "
 "**Sonuç: yasu 9 + utku 3 görev done→aktif geri çekildi.** "
 "yasu 5 rollout (VDS-DOCKER/SPACESHIP-DNS/KONG/FIRMAARAMA-SEARCH/ODEME): kanıt dosyaları YOK, odeme.py+test_odeme.py HİÇ yazılmamış, page.tsx sadece statik link, kong.yml örnek IP'de. "
 "yasu 4 eski (RAPIDAPI-OSINT/MUSTERI-ODEME-AYAR/OSB-MASTER-0060/V1-NETWORK-REPORT) + utku 3 (ADMIN-DENETIM-ALTYAPI/PAKET-ROZET/OZELLIK-MATRISI-SIM): dosyalar commit'lenmemişken kök temizlik betiği _ARSIV'e sürüklemiş — canlı ağaçta YOK (0060 göçü mersis, OSB göçü hiç yok). "
 "**Karar AGENTS.md sonuna yazıldı (dosya D-355 sonrasi): done = (a) dosya canlı ağaçta commit'li + (b) kanit alani dolu + (c) gorev_kutusu teslim kuyruğundan geçmiş; eksikse orkestratör tek taraflı aktife çeker; _ARSIV'den dosya göstermek KANIT DEĞİL; watchdog done+dosya-eksik=şüpheli-done sayar, 24 saat kanıtsız→otomatik düşürme+PO'ya isimli rapor.** "
 "Chat: yasu ve utku'ya kritik uyarı (TESLIM-KURALI) + yasu'ya ROLLOUT-DENETIM-RED; bilo'ya ALTYAPI-BILO-BASLAT. "
 "**Bilo eksik belgeleri tamam:** `agent_bilo/GUVENLIK_OZET_BILO.md` (sanitize — gerçek IP'li, parola/IBAN YOK; asıl guvenlik ozet.md IBAN+parola icerdiğinden repoya KONMADI) + `agent_bilo/altyapi_sablonlari/{docker-compose.yml,kong.yml,pg_hba.conf}` (193.111.78.200 / 141.98.51.65, parolalar ${ENV}); BASLANGIC_PROMPT okuma sirasi 4. madde sanitize özetе yönledi. "
 "**Commits:** 96c6744d (5 red + Bilo paketi, pre-commit 45/45, push; Bilo f24f418f ile non-ff→rebase+stash temiz) → bu tur (7 red + karar + hafiza). git show ile geri-okundu. "
 "**Tuzaklar:** kilit mandali `set HUGINN_AJAN=ihsan` ister; yasu kilidindeki dosyayi stage etme (git restore --staged); commit mesajinda karar no YASAK; karar_no --al ile sonraki numara tahsisli. "
 "**Güzel haber:** Bilo kendi commit'ini atti — canlı çalışıyor. "
 "**ŞİMDİ:** yasu/utku kanıtlı yeniden teslim yaparsa onayla; 24 saat sessizlikte PO'ya kapasite raporu + görev devri (Bilo/utku). PO onaylı SK02 canlı doğrulama hâlâ sırada.\n")

for i, ln in enumerate(lines):
    if ln.startswith("- **Konum (2026-10-14 15:15"):
        lines.insert(i, YENI)
        break
else:
    print("ANCHOR BULUNAMADI"); sys.exit(1)

with open(P, "w", encoding="utf-8", newline="") as f:
    f.writelines(lines)
print("EKLENDI. Toplam satir:", len(lines))
