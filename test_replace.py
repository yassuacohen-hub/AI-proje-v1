# This script replaces the api management function with a simple comment to test if replacement works
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Lines are 0-indexed
    # We want to replace lines 9 to 25 (0-index) inclusive? 
    # Line 10 (1-index) is index 9
    # Line 26 (1-index) is index 25
    # We want to replace from index 9 to index 25 inclusive.
    # So we want to replace lines[9:26] (since 26 is exclusive) -> indices 9 to 25.
    start_idx = 9  # line 10
    end_idx = 26   # line 26 (exclusive) -> we will replace up to line 25 (0-index) which is line 26 (1-index)

    # Replace with a simple comment
    replacement_lines = [
        '# API management function replaced\n'
    ]

    # Replace the lines
    lines[start_idx:end_idx] = replacement_lines

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Api management function replaced with a simple comment")

if __name__ == '__main__':
    main()
