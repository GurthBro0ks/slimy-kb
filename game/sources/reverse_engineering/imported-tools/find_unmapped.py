import string

data = open('/tmp/list.luac', 'rb').read()
body = data[3:]
lines = body.split(b'\n')
text_body = b'\n'.join(lines[1:])

used_cipher_chars = set('gx8vfu5z4LeWy7F3qATpkalBVn') | set('c2tJ')

all_alnum = set(string.ascii_letters + string.digits)
cipher_chars_in_text = set()
for b in text_body:
    c = chr(b)
    if c in all_alnum:
        cipher_chars_in_text.add(c)

print("Cipher chars in text but not mapped:")
unmapped = sorted(list(cipher_chars_in_text - used_cipher_chars))
print(unmapped)

for c in unmapped:
    words = []
    for word in text_body.split(b'"'):
        if c.encode() in word:
            words.append(word)
    print(f"Usage of {c}: {set(words)}")
