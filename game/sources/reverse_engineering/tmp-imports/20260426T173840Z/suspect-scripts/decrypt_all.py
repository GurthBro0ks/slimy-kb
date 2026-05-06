import sys
import os

input_file = sys.argv[1]
output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.luac', '.lua')

with open(input_file, 'rb') as f:
    data = f.read()

if data[:3] == bytes([0x14, 0x15, 0x16]):
    body = data[3:]
else:
    body = data

mapping = {
    'g': 'a', 'x': 'b', '8': 'c', 'v': 'd', 'f': 'e',
    'u': 'f', '5': 'g', 'z': 'h', '4': 'i', 'L': 'j',
    'e': 'k', 'W': 'l', 'y': 'm', '7': 'n', 'F': 'o',
    '3': 'p', 'q': 'q', 'A': 'r', 'T': 's', 'p': 't',
    'k': 'u', 'a': 'v', 'l': 'w', 'B': 'x', 'V': 'y',
    'n': 'z',
    'c': '0', '2': '1', 't': '2', 'J': '3', '0': '4', 's': '5'
}

decoded_body = bytearray()
for b in body:
    c = chr(b)
    if c in mapping:
        decoded_body.append(ord(mapping[c]))
    else:
        decoded_body.append(b)

with open(output_file, 'wb') as f:
    f.write(decoded_body)
