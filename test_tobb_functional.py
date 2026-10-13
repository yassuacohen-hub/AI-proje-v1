#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TOBB API Functional Test - Search by VKN + Balance"""
import asyncio
import sys
sys.path.insert(0, 'src')

from company_master.etl.tobb_api import TobbApiClient


async def test():
    client = TobbApiClient()
    
    # Test 1: Bakiye
    print("=== BAKIYE TESTI ===")
    balance = await client.get_balance()
    print(f"Basarili: {balance.success}")
    print(f"Bakiye: {balance.bakiye} TL")
    if balance.error_message:
        print(f"Hata: {balance.error_message}")
    print(f"Raw response: {balance.raw_response}")
    
    # Test 2: Kart 02 - VKN ile sorgulama
    print("\n=== KART 02 TESTI (VKN: 7350835826) ===")
    card02 = await client.search_by_vkn('7350835826')
    print(f"Basarili: {card02.success}")
    if card02.success:
        print(f"Unvan: {card02.unvani}")
        print(f"MERSIS: {card02.mersis_no}")
        print(f"Durum: {card02.firma_durumu}")
        print(f"Sermaye: {card02.sirket_toplam_sermayesi}")
        print(f"Vergi Kimlik No: {card02.vergi_kimlik_no}")
        print(f"Ticari Unvan: {card02.ticari_unvani}")
        print(f"Adres: {card02.adres}")
        print(f"Il: {card02.il}")
        print(f"Ilce: {card02.ilce}")
        if card02.naceler:
            print(f"NACE: {card02.naceler}")
        else:
            print("NACE: Yok")
    else:
        print(f"Hata: {card02.error_message}")
        print(f"Raw: {card02.raw_response}")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test())