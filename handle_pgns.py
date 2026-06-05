def split_pgn(pgn: str|list[str]) -> list[str]:
    if type(pgn) == str:
        pgn = pgn.splitlines()
    pgns = [[]]
    for i, line in enumerate(pgn):
        if len(line) == 0: continue
        if i > 0:
            if line.strip() and line.strip()[0] == "[" and not pgn[i-1].strip():
                pgns.append([])
            pgns[-1].append(line)
    return pgns

def concat_pgns(merged_pgn: str, other_pgns: list):
   for game in other_pgns:
       merged_pgn += "\n" + "".join(game)
   return merged_pgn

