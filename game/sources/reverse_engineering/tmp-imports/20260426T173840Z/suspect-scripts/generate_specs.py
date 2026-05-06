import re
from collections import defaultdict

decoded = open('/tmp/list_clean_decoded.lua', 'r').read()

# Extract all quoted strings
strings = re.findall(r'"([^"]+)"', decoded)

protocol_messages = []
grouped = defaultdict(list)

for s in strings:
    if '91Q' in s: continue # Skip the garbage string
    
    # Split by @ if possible
    parts = s.split('@', 1)
    if len(parts) == 2:
        prefix = parts[0]
        # Replace any non-alphanumeric character with underscore
        msg_name = re.sub(r'[^a-zA-Z0-9]', '_', parts[1])
        protocol_messages.append(f"{prefix}@{msg_name}")
        grouped[prefix].append(msg_name)
    else:
        # If no @, just normalize the whole thing
        msg_name = re.sub(r'[^a-zA-Z0-9]', '_', s)
        protocol_messages.append(msg_name)
        grouped['unknown'].append(msg_name)

# Write all_protocol_messages.txt
with open('/tmp/all_protocol_messages.txt', 'w') as f:
    for msg in sorted(protocol_messages):
        f.write(msg + '\n')

# Write PROTOCOL_SPEC.md
with open('/tmp/PROTOCOL_SPEC.md', 'w') as f:
    f.write("# Protocol Specification\n\n")
    for prefix in sorted(grouped.keys()):
        f.write(f"## {prefix.capitalize()} Namespace\n")
        for msg in sorted(grouped[prefix]):
            f.write(f"- `{msg}`\n")
        f.write("\n")

print("Generated spec files.")
