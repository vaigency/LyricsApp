"""Usage: python3 validate.py <batch.json> <out_dir>  — checks every song of the batch has a complete translation file."""
import json, re, sys, unicodedata, os
batch = json.load(open(sys.argv[1], encoding="utf8")); out = sys.argv[2]
def toks(line):
    ws = [re.sub(r"^[^\w]+|[^\w]+$", "", w) for w in line.split()]
    return [w for w in ws if w]
errors = 0
for s in batch:
    p = os.path.join(out, s["id"] + ".json")
    if not os.path.exists(p): print(f"MISSING {s['id']}.json  ({s['artist']} — {s['title']})"); errors += 1; continue
    try: d = json.load(open(p, encoding="utf8"))
    except Exception as e: print(f"INVALID JSON {p}: {e}"); errors += 1; continue
    if not d.get("summary"): print(f"{s['id']}: missing summary"); errors += 1
    lines = d.get("lines", {})
    for ln in s["lines"]:
        e = lines.get(ln)
        if not e: print(f"{s['id']}: missing line: {ln!r}"); errors += 1; continue
        if not e.get("de"): print(f"{s['id']}: empty de for {ln!r}"); errors += 1
        ws = e.get("words") or []
        for w in ws:
            if set(w) != {"ru", "stress", "lat", "de"}: print(f"{s['id']}: bad word keys {w}"); errors += 1; break
            if unicodedata.normalize("NFC", w["stress"].replace("́", "")) != unicodedata.normalize("NFC", w["ru"]):
                print(f"{s['id']}: stress form differs from ru: {w['ru']!r} vs {w['stress']!r}"); errors += 1
        if len(ws) != len(toks(ln)): print(f"{s['id']}: word count {len(ws)} != {len(toks(ln))} in {ln!r}"); errors += 1
print("OK" if errors == 0 else f"{errors} problem(s)")
