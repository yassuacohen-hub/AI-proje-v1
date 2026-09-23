# -*- coding: utf-8 -*-
"""D-192: Ajan Chat Sistemi — Test Suite."""

import json
from pathlib import Path

import pytest

# Test için sys.path fix
import sys
_KOK = Path(__file__).resolve().parent.parent
if str(_KOK / "src") not in sys.path:
    sys.path.insert(0, str(_KOK / "src"))

from company_master.chat import ac, guncelle, kapat, oku, ozet, bulgula, bulgular_oku


@pytest.fixture
def izole_chat_dir(tmp_path, monkeypatch):
    """Test için izole edilmiş data dizini."""
    data_dir = tmp_path / "data" / "orchestrator"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CHAT_DATA_DIR", str(data_dir))
    return data_dir


class TestAc:
    """ac() — Sorun aç."""
    
    def test_ac_basit_kayit(self, izole_chat_dir):
        """Basit sorun kaydı."""
        satir = ac("ihsan", "UI-01", "Button hover eksik", data_dir=izole_chat_dir)
        
        assert satir["ajan"] == "ihsan"
        assert satir["task_id"] == "UI-01"
        assert satir["sorun"] == "Button hover eksik"
        assert satir["durum"] == "acik"
        assert "timestamp" in satir
    
    def test_ac_cozum_onerileri_ile(self, izole_chat_dir):
        """Çözüm önerisi ile sorun aç."""
        satir = ac(
            "utku", "API-02", "Rate limit aşılıyor",
            cozum="Cache ekle",
            data_dir=izole_chat_dir
        )
        
        assert satir["cozum"] == "Cache ekle"
    
    def test_ac_task_id_normalizasyon(self, izole_chat_dir):
        """task_id büyük harfe çevrilsin."""
        satir = ac("salih", "ui-03", "Test", data_dir=izole_chat_dir)
        assert satir["task_id"] == "UI-03"
    
    def test_ac_ajan_normalizasyon(self, izole_chat_dir):
        """Ajan adı kanonik."""
        satir = ac("IHSAN", "UI-01", "Test", data_dir=izole_chat_dir)
        assert satir["ajan"] == "ihsan"


class TestGuncelle:
    """guncelle() — Çözümü güncelle."""
    
    def test_guncelle_basit(self, izole_chat_dir):
        """Sorunuçözüm önerisi ekle."""
        # 1. Sorun aç
        ac("ihsan", "UI-01", "Sorun 1", data_dir=izole_chat_dir)
        
        # 2. Güncelle
        satir = guncelle(
            "UI-01", 0,
            cozum_guncel="Çözüm 1",
            durum="cokundurmus",
            data_dir=izole_chat_dir
        )
        
        assert satir is not None
        assert satir["cozum"] == "Çözüm 1"
        assert satir["durum"] == "cokundurmus"
    
    def test_guncelle_bulunamayan_sorun(self, izole_chat_dir):
        """Var olmayan sorun None dönsün."""
        satir = guncelle("NONEXIST", 0, data_dir=izole_chat_dir)
        assert satir is None


class TestKapat:
    """kapat() — Sorunukapalı işaretle."""
    
    def test_kapat_basit(self, izole_chat_dir):
        """Sorunukapalı işaretle."""
        ac("ihsan", "UI-01", "Sorun", data_dir=izole_chat_dir)
        satir = kapat("UI-01", 0, karar="Çözüldü", data_dir=izole_chat_dir)
        
        assert satir is not None
        assert satir["durum"] == "cozuldu"


class TestOku:
    """oku() — Sorunları oku."""
    
    def test_oku_tum_sorunlar(self, izole_chat_dir):
        """Tüm sorunları oku."""
        ac("ihsan", "UI-01", "Sorun 1", data_dir=izole_chat_dir)
        ac("utku", "UI-02", "Sorun 2", data_dir=izole_chat_dir)
        
        satirlar = oku(data_dir=izole_chat_dir)
        assert len(satirlar) == 2
    
    def test_oku_task_id_filtresi(self, izole_chat_dir):
        """Belirli task_id filtrele."""
        ac("ihsan", "UI-01", "Sorun 1", data_dir=izole_chat_dir)
        ac("utku", "UI-02", "Sorun 2", data_dir=izole_chat_dir)
        
        satirlar = oku(task_id="UI-01", data_dir=izole_chat_dir)
        assert len(satirlar) == 1
        assert satirlar[0]["task_id"] == "UI-01"
    
    def test_oku_son_n_satir(self, izole_chat_dir):
        """Son N satırı al."""
        for i in range(5):
            ac("ihsan", f"UI-{i:02d}", f"Sorun {i}", data_dir=izole_chat_dir)
        
        satirlar = oku(son=3, data_dir=izole_chat_dir)
        assert len(satirlar) == 3


