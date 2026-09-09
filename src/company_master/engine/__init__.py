# -*- coding: utf-8 -*-
"""OSINT Scraper Motoru (v1) — kaynak kaydi.

Orkestrator CLI: python -m company_master.engine.osint_engine
(src layout: PYTHONPATH=src gerekir; scripts/osint_engine.py koprusu bunu halleder)
"""
from .source_registry import SourceSpec, default_sources, registry

__all__ = ["SourceSpec", "default_sources", "registry"]