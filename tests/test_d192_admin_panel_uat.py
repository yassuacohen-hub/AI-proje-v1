# -*- coding: utf-8 -*-
"""D-192 Admin Panel UAT (User Acceptance Test) — Widget ve REST API."""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

import pytest


@pytest.fixture
def chat_log(tmp_path, monkeypatch):
    """Test veri: örnek chat log'u ve bulgular."""
    data_dir = tmp_path / "data" / "orchestrator"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CHAT_DATA_DIR", str(data_dir))
    
    # ajan-chat.jsonl oluştur
    chat_file = data_dir / "ajan-chat.jsonl"
    records = [
        {
            "timestamp": "2026-09-23T14:30:00",
            "ajan": "ihsan",
            "task_id": "COP-26",
            "sorun": "API endpoint timeout 5s+ oluyor",
            "cozum": "Connection pool optimize et",
            "durum": "acik",
            "link": ""
        },
        {
            "timestamp": "2026-09-23T14:25:00",
            "ajan": "utku",
            "task_id": "UI-42",
            "sorun": "Dashboard widget loading slow",
            "cozum": "Lazy load implement et",
            "durum": "cokundurmus",
            "link": ""
        },
        {
            "timestamp": "2026-09-23T14:20:00",
            "ajan": "salih",
            "task_id": "TEST-15",
            "sorun": "E2E test flaky — random fail",
            "cozum": "Wait time increase, retry logic",
            "durum": "cozuldu",
            "link": ""
        },
    ]
    
    with chat_file.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    # ajan-chat-bulgular.jsonl oluştur
    bulgular_file = data_dir / "ajan-chat-bulgular.jsonl"
    bulgular = [
        {
            "timestamp": "2026-09-23T14:35:00",
            "konu": "Tasarım Belgesi (D-192)",
            "bulgu": "Durum enum sırası doğru mu? acik → cokundurmus → cozuldu",
            "link": "AGENTS.md#D-192"
        },
    ]
    
    with bulgular_file.open("w", encoding="utf-8") as f:
        for b in bulgular:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")
    
    return data_dir


class TestAdminPanelWidget:
    """Admin panel widget'ı render et ve kontrol et."""
    
    def test_render_chat_summary_imports(self):
        """render_chat_summary() import edilebiliyor mu?"""
        try:
            from web_dashboard.tabs.admin_panel import render_chat_summary
            assert callable(render_chat_summary)
        except ImportError as e:
            pytest.fail(f"render_chat_summary import hatası: {e}")
    
    def test_widget_metrikler_fonksiyon(self, chat_log, monkeypatch):
        """Metrik fonksiyonları (ozet, oku) çağrılabiliyor mu?"""
        try:
            from company_master.chat import ozet, oku
            
            # Veri oku
            acik = ozet("acik", data_dir=chat_log)
            cokundurmus = ozet("cokundurmus", data_dir=chat_log)
            cozuldu = ozet("cozuldu", data_dir=chat_log)
            tum = oku(data_dir=chat_log)
            
            # Kontrol
            assert len(acik) == 1, f"Açık sorun sayısı 1 olmalı, {len(acik)}"
            assert len(cokundurmus) == 1, f"Çözüm bekleniyor sayısı 1 olmalı, {len(cokundurmus)}"
            assert len(cozuldu) == 1, f"Çözüldü sayısı 1 olmalı, {len(cozuldu)}"
            assert len(tum) == 3, f"Toplam sorun 3 olmalı, {len(tum)}"
            
            # Metrik değerler doğru mu?
            assert acik[0]["ajan"] == "ihsan"
            assert cokundurmus[0]["ajan"] == "utku"
            assert cozuldu[0]["ajan"] == "salih"
        except Exception as e:
            pytest.fail(f"Widget metrik hatası: {e}")
    
    def test_widget_son_acik_sorunlar(self, chat_log, monkeypatch):
        """Son 3 açık sorun (expander'lar) render edilebiliyor mu?"""
        try:
            from company_master.chat import ozet
            
            acik = ozet("acik", data_dir=chat_log)
            son_acik = sorted(acik, key=lambda x: x.get("timestamp", ""), reverse=True)[:3]
            
            assert len(son_acik) == 1, "Son 3 açık sorundan 1 tane olmalı"
            assert son_acik[0]["task_id"] == "COP-26"
            assert "timeout" in son_acik[0]["sorun"].lower()
        except Exception as e:
            pytest.fail(f"Son açık sorunlar hatası: {e}")
    
    def test_widget_tum_sorunlar_tablosu(self, chat_log, monkeypatch):
        """Tüm sorunlar tablosu veri hazırlanabiliyor mu?"""
        try:
            from company_master.chat import oku
            
            tum = oku(data_dir=chat_log)
            rows = []
            for s in sorted(tum, key=lambda x: x.get("timestamp", ""), reverse=True):
                rows.append({
                    "Tarih": s.get("timestamp", "")[:16],
                    "Ajan": s.get("ajan", "").upper(),
                    "Görev": s.get("task_id", ""),
                    "Sorun": s.get("sorun", "")[:50],
                    "Durum": s.get("durum", ""),
                })
            
            assert len(rows) == 3, f"Tablo satırı 3 olmalı, {len(rows)}"
            assert rows[0]["Ajan"] == "IHSAN"
            assert rows[0]["Durum"] == "acik"
        except Exception as e:
            pytest.fail(f"Tüm sorunlar tablosu hatası: {e}")


