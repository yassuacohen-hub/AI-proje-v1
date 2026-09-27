with open(r'C:\Huginn Data Projesi\Huginn Data Insights\web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the except block
except_idx = content.find('except Exception as e:', 141456)
print('Except at:', except_idx)

# Show context before except
before_except = content[except_idx-200:except_idx]
print('BEFORE EXCEPT:')
print(repr(before_except))

print()
print('EXCEPT LINE:')
print(repr(content[except_idx:except_idx+100]))

print()
print('AFTER EXCEPT:')
print(repr(content[except_idx+100:except_idx+300]))