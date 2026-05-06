data = open('/tmp/list.luac', 'rb').read()
body = data[3:]
lines = body.split(b'\n')
text_body = b'\n'.join(lines[1:])

for word in text_body.split(b'"'):
    if b'I' in word:
        print(word)

for word in text_body.split(b'"'):
    if b'u' in word:
        print(word)
