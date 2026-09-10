path = r'C:\Projeler\Huginn Data Insights\.env'
with open(path, 'rb') as f:
    data = f.read()
if data.startswith(b'\xef\xbb\xbf'):
    data = data[3:]
with open(path, 'wb') as f:
    f.write(data)
print('BOM removed, size:', len(data))
