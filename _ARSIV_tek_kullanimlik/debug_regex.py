import re

s = "3DTİM ELEK. A.Ş."

# Test the specific pattern
pattern = r'\bELEK\.\b'
print(f"Testing: {s}")
print(f"Pattern: {pattern}")
matches = list(re.finditer(pattern, s, re.IGNORECASE))
print(f"Matches: {[(m.start(), m.end(), m.group()) for m in matches]}")

# Try without word boundary on the right
pattern2 = r'\bELEK\.'
matches2 = list(re.finditer(pattern2, s, re.IGNORECASE))
print(f"Pattern without right boundary: {[(m.start(), m.end(), m.group()) for m in matches2]}")

# Try with lookbehind
pattern3 = r'(?<=\s)ELEK\.'
matches3 = list(re.finditer(pattern3, s, re.IGNORECASE))
print(f"Pattern with lookbehind: {[(m.start(), m.end(), m.group()) for m in matches3]}")

# Try with optional word boundary
pattern4 = r'ELEK\.'
matches4 = list(re.finditer(pattern4, s, re.IGNORECASE))
print(f"Pattern without word boundary: {[(m.start(), m.end(), m.group()) for m in matches4]}")