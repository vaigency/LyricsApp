import json, re, sys
D = sys.argv[1]
L = json.load(open(f"{D}/lyrics.json", encoding="utf8"))
songs = []
for r in L:
    txt = r["synced"] or r["plain"]
    if not txt: continue
    lines = [re.sub(r"\[[^\]]*\]", "", x).strip() for x in txt.splitlines()]
    uniq = list(dict.fromkeys(x for x in lines if re.search(r"\w", x)))
    tid = r["uri"].split(":")[-1]
    songs.append({"id": tid, "title": r["title"], "artist": r["artist"], "lines": uniq})
songs.sort(key=lambda s: -len(s["lines"]))
N = 8; batches = [[] for _ in range(N)]; load = [0] * N
for s in songs:                      # greedy balance by line count
    i = load.index(min(load)); batches[i].append(s); load[i] += len(s["lines"])
import os; os.makedirs(f"{D}/batches", exist_ok=True); os.makedirs(f"{D}/out", exist_ok=True)
for i, b in enumerate(batches):
    json.dump(b, open(f"{D}/batches/batch_{i}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(i, len(b), "songs", load[i], "lines")
