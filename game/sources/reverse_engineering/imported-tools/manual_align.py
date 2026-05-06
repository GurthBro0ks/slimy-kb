import json

truth_group = """-- msg_group_rank
-- Create by chenx 2023-06
return function(lpc)
    RankM.setRankInfo(RANKID_GROUP, nil, lpc.list)
end"""

truth_arena = """-- msg_arena_top_query
-- Create by weism
return function(lpc)
    EventMgr.fire_event(ARENATOP_QUERY, lpc)
end"""

with open('/tmp/msg_group_rank.luac', 'rb') as f:
    enc_g = f.read()[3:]
with open('/tmp/msg_arena_top_query.luac', 'rb') as f:
    enc_a = f.read()[3:]

# Keep only printable and newlines
def clean(b_arr):
    res = bytearray()
    for b in b_arr:
        if (0x20 <= b <= 0x7E) or b in (0x0A, 0x0D):
            res.append(b)
    return res

enc_g = clean(enc_g)
enc_a = clean(enc_a)

def extract_mapping(enc, truth):
    t_idx = 0
    mapping = {}
    for e in enc:
        if t_idx >= len(truth): break
        ec = chr(e)
        tc = truth[t_idx]
        
        # Skip carriage returns in truth matching
        if tc == '\r':
            t_idx += 1
            if t_idx < len(truth): tc = truth[t_idx]
            else: break
            
        # We need a robust matching. Let's just output side-by-side
        print(f"{repr(ec):4} | {repr(tc):4}")
        t_idx += 1

print("--- GROUP RANK ---")
extract_mapping(enc_g, truth_group)