class TestOzet:
    """ozet() — Özetini göster."""
    
    def test_ozet_durum_filtresi(self, izole_chat_dir):
        """Durum başına sayı."""
        ac("ihsan", "UI-01", "Sorun 1", data_dir=izole_chat_dir)
        ac("ihsan", "UI-02", "Sorun 2", data_dir=izole_chat_dir)
        guncelle("UI-01", 0, durum="cokundurmus", data_dir=izole_chat_dir)
        
        acik = ozet("acik", data_dir=izole_chat_dir)
        cokundurmus = ozet("cokundurmus", data_dir=izole_chat_dir)
        
        assert len(acik) == 1
        assert len(cokundurmus) == 1


class TestBulgula:
    """bulgula() — Tasarım eleştirisi."""
    
    def test_bulgula_basit_kayit(self, izole_chat_dir):
        """Eleştiri kaydı."""
        satir = bulgula(
            "D-192",
            "Font tutarsız",
            link="data/design.md",
            data_dir=izole_chat_dir
        )
        
        assert satir["konu"] == "D-192"
        assert satir["bulgu"] == "Font tutarsız"
        assert satir["link"] == "data/design.md"
    
    def test_bulgular_oku_filtre(self, izole_chat_dir):
        """Eleştiri filtrele."""
        bulgula("D-192", "Bulgu 1", data_dir=izole_chat_dir)
        bulgula("D-190", "Bulgu 2", data_dir=izole_chat_dir)
        
        bulgular = bulgular_oku(konu="D-192", data_dir=izole_chat_dir)
        assert len(bulgular) == 1


class TestConcurrency:
    """Eşzamanlılık — Lock mekanizması."""
    
    def test_concurrent_append(self, izole_chat_dir):
        """Eşzamanlı append güvenli mi."""
        import threading
        
        results = []
        
        def worker(idx):
            try:
                ac(f"ajan{idx}", f"TASK-{idx}", f"Sorun {idx}", data_dir=izole_chat_dir)
                results.append(True)
            except Exception:
                results.append(False)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Tüm işlemler başarılı
        assert all(results)
        
        # 5 satır kaydedildi
        satirlar = oku(data_dir=izole_chat_dir)
        assert len(satirlar) == 5


class TestIntegration:
    """Entegrasyon testleri."""
    
    def test_tam_akis(self, izole_chat_dir):
        """Tam sorun yaşam döngüsü."""
        # 1. Sorun aç
        ac("ihsan", "UI-01", "Button eksik", cozum="Düzelt", data_dir=izole_chat_dir)
        
        # 2. Özetini kontrol
        acik = ozet("acik", data_dir=izole_chat_dir)
        assert len(acik) == 1
        
        # 3. Çözüm önerisi güncelle
        guncelle("UI-01", 0, cozum_guncel="PR gönder", durum="cokundurmus", data_dir=izole_chat_dir)
        
        # 4. Kapalı işaretle
        kapat("UI-01", 0, karar="Merged", data_dir=izole_chat_dir)
        
        # 5. Çözüldü sayısını kontrol
        cozuldu = ozet("cozuldu", data_dir=izole_chat_dir)
        assert len(cozuldu) == 1
    
    def test_mockup_orkestrator_workflow(self, izole_chat_dir):
        """Orkestratör iş akışı simülasyonu."""
        # İhsan 3 sorun bildirir
        ac("ihsan", "UI-01", "Button hover", data_dir=izole_chat_dir)
        ac("ihsan", "API-02", "Rate limit", data_dir=izole_chat_dir)
        ac("ihsan", "DB-03", "Index yok", data_dir=izole_chat_dir)
        
        # Orkestratör bunu alır ve eleştiri kaydı yapması gerekiyor
        bulgula("Ajan Chat", "3 sorun açıldı", data_dir=izole_chat_dir)
        
        # Özeti kontrol
        acik = ozet("acik", data_dir=izole_chat_dir)
        assert len(acik) == 3
        
        # 1 sorun üzerinde çalışılıyor
        guncelle("UI-01", 0, cozum_guncel="PR açıldı", durum="cokundurmus", data_dir=izole_chat_dir)
        
        # 2 sorun çözüldü
        kapat("API-02", 0, data_dir=izole_chat_dir)
        kapat("DB-03", 0, data_dir=izole_chat_dir)
        
        # Özeti kontrol
        cokundurmus = ozet("cokundurmus", data_dir=izole_chat_dir)
        cozuldu = ozet("cozuldu", data_dir=izole_chat_dir)
        
        assert len(cokundurmus) == 1
        assert len(cozuldu) == 2
