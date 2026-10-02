# -*- coding: utf-8 -*-
"""ORCH-11: Pano hijyeni + çakışma önleme + blokaj otomasyonu.

Gözlemlenen gerçek hatalar ve bu modülün çözümleri:

1. AYNI DOSYA KAVGASI : ``app.py`` hem roo hem kilo görevinde kilitliydi.
   -> ``guvenli_gorev_ekle()`` çakışan dosyaların kilidini ALMAZ, uyarı üretir.

2. UNUTULMUŞ BLOKAJ : COP-08/09/10, henüz var olmayan dosyaları test ediyordu
   (roo'nun P7-27/31/32 işleri bitmeden). Elle "blocked" işlendi, kimse açmadı.
   -> görevlere ``blokaj: [task_id, ...]`` alanı eklenir; ``pano_bakim()``
      bağımlılık bitince görevi otomatik açar ve ajanın postasına tetik düşer.

3. TAKILI TETİK : trigger dosyasında "teslim" + panoda "done" -> bayat kayıt,
   posta kutusu kirli görünür, ajan "görev yok" sanır.
   -> ``pano_bakim()`` tetik durumlarını pano ile eşitler.

4. ÇİFT KAYIT : COP-11 panoda iki kez vardı.
   -> dedupe: en gelişmiş kayıt (done/blocked > aktif/review > plan) korunur.

5. UNUTULMUŞ AJAN : onay döngüsünde copilot liste dışıydı; teslimleri işlenmedi.
   -> ``AJANLAR`` tek yerde tanımlanır; herkes bu listeyi kullanır.

6. TOKEN MALİYETİ : uzun pano tabloları ajan bağlamını şişirir.
   -> ``ozet_rapor()`` tek satırlık özet; K6 (maks 5 dosya) ve K7 (retry'da
      bağlam %50 daraltma) zaten task_board'da var.

Kullanım:
    python scripts/gorev_kutusu.py bakim          # düzelt + rapor
    python scripts/gorev_kutusu.py bakim --rapor  # sadece rapor (dokunma)
    python scripts/gorev_kutusu.py ozet           # token dostu pano özeti
"""
from __future__ import annotations

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import trigger

# D-60: kanonik adlar Türkçe (ihsan/utku/salih/yasu); tek doğruluk kaynağı trigger.AJANLAR.
# `copilot` dışarıdan gözlemci — görev almaz, listede yok.
AJANLAR = list(trigger.AJANLAR)

# Dedupe'ta hangi durum kazanır (küçük sayı kazanır)
_DURUM_ONCELIK = {"done": 0, "blocked": 1, "review": 2, "aktif": 3, "plan": 4}


def cakisirma_analizi(task_id: str, dosyalar: list[str]) -> dict:
    """Dosyalar başka aktif iş/kilit tarafından tutuluyor mu? (okuma-only)

    Returns:
        {"cakisan": [{"dosya", "tutan", "durum"}], "temiz": [...]}
    """
    kilitler = tb.locklar() if hasattr(tb, "locklar") else tb._read_json(tb.FILE_LOCKS)
    aktif = {
        d: (t["task_id"], t["durum"])
        for t in tb.gorev_listesi()
        if t.get("durum") in ("aktif", "review")
        for d in t.get("dosyalar", [])
    }
    cakisan, temiz = [], []
    for d in dosyalar or []:
        kilit = kilitler.get(d) if isinstance(kilitler, dict) else None
        if kilit and kilit.get("task_id") != task_id:
            cakisan.append({"dosya": d, "tutan": f"kilit:{kilit.get('task_id', '?')}", "durum": "kilitli"})
        elif d in aktif and aktif[d][0] != task_id:
            cakisan.append({"dosya": d, "tutan": aktif[d][0], "durum": aktif[d][1]})
        else:
            temiz.append(d)
    return {"cakisan": cakisan, "temiz": temiz}


