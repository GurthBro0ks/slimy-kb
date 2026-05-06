from collections import Counter
import re

with open('/tmp/list.luac', 'rb') as f:
    data = f.read()[3:]
    
text = bytearray()
for b in data:
    if 0x20 <= b <= 0x7E:
        text.append(b)

text_str = text.decode('ascii')
strings = re.findall(r'"([^"]+)"', text_str)

punct_counts = Counter()
for s in strings:
    for c in s:
        if not c.isalnum() and c != '@':
            punct_counts[c] += 1
            
print("Punctuation counts in strings:")
for k, v in punct_counts.most_common():
    print(f"  {repr(k)}: {v}")
