#!/usr/bin/env python3
import sys
import os

known_mappings = {
    # Lowercase
    'a': 'v', 'c': '0', 'e': 'k', 'f': 'e', 'g': 'a', 'i': 'W', 'j': 'P',
    'k': 'u', 'l': 'w', 'm': 'N', 'n': 'z', 'p': 't', 'q': 'q', 's': '5',
    't': '2', 'u': 'f', 'v': 'd', 'x': 'b', 'y': 'm', 'z': 'h', 'w': 'K',
    'b': 'Q', 'd': 'T', 'r': 'H', # guessed
    # Uppercase
    'A': 'r', 'B': 'x', 'C': 'I', 'E': 'C', 'F': 'o', 'I': 'R', 'J': '3',
    'L': 'j', 'N': 'D', 'O': 'A', 'P': 'E', 'Q': 'G', 'R': 'O', 'T': 's',
    'V': 'y', 'W': 'l', 'Z': 'U', 'H': 'Y', 'S': 'K', # from Phase 2B? wait, maybe S->K is wrong
    # Digits
    '0': '4', '1': 'S', '2': '1', '3': 'p', '4': 'i', '5': 'g', '7': 'n', '8': 'c', '9': 'M', '6': '6',
    # Punctuation
    '#': '-', '%': ' ', '+': '_', '|': '(', '*': ')', ';': '.', '=': ',',
}

def decrypt(file_path):
    data = open(file_path, 'rb').read()
    body = data[3:] # skip \x14\x15\x16 header
    out = bytearray()
    for b in body:
        if b == 10 or b == 13:
            out.append(b)
            continue
        c = chr(b)
        if c in known_mappings:
            out.append(ord(known_mappings[c]))
        else:
            out.append(b)
    return out.decode('ascii', errors='replace')

if __name__ == '__main__':
    for path in sys.argv[1:]:
        print(f"--- {os.path.basename(path)} ---")
        print(decrypt(path))
        print("------------------\n")