def guvenli_gorev_ekle(
    task_id: str,
    baslik: str,
    sahip: str,
    oncelik: str = "P1",
    dosyalar: list[str] | None = None,
    blokaj: list[str] | None = None,
    tetikle: bool = False,
    talimat: str = "",
) -> dict:
    """Çakışma analizli görev oluşturma.

    - Çakışan dosyaların kilidi ALINMAZ (uyarı döner), temizler kilitlenir.
    - ``blokaj`` alanı panoya yazılır; bağımlılık done olunca pano_bakim açar.
    - ``tetikle`` + blokaj yoksa ajanın postasına hemen tetik düşer.
    """
    analiz = cakisirma_analizi(task_id, dosyalar or [])
    uyarilar = [
        f"{c['dosya']} -> {c['tutan']} ({c['durum']}), kilit atlandı"
        for c in analiz["cakisan"]
    ]
    gorev = tb.gorev_ekle(task_id, baslik, sahip, oncelik, dosyalar=analiz["temiz"] or None)
    if blokaj:
        gorev = tb.gorev_guncelle(task_id, blokaj=list(blokaj))
    if talimat:
        # Talimat pano gorevine yazilmazsa blokaj acilirken kayboluyordu.
        gorev = tb.gorev_guncelle(task_id, talimat=talimat, **{"not": talimat})
    if tetikle and not blokaj:
        try:
            trigger.tetik_ekle(task_id, sahip, talimat)
        except trigger.TriggerError:
            pass  # bekleyen tetik zaten var
    return {"gorev": gorev, "uyarilar": uyarilar}

def blokaj_guncelle() -> dict:
    """Blokaj alanına göre görevleri otomatik aç/kapat.

    - Tüm bağımlılıklar done -> görev "plan" olur + ajan postasına tetik düşer.
    - Bağımlılık bekliyor    -> yalnızca "plan" durumdaki görev "blocked" olur
      (canlı "aktif" işe dokunulmaz; yanlış blokaj işi öldürmesin).
    """
    board = tb.gorev_listesi()
    acilan, kapanan = [], []
    for t in board:
        blokaj = t.get("blokaj")
        if not blokaj:
            continue
        durumlar = {d: (tb.gorev_getir(d) or {}).get("durum", "yok") for d in blokaj}
        tamam = all(v == "done" for v in durumlar.values())
        # Blokaj tamam: gorev 'blocked' ise acilir; 'plan' ise (henuz kapanmamis) da acilir.
        # ORCH-13 spam guvenligi: kapisi zaten acilmis goreve her turda tekrar tetik atma.
        if tamam and t["durum"] in ("blocked", "plan") and not t.get("kapisi_acildi"):
            tb.gorev_guncelle(t["task_id"], durum="plan", bitis=None,
                              kapisi_acildi=True,
                              **{"not": f"Blokaj açıldı: {', '.join(blokaj)} done"})
            try:
                taslak = str(t.get("talimat") or t.get("not") or t.get("baslik") or "")[:110]
                trigger.tetik_ekle(
                    t["task_id"], t["sahip"],
                    f"Blokaj açıldı — görevi al. ÖNCE AI proje v1/V10/03_mimari/brifler/00_sentez.md OKU. Görev: {taslak}")
            except trigger.TriggerError:
                pass
            acilan.append(t["task_id"])
        elif not tamam and t["durum"] == "plan":
            bekleyen = [d for d, v in durumlar.items() if v != "done"]
            tb.gorev_guncelle(t["task_id"], durum="blocked",
                              **{"not": f"Blokaj: {', '.join(bekleyen)} bekliyor"})
            kapanan.append(t["task_id"])
    return {"acilan": acilan, "kapanan": kapanan}


def pano_tarama() -> dict:
    """Pano + tetik dosyalarında sorun tarar; DOKUNMAZ, sadece raporlar."""
    board = tb.gorev_listesi()
    gorulen: dict[str, list] = {}
    for t in board:
        gorulen.setdefault(t["task_id"], []).append(t)
    ciftler = {tid: len(v) for tid, v in gorulen.items() if len(v) > 1}

    # D-198: arşiv de mükerrer kapısıdır. Arşiv SALT OKUNUR taranır.
    arsiv_cakisma = []
    for t in board:
        if t["durum"] in tb.KAPALI_DURUMLAR:
            continue
        dosya = tb.arsivde_bul(t["task_id"])
        if dosya:
            arsiv_cakisma.append(f"{t['task_id']} -> {dosya}")

    pano_durum = {t["task_id"]: t["durum"] for t in board}
    takilan = []
    for ajan in AJANLAR:
        for k in trigger._tetikleri_oku(ajan):
            pd = pano_durum.get(k["task_id"])
            if pd in ("done", "blocked") and k["durum"] in ("bekliyor", "alindi", "teslim", "zincir_bekleme"):
                takilan.append(f"{ajan}/{k['task_id']} tetik={k['durum']} pano={pd}")
            elif pd in ("aktif", "review") and k["durum"] == "bekliyor":
                takilan.append(f"{ajan}/{k['task_id']} tetik=bekliyor pano={pd}")

    bloklu = [t["task_id"] for t in board if t["durum"] == "blocked"]
    return {
        "cift_kayit": ciftler,
        "takili_tetik": takilan,
        "blocked": bloklu,
        "arsiv_cakisma": arsiv_cakisma,
    }


