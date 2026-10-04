# ALTYAPI-9ROUTER-MITM-PATCH-01 — Brief (yasu)

**Başlık:** [ALTYAPI] 9router MITM NODE_ENV patch kalıcılığını denetle + clinepass OAuth testi ölç -> bulgu_defteri.md (1s)
**Öncelik:** P2 · **Kit:** `ALTYAPI` (AGENTS.md D-196)
**Kilitli dosya:** `C:/Users/yasin/AppData/Roaming/npm/node_modules/9router/app/.next-cli-build/server/chunks/915.js`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden
`data/orchestrator/bulgu_defteri.md` task-id `DEBUG-9ROUTER-COPILOT-502` altındaki 2 ve 3. kayıtlar bu görevi doğuruyor:
- Kayıt #2 (🟡 dikkat): 915.js spawn env'i hâlâ `NODE_ENV=production` döndürüyor (mtime 25 Eylül, v0.5.86), runtime `server.js`'teki `IS_DEV` buna bağlı, önceki patch doğrulanamadı, `logs/mitm/` boş kaldı.
- Kayıt #3 (🔵 öneri): OAuth test sonuçlarında 8 hesaptan 2'si (clinepass: `yassuacohen@gmail.com`, `muhammeddcan82@gmail.com`) ERROR veriyor, orijinal Copilot 502 şikayetiyle ilişkisi doğrulanmadı.

## Doğrulanacak varsayım
- `915.js` modül `96182` içindeki spawn çağrılarında `env:{...process.env,ROUTER_API_KEY:a,NODE_ENV:"production",MITM_ROUTER_BASE:G}` satırı (iki yerde: Windows `e(process.execPath,[B],...)` branch ve sudo `e("sudo",["-S","-E","sh","-c",c],...)` branch) varsayıldı. Farklıysa **dur**, panoya sorun aç.
- `C:/Users/yasin/AppData/Roaming/9router/runtime/mitm/server.js` içinde `Su=process.env.NODE_ENV==="development"` (IS_DEV) satırı varsayıldı. Yoksa **dur**.
- `<DATA_DIR>/logs/mitm/*.req.json` / `*.res.txt` dump yolu `87777.js` modülündeki `dumpRequest`/`createResponseDumper` fonksiyonlarından geliyor varsayıldı.
- 9router dashboard → Sağlayıcılar → OAuth Test Results ekranında clinepass 2 hesabının ERROR durumda olduğu varsayıldı (ölçüm anı: bu görevin açıldığı tarih). Farklıysa **dur**, panoya sorun aç.

## Adımlar
1. `915.js`'teki her iki spawn çağrısının `env` objesine `NODE_ENV:"development",DEBUG_MITM:"1"` ekle (mevcut `NODE_ENV:"production"` değerini değiştir).
2. 9router'ı yeniden başlat (tray restart veya `taskkill` + yeniden aç).
3. Copilot/Antigravity üzerinden gerçek bir istek gönder; `logs/mitm/` klasöründe yeni dump dosyası oluştuğunu dosya adı + mtime ile kanıtla.
4. 9router dashboard → OAuth Providers → Test Results'ı yeniden çalıştır; clinepass 2 hesabın (`yassuacohen@gmail.com`, `muhammeddcan82@gmail.com`) durumunu kontrol et. ERROR hâlâ varsa bu hesapların orijinal Copilot 502 şikayetiyle bağlantısını (aynı hesap Copilot bağlantısında kullanılıyor mu) belirle.

## Kabul kriteri
- [ ] `logs/mitm/` içinde adımdan sonra oluşan dump dosyasının mtime kanıtı var.
- [ ] clinepass 2 hesabın yeni test sonucu (OK/ERROR) ve Copilot 502 ile ilişkisi netleştirildi.
- [ ] Sonuç `bulgu_defteri.py ekle` ile `DEBUG-9ROUTER-COPILOT-502` task-id'sine kaydedildi (kanıtlı).

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** `hubs/ADMIN_DASHBOARD_HUB.md` dosyasının "Kapanan işler" bölümüne `ALTYAPI-9ROUTER-MITM-PATCH-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**, brifi yeniden okuyup beklemek değil:

- Brifteki bir varsayım kodda tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- Bir adım tıkandıysa → sorun aç, **sonraki adıma geç**, zinciri durdurma.
- @mention aldıysan → P2 15-30 dk içinde cevap **zorunlu**.

```bash
python scripts/ajan_chat.py ac yasu ALTYAPI-9ROUTER-MITM-PATCH-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id ALTYAPI-9ROUTER-MITM-PATCH-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id ALTYAPI-9ROUTER-MITM-PATCH-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id ALTYAPI-9ROUTER-MITM-PATCH-01 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).** İnsan tetiği bekleme; tek komutla nöbete gir:

```bash
python scripts/gorev_kutusu.py nobet --ajan yasu
```

- Çıkış `0` = **İŞ VAR** (POSTA / SORU / CHAT satırları) → hemen yap: soruya cevap yaz (`chat_gonder.py --kimden yasu`), görevi `al`.
- Çıkış `3` = 60 dk iş gelmedi → ihsan'a kısa rapor yaz, sonra kapat.
- `nobet` dönmeden "bitti" denmez. Döngü: teslim → nobet → iş → teslim → nobet.

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[plans/_brief_sablon]]
