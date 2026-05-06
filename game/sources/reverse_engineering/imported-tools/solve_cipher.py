import string
import os

truth_group_rank = """-- msg_group_rank
-- Create by chenx 2023-06
return function(lpc)
    RankM.setRankInfo(RANKID_GROUP, nil, lpc.list)
end"""

truth_arena_top = """-- msg_arena_top_query
-- Create by weism
return function(lpc)
    EventMgr.fire_event(ARENATOP_QUERY, lpc)
end"""

def get_text_bytes(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    if data[:3] == bytes([0x14, 0x15, 0x16]):
        data = data[3:]
    # filter to only printable ascii and newline/carriage return
    res = bytearray()
    for b in data:
        if 0x20 <= b <= 0x7E or b == 0x0A or b == 0x0D:
            res.append(b)
    return res

encoded_group = get_text_bytes('/tmp/msg_group_rank.luac')
encoded_arena = get_text_bytes('/tmp/msg_arena_top_query.luac')

def compare(encoded_bytes, truth_str, name):
    truth_bytes = truth_str.replace('\r', '').encode('ascii')
    # Filter out carriage returns from encoded for fair comparison
    encoded_bytes = encoded_bytes.replace(b'\r', b'')
    
    # We only care about matching up to the length of truth
    # Wait, what if there are extra newlines? Let's just compare character by character
    # ignoring extra whitespace at the start or end if needed.
    # Actually, we can align by stripping leading/trailing whitespace
    encoded_str = encoded_bytes.decode('ascii')
    
    # Simple alignment: they should be exactly the same length if we strip trailing whitespace
    # Actually, let's just do a direct alignment
    
    mapping = {}
    conflicts = []
    
    # Strip leading/trailing newlines
    enc_lines = encoded_str.strip().split('\n')
    truth_lines = truth_str.strip().split('\n')
    
    for i, (eline, tline) in enumerate(zip(enc_lines, truth_lines)):
        # print(f"ENC: {eline}")
        # print(f"TRU: {tline}")
        if len(eline) != len(tline):
            print(f"Length mismatch in {name} line {i}: {len(eline)} vs {len(tline)}")
            # Try to zip as much as possible
        for ec, tc in zip(eline, tline):
            if ec not in mapping:
                mapping[ec] = tc
            else:
                if mapping[ec] != tc:
                    conflicts.append((ec, mapping[ec], tc))
                    
    return mapping, conflicts

map1, conf1 = compare(encoded_group, truth_group_rank, "group_rank")
map2, conf2 = compare(encoded_arena, truth_arena_top, "arena_top")

print("Conflicts in group:", conf1)
print("Conflicts in arena:", conf2)

combined_map = {}
all_conflicts = []

for m in [map1, map2]:
    for k, v in m.items():
        if k in combined_map and combined_map[k] != v:
            all_conflicts.append((k, combined_map[k], v))
        combined_map[k] = v

print("All conflicts:", all_conflicts)
print("Extracted Mapping:")
for k in sorted(combined_map.keys()):
    print(f"  {repr(k)} -> {repr(combined_map[k])}")

# Let's write the mappings out as a json or python dict
import json
with open('/tmp/extracted_map.json', 'w') as f:
    json.dump(combined_map, f)
