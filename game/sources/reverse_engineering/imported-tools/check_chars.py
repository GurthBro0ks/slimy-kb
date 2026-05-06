data = open('/tmp/list.luac', 'rb').read()
body = data[3:]
lines = body.split(b'\n')
text_body = b'\n'.join(lines[1:])

import re

# find any alphanumeric sequence containing 't'
words_with_t = re.findall(b'[a-zA-Z0-9_]*t[a-zA-Z0-9_]*', text_body)
print("Words with t:", set(words_with_t))

# find any alphanumeric sequence containing 'c'
words_with_c = re.findall(b'[a-zA-Z0-9_]*c[a-zA-Z0-9_]*', text_body)
print("Words with c:", set(words_with_c))

# find any alphanumeric sequence containing 'n'
words_with_n = re.findall(b'[a-zA-Z0-9_]*n[a-zA-Z0-9_]*', text_body)
print("Words with n:", set(words_with_n))

# find any alphanumeric sequence containing 'L'
words_with_L = re.findall(b'[a-zA-Z0-9_]*L[a-zA-Z0-9_]*', text_body)
print("Words with L:", set(words_with_L))

# find any alphanumeric sequence containing 'J'
words_with_J = re.findall(b'[a-zA-Z0-9_]*J[a-zA-Z0-9_]*', text_body)
print("Words with J:", set(words_with_J))
