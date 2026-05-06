import re
data = open('/tmp/list.luac', 'rb').read()
body = data[3:]
lines = body.split(b'\n')
text_body = b'\n'.join(lines[1:])

mapping = {
    'g': 'a', 'x': 'b', '8': 'c', 'v': 'd', 'f': 'e',
    'u': 'f', '5': 'g', 'z': 'h', '4': 'i', 'L': 'j',
    'e': 'k', 'W': 'l', 'y': 'm', '7': 'n', 'F': 'o',
    '3': 'p', 'q': 'q', 'A': 'r', 'T': 's', 'p': 't',
    'k': 'u', 'a': 'v', 'l': 'w', 'B': 'x', 'V': 'y',
    'n': 'z',
    'c': '0', '2': '1', 't': '2', 'J': '3', '0': '4', 's': '5'
}

def decode(text_bytes):
    out = bytearray()
    for b in text_bytes:
        c = chr(b)
        if c in mapping:
            out.append(ord(mapping[c]))
        else:
            out.append(b)
    return out

decoded_body = decode(text_body).decode('ascii', errors='ignore')

# Extract all quoted strings
strings = re.findall(r'"([^"]*)"', decoded_body)
for s in strings:
    if '91Q' not in s and re.search(r'[a-zA-Z0-9]', s):
        # find characters that are still letters but might be garbage
        # anything not in [a-z0-5] and special characters
        pass

# let's just save the decoded_body and check the handler code
open('/tmp/list_clean_decoded.lua', 'w').write(decoded_body)
