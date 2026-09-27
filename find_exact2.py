with open(r'C:\Huginn Data Projesi\Huginn Data Insights\web_app.py', 'rb') as f:
    content = f.read()

# Find the SPECIFIC pattern for MFA status - use the unique marker
marker = b'MFA status hatas'
pos = content.find(b'MFA status hatas')
print(f'Marker at: {pos}')

# Find the except block - go backwards from the marker
except_pos = content.rfind(b'except Exception as e:', 0, pos + 200)
print(f'Except at: {except_pos}')

# Find the end of the function (next function or end of file)
# Look for the next function definition or end of file
next_func = content.find(b'\n\n@app.', pos)
if next_func == -1:
    next_func = len(content)
end_pos = next_func

print(f'End at: {next_func}')

# Show the exact bytes to replace
print(repr(content[pos-100:pos+500]))

# Now construct the exact old pattern
old_start = content.rfind(b'            }\r\n        \r\n        except Exception as e:', 0, pos + 200)
print(f'Old start at: {old_start}')

# The exact old pattern
old = content[old_start:content.find(b'if __name__ == "__main__":', pos) + len('if __name__ == "__main__":\r\n    uvicorn.run(app, host="0.0.0.0", port=8000)')]
print('OLD PATTERN:')
print(repr(old[:500]))