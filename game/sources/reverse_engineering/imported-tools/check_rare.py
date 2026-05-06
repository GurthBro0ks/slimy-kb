data = open('/tmp/list.luac', 'rb').read()
body = data[3:]
lines = body.split(b'\n')
text_body = b'\n'.join(lines[1:])

import re

for c in b'2901ZjmENsQRP':
    words = re.findall(b'[a-zA-Z0-9_]*' + bytes([c]) + b'[a-zA-Z0-9_]*', text_body)
    print(f"Words with {chr(c)}:", set(words))
