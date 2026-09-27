import json
from pathlib import Path

# Check nace-rev-2-1.json
path2 = Path('C:/Huginn Data Projesi/Huginn Data Insights/data/nace/nace-rev-2-1.json')
with open(path2, 'r', encoding='utf-8') as f:
    data = json.load(f)
    print('nace-rev-2-1.json structure:')
    print(f'  Type: {type(data)}')
    if isinstance(data, list):
        print(f'  List length: {len(data)}')
        if data:
            print(f'  First item keys: {list(data[0].keys())}')
            print(f'  First item: {data[0]}')

# Check nace-rev-2.json
path3 = Path('C:/Huginn Data Projesi/Huginn Data Insights/data/nace/nace-rev-2.json')
with open(path3, 'r', encoding='utf-8') as f:
    data = json.load(f)
    print('nace-rev-2.json structure:')
    print(f'  Type: {type(data)}')
    if isinstance(data, list):
        print(f'  List length: {len(data)}')
        if data:
            print(f'  First item keys: {list(data[0].keys())}')
            print(f'  First item: {data[0]}')