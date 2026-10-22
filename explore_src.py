import os

root = r"c:\Huginn Data Projesi\Huginn Data Insights\src"
if os.path.exists(root):
    for dirpath, dirnames, filenames in os.walk(root):
        level = dirpath.replace(root, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(dirpath)}/')
        for f in filenames[:10]:
            print(f'{indent}  {f}')
else:
    print("src does not exist")