def pano_bakim() -> dict:
    """Pano hijyeni: dedupe + tetik eşitleme + bayat zincir + blokaj. Düzeltir."""
    rapor: dict = {"dedupe": 0, "tetik_esit": 0, "zincir": []}
    rapor.update(blokaj_guncelle())

    # 1) Çift kayıt temizle: en gelişmiş kayıt kazanır, eşitlikte son kayıt
    board = tb.gorev_listesi()
    gorulen: dict[str, list[int]] = {}
    for i, t in enumerate(board):
        gorulen.setdefault(t["task_id"], []).append(i)
    silinecek: set[int] = set()
    for indeksler in gorulen.values():
        if len(indeksler) < 2:
            continue
        kazanan = min(indeksler, key=lambda i: (_DURUM_ONCELIK.get(board[i]["durum"], 9), i))
        silinecek |= set(indeksler) - {kazanan}
    if silinecek:
        rapor["dedupe"] = len(silinecek)
        board = [t for i, t in enumerate(board) if i not in silinecek]
        tb._write_json(tb.TASK_BOARD, board)
        tb._md_yaz(board)

    # 2) Tetik <-> pano eşitle (bayat kayıt bırakma)
    pano_durum = {t["task_id"]: t["durum"] for t in tb.gorev_listesi()}
    for ajan in AJANLAR:
        kayitlar = trigger._tetikleri_oku(ajan)
        degisti = False
        for k in kayitlar:
            pd = pano_durum.get(k["task_id"])
            # D-317: KAPALI_DURUMLAR (done/archive/iptal) + blocked hepsi senkronize olur.
            if (pd in tb.KAPALI_DURUMLAR or pd == "blocked") and k["durum"] not in (
                *tb.KAPALI_DURUMLAR, "blocked"
            ):
                k["durum"] = pd
                k.pop("onceki_gorev", None)
                degisti = True
                rapor["tetik_esit"] += 1
            elif k["durum"] == "bekliyor" and pd == "aktif":
                k["durum"] = "alindi"
                degisti = True
                rapor["tetik_esit"] += 1
        if degisti:
            trigger._tetikleri_yaz(kayitlar, ajan)

    # 3) Bayat zincir: önceki done olmuş ama zincir hâlâ bekliyor
    for ajan in AJANLAR:
        for k in trigger._tetikleri_oku(ajan):
            onceki = k.get("onceki_gorev")
            if k["durum"] == "zincir_bekleme" and onceki in pano_durum:
                if pano_durum[onceki] in ("done", "blocked"):
                    sonraki = trigger.zincir_devam_et(onceki, ajan)
                    if sonraki:
                        rapor["zincir"].append(f"{onceki} -> {sonraki['task_id']}")
    return rapor


def ozet_rapor() -> str:
    """Token dostu tek satırlık pano özeti."""
    board = tb.gorev_listesi()
    aktif = [t for t in board if t["durum"] in ("aktif", "review")]
    bloklu = [t for t in board if t["durum"] == "blocked"]
    bekleyen = {a: len(trigger.bekleyen_tetikler(a)) for a in AJANLAR}
    onay = len(trigger.onay_bekleyenler())
    aktif_s = " ".join(f"{t['task_id']}({t['sahip']})" for t in aktif[:6]) or "-"
    bek_s = " ".join(f"{a}={n}" for a, n in bekleyen.items() if n) or "-"
    return (f"AKTIF: {aktif_s} | TETIK: {bek_s} | "
            f"ONAY: {onay} | BLOCKED: {len(bloklu)}")
