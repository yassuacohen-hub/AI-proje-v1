import re
with open('restore_original.py', 'r') as f:
    content = f.read()
pattern = re.compile(r"original_content = '''(.*?)'''", re.DOTALL)
match = pattern.search(content)
if match:
    original_str = match.group(1)
    lines = original_str.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.rstrip() == '        except APIError:':
            lines[i] = '    except APIError:\n'
            break
    fixed_str = ''.join(lines)
    with open('web_dashboard/tabs/admin_extras.py', 'w', encoding='utf-8') as f:
        f.write(fixed_str)
else:
    print('Original content not found')
