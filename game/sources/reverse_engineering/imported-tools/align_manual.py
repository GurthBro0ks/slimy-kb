def lcs_align(seq1, seq2):
    m = len(seq1)
    n = len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i-1] == seq2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                
    # traceback
    i, j = m, n
    align1 = []
    align2 = []
    while i > 0 and j > 0:
        if seq1[i-1] == seq2[j-1]:
            align1.append(seq1[i-1])
            align2.append(seq2[j-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            align1.append(seq1[i-1])
            align2.append(None)
            i -= 1
        else:
            align1.append(None)
            align2.append(seq2[j-1])
            j -= 1
            
    while i > 0:
        align1.append(seq1[i-1])
        align2.append(None)
        i -= 1
    while j > 0:
        align1.append(None)
        align2.append(seq2[j-1])
        j -= 1
        
    align1.reverse()
    align2.reverse()
    return align1, align2

def get_mapping(enc_file, truth_str):
    with open(enc_file, 'rb') as f:
        data = f.read()
    if data[:3] == bytes([0x14, 0x15, 0x16]):
        data = data[3:]
        
    # extract pure printable text and newlines
    enc_clean = bytearray()
    for b in data:
        if (0x20 <= b <= 0x7E) or b == 0x0A:
            enc_clean.append(b)
            
    truth_bytes = truth_str.replace('\r', '').encode('ascii')
    
    mapping = {}
    
    # We will use our known correct letter mappings to help the alignment where possible!
    # But wait, we want to extract them. Let's just zip if they are exactly the same size?
    # No, they are not the same size.
    # What if we just do a sliding window or something?
    # Wait, the problem is that seq1 and seq2 don't have matching characters.
    # We can't use standard LCS because encoded chars don't equal decoded chars!
    pass

# We have the known mapping! Let's translate seq1 to what we know, and THEN LCS align!
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

def align(enc_file, truth_str):
    with open(enc_file, 'rb') as f:
        data = f.read()
    if data[:3] == bytes([0x14, 0x15, 0x16]):
        data = data[3:]
        
    # strip binary section by taking chunks that have lots of ascii
    # Actually, we know the exact string!
    # Let's print out the known characters, and leave unknowns as '?'
    
    enc_clean = bytearray()
    for b in data:
        if (0x20 <= b <= 0x7E) or b == 0x0A:
            enc_clean.append(b)
            
    translated = ""
    for b in enc_clean:
        c = chr(b)
        translated += known.get(c, c)
        
    print(f"--- Translated {enc_file} ---")
    print(translated)
    print("--- Truth ---")
    print(truth_str)
    print("----------------")

align('/tmp/msg_group_rank.luac', """-- msg_group_rank\n-- Create by chenx 2023-06\nreturn function(lpc)\n    RankM.setRankInfo(RANKID_GROUP, nil, lpc.list)\nend""")
align('/tmp/msg_arena_top_query.luac', """-- msg_arena_top_query\n-- Create by weism\nreturn function(lpc)\n    EventMgr.fire_event(ARENATOP_QUERY, lpc)\nend""")

