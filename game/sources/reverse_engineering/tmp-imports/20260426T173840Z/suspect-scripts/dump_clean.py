import json

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

def get_clean_bytes(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    data = data[3:]
    res = bytearray()
    for b in data:
        if 0x20 <= b <= 0x7E or b in (0x0A, 0x0D, 0x09):
            res.append(b)
    return res

enc_g = get_clean_bytes('/tmp/msg_group_rank.luac')
enc_a = get_clean_bytes('/tmp/msg_arena_top_query.luac')

# Let's write out the clean bytes to see them
with open('/tmp/clean_g.txt', 'wb') as f: f.write(enc_g)
with open('/tmp/clean_a.txt', 'wb') as f: f.write(enc_a)
