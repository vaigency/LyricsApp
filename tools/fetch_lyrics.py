import json, re, sys, time, urllib.parse, urllib.request
D = sys.argv[1]
tracks = json.load(open(f"{D}/tracks.json", encoding="utf8"))
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "LyricsApp personal (github.com/vaigency/LyricsApp)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        return None if e.code == 404 else (_ for _ in ()).throw(e)
def clean(t): return re.sub(r"\s*[\(\[](feat|ft|remix|prod)[^\)\]]*[\)\]]", "", t, flags=re.I).strip()
res, seen = [], set()
for t in tracks:
    if t["uri"] in seen: continue
    seen.add(t["uri"])
    first = t["artist"].split(",")[0].strip()
    dur = t["dur"] / 1000
    rec = get("https://lrclib.net/api/get?" + urllib.parse.urlencode({"track_name": t["title"], "artist_name": first, "duration": round(dur)}))
    if not (rec and rec.get("syncedLyrics")):
        cands = []
        for q in [{"track_name": clean(t["title"]), "artist_name": first}, {"q": f"{first} {clean(t['title'])}"}]:
            cands += get("https://lrclib.net/api/search?" + urllib.parse.urlencode(q)) or []
            time.sleep(0.2)
        good = [c for c in cands if c.get("syncedLyrics") and abs(c["duration"] - dur) < 8]
        good.sort(key=lambda c: abs(c["duration"] - dur))
        rec = good[0] if good else (rec or next((c for c in cands if c.get("plainLyrics") and abs(c["duration"] - dur) < 8), None))
    status = "synced" if rec and rec.get("syncedLyrics") else ("plain" if rec and rec.get("plainLyrics") else ("instrumental" if rec and rec.get("instrumental") else "none"))
    res.append({**t, "status": status, "lrclib_id": rec and rec.get("id"), "synced": rec and rec.get("syncedLyrics"), "plain": rec and rec.get("plainLyrics")})
    print(f"{status:8} {t['artist']} — {t['title']}", flush=True)
    time.sleep(0.25)
json.dump(res, open(f"{D}/lyrics.json", "w", encoding="utf8"), ensure_ascii=False)
from collections import Counter; print(Counter(r["status"] for r in res))
