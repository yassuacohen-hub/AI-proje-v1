with open(r'C:\Huginn Data Projesi\Huginn Data Insights\web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the verify function
idx = content.find('def api_admin_mfa_verify')
try_idx = content.find('try:', idx)
except_idx = content.find('except Exception as e:', idx)

print(f'Try at: {try_idx}')
print(f'Except at: {except_idx}')

# Get the context around except
except_context = content[except_idx-200:except_idx+300]
print('EXCEPT CONTEXT:')
print(repr(except_context))

# The structure should be:
# try: (at indent 4 from function start = 8 from file start)
#   ... code ...
#   with engine.begin() as conn: (indent 8)
#     conn.execute( ... )  # missing closing )
#   }  (closes with block)
# except Exception as e: (should be at same level as try = indent 8 from file start)
#     raise ...

# The issue: except is at indent 16 (12 spaces from file start?), should be at 8 (same as try)
# Also missing ) for conn.execute()

# Let's find the exact boundaries
except_start = content.find('except Exception as e:\n', except_idx)
except_end = content.find('\n\n', except_idx)
if except_end == -1:
    except_end = except_idx + 500

print('EXCEPT BLOCK:')
print(repr(content[except_idx:except_end]))

# The structure around except:
# Before except: dict close }, with block close }, except:
# Need to add ) for conn.execute() and } for with block before except

# Let's find the exact boundaries
before_except = content[except_idx-100:except_idx]
print('BEFORE EXCEPT:')
print(repr(before_except))
"