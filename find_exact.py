with open(r'C:\Huginn Data Projesi\Huginn Data Insights\web_app.py', 'rb') as f:
    content = f.read()

# Find the specific pattern for MFA status function
# The pattern is: "MFA status hatas" followed by the except block
marker = b'MFA status hatas'
pos = content.find(b'MFA status hatas')
print(f'Marker at: {pos}')

# Find the except block before this marker
except_pos = content.rfind(b'except Exception as e:', 0, pos + 200)
print(f'except at: {except_pos}')

# Show context
context = content[except_pos-50:pos+300]
print(repr(context))