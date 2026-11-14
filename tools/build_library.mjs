// Usage: node build_library.mjs <pl dir> <access code> <output library.enc>
// Bundles lyrics + translations per Spotify track id, gzips, encrypts with AES-GCM (key: PBKDF2-SHA256, 200k iterations).
import fs from "node:fs"; import zlib from "node:zlib"; import { webcrypto as crypto } from "node:crypto";
const [dir, code, outFile] = process.argv.slice(2);
const tracks = JSON.parse(fs.readFileSync(`${dir}/lyrics.json`, "utf8"));
const parseLRC = (lrc) => {
  const out = [];
  for (const raw of lrc.split(/\r?\n/)) {
    const stamps = [...raw.matchAll(/\[(\d+):(\d+(?:[.:]\d+)?)\]/g)]; if (!stamps.length) continue;
    const text = raw.replace(/\[[^\]]*\]/g, "").trim();
    for (const m of stamps) out.push([Math.round((+m[1] * 60 + parseFloat(m[2].replace(":", "."))) * 1000), text]);
  }
  return out.sort((a, b) => a[0] - b[0]);
};
const lib = {}; let missing = 0;
for (const t of tracks) {
  if (!t.synced && !t.plain) continue;
  const id = t.uri.split(":").pop(), f = `${dir}/out/${id}.json`;
  if (!fs.existsSync(f)) { console.log("no translation:", t.artist, "—", t.title); missing++; continue; }
  const g = JSON.parse(fs.readFileSync(f, "utf8"));
  const lines = t.synced ? parseLRC(t.synced) : t.plain.split(/\r?\n/).map((x, i) => [i * 4000, x.trim()]);
  lib[id] = { title: t.title, artist: t.artist, synced: !!t.synced, lines, summary: g.summary, byText: g.lines };
}
const gz = zlib.gzipSync(Buffer.from(JSON.stringify(lib)), { level: 9 });
const salt = crypto.getRandomValues(new Uint8Array(16)), iv = crypto.getRandomValues(new Uint8Array(12));
const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(code), "PBKDF2", false, ["deriveKey"]);
const key = await crypto.subtle.deriveKey({ name: "PBKDF2", salt, iterations: 200000, hash: "SHA-256" }, base, { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
const ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, gz));
fs.writeFileSync(outFile, Buffer.concat([salt, iv, ct]));
console.log(`${Object.keys(lib).length} songs, ${missing} without translation, ${(gz.length / 1024).toFixed(0)} KB`);
