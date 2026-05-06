import re
import sys

mapping = {
    'g': 'a', 'x': 'b', '8': 'c', 'v': 'd', 'f': 'e',
    'u': 'f', '5': 'g', 'z': 'h', '4': 'i', 'L': 'j',
    'e': 'k', 'W': 'l', 'y': 'm', '7': 'n', 'F': 'o',
    '3': 'p', 'q': 'q', 'A': 'r', 'T': 's', 'p': 't',
    'k': 'u', 'a': 'v', 'l': 'w', 'B': 'x', 'V': 'y',
    'n': 'z',
    'c': '0', '2': '1', 't': '2', 'J': '3', '0': '4', 's': '5',
    'O': 'A', 'b': 'Q', 'I': 'R', 'Z': 'U', 'j': 'P', 'P': 'E',
    'm': 'N', 'H': 'Y', 'R': 'O', 'd': 'T', 'E': 'C', '9': 'M',
    '1': 'S', 'Q': 'G', 'i': 'W', 'C': 'I', 'N': 'D', 'S': 'K'
}

punct_map = {
    '#': '(',
    '*': '_',
    '=': ',',
    '(': ' ',
    '_': '.',
    ':': '(',
    ';': '.',
    '+': '_',
    '-': ')',
    '|': '\n',
    '{': ' ',
    '}': ' ',
    '[': ' ',
    ']': ' ',
    ' ': '_'
}

def decode_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    if data[:3] == bytes([0x14, 0x15, 0x16]):
        body = data[3:]
    else:
        body = data
    
    # Just look at the text part (skip binary)
    text = re.sub(b'[^\x20-\x7E\n\r]', b'', body).decode('ascii')
    
    decoded = ""
    for c in text:
        if c in mapping:
            decoded += mapping[c]
        elif c in punct_map:
            decoded += punct_map[c]
        else:
            decoded += c
    return decoded

print("=== msg_group_rank.luac ===")
print(decode_file('/tmp/msg_group_rank.luac'))

print("\n=== msg_arena_top_query.luac ===")
print(decode_file('/tmp/msg_arena_top_query.luac'))

