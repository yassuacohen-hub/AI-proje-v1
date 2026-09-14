# -*- coding: utf-8 -*-
"""UX-01: Yeniden kullanılabilir UI bileşenleri.

Sekiz temel bileşen: Button, Input, Dropdown, Badge, Card (+MetricCard),
Table, Modal, Tooltip.

ADMIN-UI-01 ile eklenen sayfa iskeleti: PageHeader, Section, SectionNav.
ADMIN-UI-02 ile eklenen buton sistemi: ROLLER, ButtonGroup.
ADMIN-UI-03 ile eklenen kabuk: TopBar, ThemeToggle, ChatBubble.
"""
from __future__ import annotations

from company_master.ui.components.badge import DURUM_VARYANT, Badge
from company_master.ui.components.button import ROLLER, Button, ButtonGroup, rol_dogrula
from company_master.ui.components.card import KATEGORILER, Card, MetricCard
from company_master.ui.components.dropdown import Dropdown, secenekleri_normalize
from company_master.ui.components.input import TIPLER, Input
from company_master.ui.components.modal import MODAL_BOYUTLARI, Modal
from company_master.ui.components.page import (
    PageHeader,
    Section,
    SectionNav,
    kimlik_uret,
)
from company_master.ui.components.table import HIZALAMALAR, Table
from company_master.ui.components.tooltip import KONUMLAR, Tooltip
from company_master.ui.components.topbar import (
    SOHBET_ROLLERI,
    TEMA_SUNUMU,
    ChatBubble,
    ThemeToggle,
    TopBar,
    tema_dogrula,
    tema_karsiti,
)

__all__ = [
    "Badge",
    "Button",
    "ButtonGroup",
    "Card",
    "ChatBubble",
    "Dropdown",
    "Input",
    "MetricCard",
    "Modal",
    "PageHeader",
    "Section",
    "SectionNav",
    "Table",
    "ThemeToggle",
    "Tooltip",
    "TopBar",
    "DURUM_VARYANT",
    "HIZALAMALAR",
    "KATEGORILER",
    "KONUMLAR",
    "MODAL_BOYUTLARI",
    "ROLLER",
    "SOHBET_ROLLERI",
    "TEMA_SUNUMU",
    "TIPLER",
    "kimlik_uret",
    "rol_dogrula",
    "secenekleri_normalize",
    "tema_dogrula",
    "tema_karsiti",
]
