import json
from unittest.mock import patch, MagicMock

import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from web_app import app


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "time" in data


class TestKPIEndpoint:
    @patch("web_app.get_engine")
    def test_kpi_returns_expected_fields(self, mock_get_engine, client):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.mappings.return_value.first.return_value = {
            "total": 100,
            "tax": 10,
            "vergi": 20,
            "vkn_either": 30,
            "web": 40,
            "parsel": 5,
            "adres": 60,
            "tel": 70,
            "email": 50,
            "nace": 80,
            "avg_score": 56.54,
        }
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        response = client.get("/api/kpi")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 100
        assert data["avg_score"] == 56.54

    @patch("web_app.get_engine")
    def test_kpi_returns_empty_when_no_data(self, mock_get_engine, client):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.mappings.return_value.first.return_value = None
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        response = client.get("/api/kpi")
        assert response.status_code == 200
        assert response.json() == {}


class TestCompaniesEndpoint:
    @patch("web_app.get_engine")
    def test_companies_returns_list(self, mock_get_engine, client):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.scalar.return_value = 2
        mock_conn.execute.return_value.mappings.return_value.all.return_value = [
            {
                "legal_name": "FIRMA A",
                "trade_name": "A Ticaret",
                "website_domain": "a.com",
                "primary_phone": "0312 111 22 33",
                "primary_email": "a@test.com",
                "tax_number": "1111111111",
                "vergi_no": "1111111111",
                "osb_parsel": "1/1",
                "nace_code": "71.12",
                "data_quality_score": 75.0,
            },
            {
                "legal_name": "FIRMA B",
                "trade_name": "B Ticaret",
                "website_domain": "b.com",
                "primary_phone": "0312 222 33 44",
                "primary_email": "b@test.com",
                "tax_number": "2222222222",
                "vergi_no": "2222222222",
                "osb_parsel": "2/2",
                "nace_code": "72.11",
                "data_quality_score": 85.0,
            },
        ]
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        response = client.get("/api/companies?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["legal_name"] == "FIRMA A"

    @patch("web_app.get_engine")
    def test_companies_search_filters(self, mock_get_engine, client):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.scalar.return_value = 1
        mock_conn.execute.return_value.mappings.return_value.all.return_value = [
            {
                "legal_name": "FIRMA A",
                "trade_name": "A Ticaret",
                "website_domain": "a.com",
                "primary_phone": "0312 111 22 33",
                "primary_email": "a@test.com",
                "tax_number": "1111111111",
                "vergi_no": "1111111111",
                "osb_parsel": "1/1",
                "nace_code": "71.12",
                "data_quality_score": 75.0,
            }
        ]
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        response = client.get("/api/companies?limit=2&search=Firma")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1


class TestDashboardEndpoint:
    def test_dashboard_returns_html(self, client):
        response = client.get("/api/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Huginn" in response.text


class TestStaticFiles:
    def test_css_served(self, client):
        response = client.get("/static/css/style.css")
        assert response.status_code == 200

    def test_js_served(self, client):
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
