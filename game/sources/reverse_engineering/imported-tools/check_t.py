data = open('/tmp/list.luac', 'rb').read()
body = data[3:]
lines = body.split(b'\n')
text_body = b'\n'.join(lines[1:])

for word in text_body.split(b'"'):
    if b't' in word and b'misc@' in word:
        print(word)
