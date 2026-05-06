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

known = {
    'g': 'a', 'x': 'b', '8': 'c', 'v': 'd', 'f': 'e',
    'u': 'f', '5': 'g', 'z': 'h', '4': 'i', 'L': 'j',
    'e': 'k', 'W': 'l', 'y': 'm', '7': 'n', 'F': 'o',
    '3': 'p', 'q': 'q', 'A': 'r', 'T': 's', 'p': 't',
    'k': 'u', 'a': 'v', 'l': 'w', 'B': 'x', 'V': 'y',
    'n': 'z',
    'c': '0', '2': '1', 't': '2', 'J': '3', '0': '4', 's': '5',
    'O': 'A', 'b': 'Q', 'I': 'R', 'Z': 'U', 'j': 'P', 'P': 'E',
    'm': 'N', 'H': 'Y', 'R': 'O', 'd': 'T', 'E': 'C', '9': 'M',
    '1': 'S', 'Q': 'G', 'i': 'W', 'C': 'I', 'N': 'D', 'S': 'K'
}

def lcs_align(enc_bytes, truth_str):
    truth_bytes = truth_str.replace('\r', '').encode('ascii')
    m, n = len(enc_bytes), len(truth_bytes)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            ec = chr(enc_bytes[i-1])
            tc = chr(truth_bytes[j-1])
            # Match if known mapping matches, OR if they are both spaces, OR if we just want to force a match
            is_match = (ec in known and known[ec] == tc) or (ec not in known and ec == tc)
            
            if is_match:
                dp[i][j] = dp[i-1][j-1] + 2
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1], dp[i-1][j-1] + 1)
                
    i, j = m, n
    align_enc = []
    align_tru = []
    
    while i > 0 and j > 0:
        ec = chr(enc_bytes[i-1])
        tc = chr(truth_bytes[j-1])
        is_match = (ec in known and known[ec] == tc) or (ec not in known and ec == tc)
        
        if is_match or dp[i][j] == dp[i-1][j-1] + 1:
            align_enc.append(ec)
            align_tru.append(tc)
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i-1][j]:
            align_enc.append(ec)
            align_tru.append('')
            i -= 1
        else:
            align_enc.append('')
            align_tru.append(tc)
            j -= 1
            
    while i > 0:
        align_enc.append(chr(enc_bytes[i-1]))
        align_tru.append('')
        i -= 1
    while j > 0:
        align_enc.append('')
        align_tru.append(chr(truth_bytes[j-1]))
        j -= 1
        
    align_enc.reverse()
    align_tru.reverse()
    
    mapping = {}
    conflicts = []
    log = []
    
    for e, t in zip(align_enc, align_tru):
        if e != '' and t != '':
            if e not in mapping:
                mapping[e] = t
                log.append(f"Mapped: {repr(e)} -> {repr(t)}")
            elif mapping[e] != t:
                log.append(f"CONFLICT: {repr(e)} was {repr(mapping[e])}, now {repr(t)}")
                # Ground truth wins, so overwrite
                mapping[e] = t
    
    return mapping, log

with open('/tmp/clean_g.txt', 'rb') as f:
    enc_g = f.read()
with open('/tmp/clean_a.txt', 'rb') as f:
    enc_a = f.read()

m1, log1 = lcs_align(enc_g, truth_group_rank)
m2, log2 = lcs_align(enc_a, truth_arena_top)

final_map = known.copy()
for k, v in m1.items():
    final_map[k] = v
for k, v in m2.items():
    final_map[k] = v

# Ensure all 6 digits and letters are captured
# "Digits missing: 6" -> 6 maps to 6?
if '6' not in final_map:
    final_map['6'] = '6'

with open('/tmp/substitution_table_v2.txt', 'w') as f:
    f.write("=== COMPLETE CIPHER MAPPING ===\n")
    for k in sorted(final_map.keys()):
        f.write(f"{repr(k)} -> {repr(final_map[k])}\n")

print("Created mapping. Keys mapped:", len(final_map))