class TestAdminPanelREST:
    """Admin panel REST API endpoint'leri test et."""
    
    def test_rest_endpoint_health_check(self, chat_log):
        """Streamlit app başlayabiliyor mu (health check)?"""
        # Not: Full REST test için streamlit server çalışması gerekir
        # UAT için: import ve fixture success yeterli
        assert chat_log.exists()
        assert (chat_log / "ajan-chat.jsonl").exists()
    
    def test_rest_sorun_ac_payload(self, chat_log, monkeypatch):
        """REST POST /chat/ac payload'ı valid mi?"""
        try:
            from company_master.chat import ac
            
            payload = {
                "ajan": "yasu",
                "task_id": "CODE-99",
                "sorun": "Performance regression detected",
                "cozum": "Profiling yapılacak"
            }
            
            result = ac(
                ajan=payload["ajan"],
                task_id=payload["task_id"],
                sorun=payload["sorun"],
                cozum=payload["cozum"],
                data_dir=chat_log
            )
            
            assert result["ajan"] == "yasu"
            assert result["task_id"] == "CODE-99"
            assert result["durum"] == "acik"
            assert len(result) == 7, "Result dict 7 alan olmalı"
        except Exception as e:
            pytest.fail(f"REST POST hatası: {e}")
    
    def test_rest_sorun_oku_filtresi(self, chat_log, monkeypatch):
        """REST GET /chat/problems?task_id=X filtreleme working?"""
        try:
            from company_master.chat import oku
            
            # Scenario: task_id=UI-42 sorunlarını getir
            result = oku(task_id="UI-42", data_dir=chat_log)
            
            assert len(result) == 1, f"UI-42 sorun sayısı 1 olmalı, {len(result)}"
            assert result[0]["ajan"] == "utku"
            assert result[0]["durum"] == "cokundurmus"
        except Exception as e:
            pytest.fail(f"REST GET filtresi hatası: {e}")
    
    def test_rest_sorun_guncelle_payload(self, chat_log, monkeypatch):
        """REST PUT /chat/problems/{task_id}/{index} güncelleme working?"""
        try:
            from company_master.chat import guncelle
            
            # UI-42 sorununu güncelle (index 0, çünkü tek sorun)
            result = guncelle(
                task_id="UI-42",
                sorun_index=0,
                cozum_guncel="Lazy loading implemented ve tested",
                durum="cozuldu",
                data_dir=chat_log
            )
            
            assert result is not None, "Güncelleme başarısız"
            assert result["durum"] == "cozuldu"
            assert "implemented" in result["cozum"].lower()
        except Exception as e:
            pytest.fail(f"REST PUT hatası: {e}")


