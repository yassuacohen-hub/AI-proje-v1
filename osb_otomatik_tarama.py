#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OSB Otomatik Tarama - Baslik ve Konfigurasyon"""

import json
import os
import time
from datetime import datetime

# Konfigurasyon
JSON_INPUT = r'c:\Huginn Data Projesi\osb_harita_verisi.json'
JSON_OUTPUT = r'c:\Huginn Data Projesi\osb_firma_havuzu.json'

BASELINE = {
    "www.agiosb.org": {"firma_sayisi": "Rehber var", "sektor": "Gida/lojistik"},
    "www.adanaorganize.org.tr": {"firma_sayisi": "498 firma", "sektor": "Genel"}
}