data = open('/tmp/list.luac', 'rb').read()
body = data[3:]
lines = body.split(b'\n')
text_body = b'\n'.join(lines[1:])

import re

# We will just find strings like "misc@msg..." in the original bytes
def find_words():
    for word in text_body.split(b'"'):
        if b'misc' in word:
            print(word)

words = []
in_string = False
curr_word = bytearray()
for b in text_body:
    if b == ord('"'):
        if in_string:
            words.append(curr_word)
            curr_word = bytearray()
            in_string = False
        else:
            in_string = True
    elif in_string:
        curr_word.append(b)

known_mappings = {
    'A': 'r', 'f': 'e', 'p': 't', 'k': 'u', '7': 'n', 'F': 'o',
    '4': 'i', 'T': 's', '5': 'g', 'a': 'v', 'g': 'a', '8': 'c',
    'V': 'y', 'W': 'l', 'x': 'b', '3': 'p', 'v': 'd', 'z': 'z',
    'y': 'm', 'l': 'w', 'B': 'x', 'q': 'q', 'I': 'f'
}

def partial_decode(b_arr):
    out = bytearray()
    for b in b_arr:
        c = chr(b)
        if c in known_mappings:
            out.append(ord(known_mappings[c]))
        else:
            out.append(b)
    return out

for w in words:
    if b'misc' in w or b'misc' in partial_decode(w):
        pd = partial_decode(w).decode('ascii', errors='ignore')
        orig = w.decode('ascii', errors='ignore')
        if 'uetcz' in pd or 'unloce' in pd or 'eigzt' in pd:
            print(f"Orig: {orig} -> Partial: {pd}")
