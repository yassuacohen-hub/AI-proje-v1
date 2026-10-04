import sys
sys.path.insert(0, '.')
from src.company_master.gateway.ninerouter_client import NineRouter
nr = NineRouter()
print('TEST:', nr.chat('test'))