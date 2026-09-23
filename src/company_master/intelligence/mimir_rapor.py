# -*- coding: utf-8 -*-
"""MIMIR Seviye 1 Architect Rapor Yazma Otomasyonu (D-190).

Görev durum=done + mod=architect → otomatik rapor yazma.
Zero insan müdahalesi tasarım aşamasında.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from company_master.orchestrator.task_board import gorev_getir

# STATE_DIR: data/orchestrator dizini (task_board.py'den)
_ROOT = Path(__file__).resolve().parents[3]
STATE_DIR = _ROOT / "data" / "orchestrator"


class MimirRaporYazici:
    """MIMIR architect raporlarını otomatik yazar (D-190).
    
    Rapor template:
    - Başlık: Görev özeti
    - Tarih: Report timestamp
    - Sahip: MIMIR
    - Görev bilgisi: task_id, mod, atanan ajan
    - Bulgular: Boş bölüm (review aşamasında insan doldurur)
    """

    RAPOR_DIR = STATE_DIR / "raporlar"
    
    def rapor_yazmayi_tetikle(self, task_id: str) -> bool:
        """Task durum=done + mod=architect ise rapor yaz.
        
        Args:
            task_id: Görev kimliği
            
        Returns:
            True = rapor yazıldı, False = yazılmadı (task bulunamadı/mod yanlış/hata)
        """
        try:
            gorev = gorev_getir(task_id)
            if not gorev:
                return False
            
            # Mod kontrolü: architect olmalı
            if gorev.get("mod") != "architect":
                return False
            
            # Rapor hazırla
            icerik = self._rapor_hazirla(gorev)
            
            # Dosyaya yaz
            rapor_yolu = self._rapor_dosyasini_yaz(task_id, icerik)
            
            return bool(rapor_yolu)
        except Exception:
            return False

    def _rapor_hazirla(self, gorev: dict) -> str:
        """Rapor markdown içeriğini oluştur.
        
        Args:
            gorev: Task board'dan okunan görev dict'i
            
        Returns:
            Markdown formatında rapor metni
        """
        task_id = gorev.get("task_id", "?")
        baslik = gorev.get("baslik", "Başlık yok")
        sahip = gorev.get("sahip", "?")
        tarih_iso = gorev.get("basla", datetime.now().isoformat())
        
        # ISO tarihi kısalt (YYYY-MM-DD HH:MM)
        try:
            dt = datetime.fromisoformat(tarih_iso)
            tarih_kisa = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            tarih_kisa = tarih_iso[:19]
        
        # Brief oku (varsa)
        brief_dosya = self._brif_dosya_bul(task_id)
        brief_icerik = ""
        if brief_dosya:
            brief_icerik = self._dosya_oku(brief_dosya)
            # İlk 500 karakteri al
            if len(brief_icerik) > 500:
                brief_icerik = brief_icerik[:500] + "\n\n(... kısaltıldı)"
        
        # Rapor template
        rapor = f"""# Architect Raporu: {task_id}

**Görev:** {baslik}

**Rapor Tarihi:** {tarih_kisa}  
**Rapor Sahibi:** MIMIR (Seviye 1 - Architect)  
**Atanan Ajan:** {sahip}

---

## Görev Özeti

Görev ID: `{task_id}`

Mod: architect

Atanan: {sahip}

---

## Brief Özeti (Kaynak)

"""
        if brief_icerik:
            rapor += f"""```
{brief_icerik}
```

"""
        else:
            rapor += """Brief bulunamadı.

"""
        
        rapor += """---

## Bulgular

(Bu bölüm insan review aşamasında doldurulacaktır.)

---

*MIMIR tarafından otomatik oluşturuldu (D-190 Architect Rapor Otomasyonu)*
"""
        return rapor

    def _rapor_dosyasini_yaz(self, task_id: str, icerik: str) -> Optional[Path]:
        """Raporu dosyaya yaz (D-57/D-60 uyumlu adlandırma).
        
        Dosya adı: {TASK_ID}_rapor_{TARIH}_mimir.md
        
        Args:
            task_id: Görev kimliği
            icerik: Rapor markdown metni
            
        Returns:
            Yazılan dosyanın yolu, ya da hata ise None
        """
        try:
            # Rapor dizini oluştur
            self.RAPOR_DIR.mkdir(parents=True, exist_ok=True)
            
            # Tarih: YYYY-MM-DD format
            tarih = datetime.now().strftime("%Y-%m-%d")
            
            # Dosya adı: {TASK_ID}_rapor_{TARIH}_mimir.md
            dosya_adi = f"{task_id}_rapor_{tarih}_mimir.md"
            dosya_yolu = self.RAPOR_DIR / dosya_adi
            
            # Yaz
            dosya_yolu.write_text(icerik, encoding="utf-8")
            
            return dosya_yolu
        except Exception:
            return None

    def _brif_dosya_bul(self, task_id: str) -> Optional[Path]:
        """Brief dosyasını bul.
        
        Arama sırası:
        1. plans/{TASK_ID}_brif.md (yeni konum, D-189 uyumlu)
        2. plans/brief_{AJAN_KISA}_{TASK_ID}.md (eski konum)
        
        Args:
            task_id: Görev kimliği
            
        Returns:
            Brief dosyasının yolu, ya da None
        """
        # D-189 yeni format: plans/{TASK_ID}_brif.md
        yeni_format = (self.RAPOR_DIR.parent.parent.parent / "plans") / f"{task_id}_brif.md"
        if yeni_format.exists():
            return yeni_format
        
        # Eski format: plans/brief_{AJAN}_{TASK_ID}.md
        plans_dir = self.RAPOR_DIR.parent.parent.parent / "plans"
        if plans_dir.exists():
            for brief_dosya in plans_dir.glob(f"brief_*_{task_id}.md"):
                return brief_dosya
        
        return None

    def _dosya_oku(self, yol: Path | str) -> str:
        """Dosyayı oku.
        
        Args:
            yol: Dosya yolu
            
        Returns:
            Dosya içeriği (UTF-8), ya da boş string (hata)
        """
        try:
            return Path(yol).read_text(encoding="utf-8")
        except Exception:
            return ""
