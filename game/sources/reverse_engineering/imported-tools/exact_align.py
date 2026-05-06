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
    
    # filter to only printable ascii and newline
    res = bytearray()
    for b in data:
        if (0x20 <= b <= 0x7E) or b == 0x0A:
            res.append(b)
    return res

encoded_group = get_text_bytes('/tmp/msg_group_rank.luac')
encoded_arena = get_text_bytes('/tmp/msg_arena_top_query.luac')

def compare(encoded_bytes, truth_str, name):
    # remove \r from truth
    truth_bytes = truth_str.replace('\r', '').encode('ascii')
    encoded_bytes = encoded_bytes.replace(b'\r', b'')
    
    print(f"Aligning {name}: len(enc)={len(encoded_bytes)}, len(truth)={len(truth_bytes)}")
    
    mapping = {}
    
    # Let's print them side-by-side to debug alignment
    for i in range(min(len(encoded_bytes), len(truth_bytes))):
        ec = chr(encoded_bytes[i])
        tc = chr(truth_bytes[i])
        if ec not in mapping:
            mapping[ec] = tc
        elif mapping[ec] != tc:
            print(f"  Conflict at {i}: {repr(ec)} mapped to {repr(mapping[ec])} but now {repr(tc)}")
            
        print(f"{i:3d}: {repr(ec)} -> {repr(tc)}")
        
    return mapping

print("Group Rank:")
map1 = compare(encoded_group, truth_group_rank, "group_rank")
print("\nArena Top:")
map2 = compare(encoded_arena, truth_arena_top, "arena_top")

