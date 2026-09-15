import re
with open('restore_original.py', 'r') as f:
    content = f.read()
match = re.search(r"original_content = '''(.*?)'''", content, re.DOTALL)
if match:
    original_str = match.group(1)
    # Fix the except indentation in render_api_management
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
