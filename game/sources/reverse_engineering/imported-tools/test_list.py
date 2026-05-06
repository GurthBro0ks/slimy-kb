import re

known = {
    'a':'v', 'c':'0', 'e':'k', 'f':'e', 'g':'a', 'i':'W', 'j':'P', 'k':'u', 
    'l':'w', 'm':'N', 'n':'z', 'p':'t', 'q':'q', 's':'5', 't':'2', 'u':'f', 
    'v':'d', 'x':'b', 'y':'m', 'z':'h',
    'A':'r', 'B':'x', 'C':'I', 'E':'C', 'F':'o', 'I':'R', 'J':'3', 'L':'j', 
    'N':'D', 'O':'A', 'P':'E', 'Q':'G', 'R':'O', 'T':'s', 'V':'y', 'W':'l', 'Z':'U',
    '0':'4', '1':'S', '2':'1', '3':'p', '4':'i', '5':'g', '7':'n', '8':'c', '9':'M',
    'b':'Q', 'd':'T', 'H':'Y',
    '#':'-', '+':'_', '%':' ', ';':'.', '{':'\n', '=':'(', '|':')', '*':','
}

# Add self-mappings for unmapped characters so they don't disappear
for i in range(256):
    c = chr(i)
    if c not in known:
        known[c] = c

with open('/tmp/list.luac', 'rb') as f:
    data = f.read()

if data[:3] == bytes([0x14, 0x15, 0x16]):
    body = data[3:]
else:
    body = data

# Skip metadata header if present
lines = body.split(b'\n', 1)
if len(lines) > 1:
    text_body = lines[1]
else:
    text_body = lines[0]

decoded_body = bytearray()
for b in text_body:
    c = chr(b)
    decoded_body.append(ord(known[c]))

decoded_str = decoded_body.decode('ascii', errors='ignore')

# Check valid Lua keywords
print("Contains 'return':", 'return' in decoded_str)
print("Contains 'function':", 'function' in decoded_str)

# Extract protocol messages
strings = re.findall(r'"([^"]+)"', decoded_str)
print("Total strings:", len(strings))

invalid_chars = set()
for s in strings:
    for c in s:
        if not c.isalnum() and c not in ['_', ' ', '.', '@']:
            invalid_chars.add(c)
            
print("Invalid chars in strings:", invalid_chars)
