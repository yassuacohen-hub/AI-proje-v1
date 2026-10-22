import sys
sys.path.insert(0, r'c:\Huginn Data Projesi\Huginn Data Insights\src')

from company_master.api.routers.v1 import router as v1_router
print('v1 router imported successfully')
print(f'Router prefix: {v1_router.prefix}')
print(f'Router tags: {v1_router.tags}')

# Also test network_router
from company_master.api.routers.v1.network_router import router as network_router
print(f'Network router imported successfully')
print(f'Network router prefix: {network_router.prefix}')

# Test fraud module
from company_master.api.routers.v1.fraud import get_fraud_dict, apply_kvkk_mask
print(f'Fraud functions imported successfully')

# Test scope module
from company_master.api.routers.v1.scope import scope_gerekli, kredi_dus
print(f'Scope functions imported successfully')

print('\nAll imports successful!')