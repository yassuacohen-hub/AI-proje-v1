#!/usr/bin/env python3
"""
API Aktivite Log Testleri — API-ADMIN-AKTIVITE-YAZ-14
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from unittest.mock import MagicMock, patch, Mock


def make_mock_conn():
    """Mock connection that works as context manager."""
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=None)
    return mock_conn


def make_mock_engine(mock_conn):
    """Mock engine that returns mock_conn on connect()."""
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    return mock_engine


def get_params(call_args):
    """Extract params dict from call_args (_Call object)."""
    # call_args.args is a tuple: (sql_clause, params_dict)
    if hasattr(call_args, 'args') and len(call_args.args) >= 2:
        return call_args.args[1]
    # Fallback for tuple-like
    if hasattr(call_args, '__getitem__') and len(call_args) >= 2:
        return call_args[1]
    return {}


def test_aktivite_yaz_basarili():
    """aktivite_yaz basarili yazim testi."""
    from web_app import aktivite_yaz

    mock_conn = make_mock_conn()
    mock_engine = make_mock_engine(mock_conn)

    with patch('web_app.get_engine', return_value=mock_engine):
        aktivite_yaz(
            user_id="test-user",
            olay_tipi="giris",
            detay={"ip": "127.0.0.1"},
            basarili=True,
        )

        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

        # SQL kontrolu
        call_args = mock_conn.execute.call_args
        sql_text = str(call_args.args[0])
        assert "INSERT INTO user_activity_log" in sql_text
        assert "user_id" in sql_text
        assert "olay_tipi" in sql_text
        assert "detay" in sql_text
        assert "basarili" in sql_text
        assert "ip_adresi" in sql_text

        params = get_params(call_args)
        assert params["uid"] == "test-user"
        assert params["tip"] == "giris"
        assert params["ok"] is True

    print("[TEST] aktivite_yaz_basarili: PASSED")


def test_aktivite_yaz_db_hatasi():
    """DB hatasinda sessiz gecis testi (ana akis dusmemeli)."""
    from web_app import aktivite_yaz

    mock_conn = make_mock_conn()
    mock_conn.execute.side_effect = Exception("DB baglanti hatasi")
    mock_engine = make_mock_engine(mock_conn)

    with patch('web_app.get_engine', return_value=mock_engine):
        # Hata firlatmamali, sessizce gecmeli
        aktivite_yaz(
            user_id="test-user",
            olay_tipi="arama",
            detay={"terim": "test"},
            basarili=False,
        )

        # Hata loglanmali ama exception firlatilmamali
        mock_conn.execute.assert_called_once()

    print("[TEST] aktivite_yaz_db_hatasi: PASSED")


def test_aktivite_yaz_request_ip():
    """Request'ten IP alinmali testi."""
    from web_app import aktivite_yaz
    from starlette.requests import Request

    mock_conn = make_mock_conn()
    mock_engine = make_mock_engine(mock_conn)

    with patch('web_app.get_engine', return_value=mock_engine):
        mock_request = Mock(spec=Request)
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.100"

        aktivite_yaz(
            user_id="test-user",
            olay_tipi="ai_kullanim",
            request=mock_request,
        )

        call_args = mock_conn.execute.call_args
        params = get_params(call_args)
        assert params["ip"] == "192.168.1.100"

    print("[TEST] aktivite_yaz_request_ip: PASSED")


def test_aktivite_yaz_no_request():
    """Request None ise IP bos olmali testi."""
    from web_app import aktivite_yaz

    mock_conn = make_mock_conn()
    mock_engine = make_mock_engine(mock_conn)

    with patch('web_app.get_engine', return_value=mock_engine):
        aktivite_yaz(
            user_id="test-user",
            olay_tipi="giris",
            request=None,
        )

        call_args = mock_conn.execute.call_args
        params = get_params(call_args)
        assert params["ip"] is None

    print("[TEST] aktivite_yaz_no_request: PASSED")


def test_aktivite_yaz_detay_json():
    """Detay dict JSON olarak kaydedilmeli testi."""
    from web_app import aktivite_yaz
    import json

    mock_conn = make_mock_conn()
    mock_engine = make_mock_engine(mock_conn)

    with patch('web_app.get_engine', return_value=mock_engine):
        detay = {"terim": "test arama", "sonuc_adedi": 5}
        aktivite_yaz(
            user_id="test-user",
            olay_tipi="arama",
            detay=detay,
        )

        call_args = mock_conn.execute.call_args
        params = get_params(call_args)
        # JSON olarak serilestirilmis olmali
        assert params["detay"] == json.dumps(detay)

    print("[TEST] aktivite_yaz_detay_json: PASSED")


if __name__ == "__main__":
    test_aktivite_yaz_basarili()
    test_aktivite_yaz_db_hatasi()
    test_aktivite_yaz_request_ip()
    test_aktivite_yaz_no_request()
    test_aktivite_yaz_detay_json()
    print("\n[TUM TESTLER GECTI]")