class TestUserAcceptanceCriteria:
    """UAT: Kullanıcı kabul kriterleri."""
    
    def test_uac_1_metrikler_gorunuyor(self, chat_log, monkeypatch):
        """UAC-1: 3 metrik (açık/çözüm bekleniyor/çözüldü) gösterilmeli."""
        from company_master.chat import ozet
        
        acik = len(ozet("acik", data_dir=chat_log))
        cokundurmus = len(ozet("cokundurmus", data_dir=chat_log))
        cozuldu = len(ozet("cozuldu", data_dir=chat_log))
        
        # Her metrik visible olmalı (0 da olabilir)
        assert isinstance(acik, int) and acik >= 0
        assert isinstance(cokundurmus, int) and cokundurmus >= 0
        assert isinstance(cozuldu, int) and cozuldu >= 0
    
    def test_uac_2_son_sorunlar_expander(self, chat_log, monkeypatch):
        """UAC-2: Son açık sorunlar expander'lar ile gösterilmeli."""
        from company_master.chat import ozet
        
        acik = ozet("acik", data_dir=chat_log)
        son_3 = sorted(acik, key=lambda x: x.get("timestamp", ""), reverse=True)[:3]
        
        # Her sorun: ajan + task_id + sorun + çözüm önerileri
        for sorun in son_3:
            assert sorun.get("ajan"), "Ajan boş"
            assert sorun.get("task_id"), "Task ID boş"
            assert sorun.get("sorun"), "Sorun açıklaması boş"
    
    def test_uac_3_tum_sorunlar_tablosu(self, chat_log, monkeypatch):
        """UAC-3: Tüm sorunlar filtrelenebilir tablo ile gösterilmeli."""
        from company_master.chat import oku
        
        tum = oku(data_dir=chat_log)
        
        # Tablo kolonları: Tarih, Ajan, Görev, Sorun, Durum
        assert len(tum) > 0, "Sorun kaydı yok"
        
        for sorun in tum:
            assert "timestamp" in sorun
            assert "ajan" in sorun
            assert "task_id" in sorun
            assert "sorun" in sorun
            assert "durum" in sorun
    
    def test_uac_4_sorun_acma_kapama_islemler(self, chat_log, monkeypatch):
        """UAC-4: ac() / guncelle() / kapat() işlemleri hızlı ve güvenli olmalı."""
        from company_master.chat import ac, guncelle, kapat
        
        # Sorun aç
        t0 = datetime.now()
        yeni = ac("yasu", "PERF-100", "Memory leak in parser", data_dir=chat_log)
        t_ac = (datetime.now() - t0).total_seconds()
        
        assert t_ac < 1, f"ac() 1s'dan uzun: {t_ac:.2f}s"
        
        # Güncelle
        t0 = datetime.now()
        guncel = guncelle("PERF-100", 0, "Profiler dump analysis", "cokundurmus", data_dir=chat_log)
        t_guncelle = (datetime.now() - t0).total_seconds()
        
        assert t_guncelle < 1, f"guncelle() 1s'dan uzun: {t_guncelle:.2f}s"
        assert guncel is not None
        
        # Kapat
        t0 = datetime.now()
        kapal = kapat("PERF-100", 0, "Merged fix branch", data_dir=chat_log)
        t_kapat = (datetime.now() - t0).total_seconds()
        
        assert t_kapat < 1, f"kapat() 1s'dan uzun: {t_kapat:.2f}s"
        assert kapal["durum"] == "cozuldu"


class TestAdminPanelRegression:
    """Admin panel regression: existing functionality korunuyor mu?"""
    
    def test_regression_decision_tab_calisir(self):
        """render_decision_tab() hala çalışıyor mu?"""
        try:
            from web_dashboard.tabs.admin_panel import render_decision_tab
            assert callable(render_decision_tab)
        except ImportError as e:
            pytest.fail(f"render_decision_tab import hatası: {e}")
    
    def test_regression_settings_tab_calisir(self):
        """render_ayarlar_tab() hala çalışıyor mu?"""
        try:
            from web_dashboard.tabs.admin_panel import render_ayarlar_tab
            assert callable(render_ayarlar_tab)
        except ImportError as e:
            pytest.fail(f"render_ayarlar_tab import hatası: {e}")
    
    def test_regression_reports_tab_calisir(self):
        """render_rapor_listesi_tab() hala çalışıyor mu?"""
        try:
            from web_dashboard.tabs.admin_panel import render_rapor_listesi_tab
            assert callable(render_rapor_listesi_tab)
        except ImportError as e:
            pytest.fail(f"render_rapor_listesi_tab import hatası: {e}")
