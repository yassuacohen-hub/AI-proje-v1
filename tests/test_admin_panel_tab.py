from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from scripts import decision_log
from web_dashboard.tabs import admin_panel


def _mock_streamlit(monkeypatch):
    """Streamlit fonksiyonlarini mock et."""
    monkeypatch.setattr(admin_panel.st, "info", MagicMock())
    monkeypatch.setattr(admin_panel.st, "error", MagicMock())
    monkeypatch.setattr(admin_panel.st, "success", MagicMock())
    monkeypatch.setattr(admin_panel.st, "caption", MagicMock())
    monkeypatch.setattr(admin_panel.st, "dataframe", MagicMock())
    monkeypatch.setattr(admin_panel.st, "selectbox", MagicMock(return_value="Hepsi"))
    monkeypatch.setattr(admin_panel.st, "multiselect", MagicMock(return_value=[]))
    monkeypatch.setattr(admin_panel.st, "text_input", MagicMock(return_value=""))
    monkeypatch.setattr(admin_panel.st, "form_submit_button", MagicMock(return_value=False))
    monkeypatch.setattr(admin_panel.st, "rerun", MagicMock())

    # columns context manager
    mock_col = MagicMock()
    mock_col.__enter__ = MagicMock(return_value=mock_col)
    mock_col.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr(admin_panel.st, "columns", lambda n: [mock_col] * n)

    # form context manager
    mock_form = MagicMock()
    mock_form.__enter__ = MagicMock(return_value=None)
    mock_form.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr(admin_panel.st, "form", MagicMock(return_value=mock_form))


def test_render_decision_tab_shows_empty_state(monkeypatch):
    _mock_streamlit(monkeypatch)
    info = admin_panel.st.info

    admin_panel.render_decision_tab([])

    info.assert_called_once_with("Henüz karar kaydı yok — ilk kararı aşağıdaki formdan ekleyin.")


def test_render_decision_tab_renders_populated_log(monkeypatch):
    _mock_streamlit(monkeypatch)
    dataframe = admin_panel.st.dataframe
    caption = admin_panel.st.caption

    decisions = [
        {
            "ts": "2026-09-13T12:00:00+00:00",
            "title": "Test kararı",
            "decision": "accepted",
            "decider": "copilot",
            "reason": "Test gerekçesi",
            "tags": ["test", "audit"],
        }
    ]

    admin_panel.render_decision_tab(decisions)

    rendered = dataframe.call_args.args[0]
    assert len(rendered) == 1
    assert rendered.iloc[0]["Baslik"] == "Test kararı"
    assert rendered.iloc[0]["Etiketler"] == "test, audit"
    caption.assert_called_once()


def test_render_decision_tab_uses_pageheader(monkeypatch):
    _mock_streamlit(monkeypatch)
    mock_ph_instance = MagicMock()
    monkeypatch.setattr(admin_panel, "PageHeader", MagicMock(return_value=mock_ph_instance))

    admin_panel.render_decision_tab([])

    admin_panel.PageHeader.assert_called_once()
    args, kwargs = admin_panel.PageHeader.call_args
    assert args[0] == "Karar Defteri"
    assert kwargs.get("ust_etiket") == "İş · Yönetim"
    assert kwargs.get("ikon") == "📒"
    mock_ph_instance.render.assert_called_once()


def test_render_decision_tab_filters_by_decider(monkeypatch):
    _mock_streamlit(monkeypatch)
    admin_panel.st.selectbox.return_value = "copilot"

    decisions = [
        {
            "ts": "2026-09-13T12:00:00+00:00",
            "title": "Karar 1",
            "decision": "accepted",
            "decider": "copilot",
            "reason": "Gerekçe 1",
            "tags": [],
        },
        {
            "ts": "2026-09-13T12:00:00+00:00",
            "title": "Karar 2",
            "decision": "rejected",
            "decider": "admin",
            "reason": "Gerekçe 2",
            "tags": [],
        },
    ]

    admin_panel.render_decision_tab(decisions)

    rendered = admin_panel.st.dataframe.call_args.args[0]
    assert len(rendered) == 1
    assert rendered.iloc[0]["Karar Veren"] == "copilot"


def test_render_decision_tab_filters_by_tags(monkeypatch):
    _mock_streamlit(monkeypatch)
    admin_panel.st.multiselect.return_value = ["test"]

    decisions = [
        {
            "ts": "2026-09-13T12:00:00+00:00",
            "title": "Karar 1",
            "decision": "accepted",
            "decider": "admin",
            "reason": "Gerekçe 1",
            "tags": ["test"],
        },
        {
            "ts": "2026-09-13T12:00:00+00:00",
            "title": "Karar 2",
            "decision": "rejected",
            "decider": "admin",
            "reason": "Gerekçe 2",
            "tags": ["other"],
        },
    ]

    admin_panel.render_decision_tab(decisions)

    rendered = admin_panel.st.dataframe.call_args.args[0]
    assert len(rendered) == 1
    assert rendered.iloc[0]["Baslik"] == "Karar 1"


def test_render_decision_tab_form_submission(monkeypatch):
    _mock_streamlit(monkeypatch)
    monkeypatch.setattr(admin_panel, "log_decision", MagicMock())
    monkeypatch.setattr(admin_panel, "aktif_kullanici", lambda: "test@example.com")
    admin_panel.st.form_submit_button.return_value = True
    # text_input calls in order: Ara, Baslik, Karar, Gerekce, Etiketler
    admin_panel.st.text_input.side_effect = ["", "Yeni Karar", "accepted", "Gerekçe", "test, yeni"]

    decisions = [
        {
            "ts": "2026-09-13T12:00:00+00:00",
            "title": "Eski Karar",
            "decision": "accepted",
            "decider": "admin",
            "reason": "Eski gerekçe",
            "tags": ["eski"],
        }
    ]

    admin_panel.render_decision_tab(decisions)

    admin_panel.log_decision.assert_called_once_with(
        "Yeni Karar", "accepted", "test@example.com", "Gerekçe", ["test", "yeni"]
    )
    admin_panel.st.success.assert_called_once_with("Karar kaydedildi.")
    admin_panel.st.rerun.assert_called_once()


def test_read_decisions_skips_broken_jsonl_lines(monkeypatch, tmp_path: Path):
    log_file = tmp_path / "decision_log.jsonl"
    log_file.write_text(
        '{"title":"gecerli","decision":"accepted"}\n'
        '{bozuk jsonl}\n'
        '{"title":"ikinci","decision":"deferred"}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(decision_log, "DECISION_LOG", log_file)

    entries = decision_log.read_decisions()

    assert [entry["title"] for entry in entries] == ["gecerli", "ikinci"]