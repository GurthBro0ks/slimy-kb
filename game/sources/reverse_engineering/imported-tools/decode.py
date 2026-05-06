import string
from collections import Counter

data = open('/tmp/list.luac', 'rb').read()
body = data[3:]
lines = body.split(b'\n')
text_body = b'\n'.join(lines[1:])  # skip binary header

known_mappings = {
    'A': 'r', 'f': 'e', 'p': 't', 'k': 'u', '7': 'n', 'F': 'o',
    '4': 'i', 'T': 's', '5': 'g', 'a': 'v', 'g': 'a', '8': 'c',
    'V': 'y', 'W': 'l', 'x': 'b', '3': 'p', 'v': 'd', 'z': 'z',
    'y': 'm', 'l': 'w', 'B': 'x', 'q': 'q', 'I': 'f'
}

# Reverse mapping to see what's taken
taken_decoded = set(known_mappings.values())

def decode(text_bytes):
    out = bytearray()
    for b in text_bytes:
        c = chr(b)
        if c in known_mappings:
            out.append(ord(known_mappings[c]))
        else:
            out.append(b)
    return out

decoded_body = decode(text_body)

# Print frequency of unknown characters
unknown_freq = Counter()
for b in text_body:
    c = chr(b)
    if (c.isalpha() or c.isdigit()) and c not in known_mappings:
        unknown_freq[c] += 1

print("Unknown character frequencies:")
for k, v in unknown_freq.most_common():
    print(f"{k}: {v}")

print("\nMissing decoded characters (a-z):")
all_lowercase = set(string.ascii_lowercase)
print(sorted(list(all_lowercase - taken_decoded)))

print("\nSample of decoded text (lines 100-150):")
print(decoded_body.split(b'\n')[100:150])
