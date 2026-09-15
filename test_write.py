# This script tests if we can write to a file
import sys

test_path = 'test_write.txt'
with open(test_path, 'w', encoding='utf-8') as f:
    f.write('Hello, world!')
with open(test_path, 'r', encoding='utf-8') as f:
    content = f.read()
print('Content of test file: {}'.format(repr(content)))
if content == 'Hello, world!':
    print('Write test passed')
else:
    print('Write test failed')
