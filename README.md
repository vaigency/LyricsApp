# Подстрочник – Russische Songs mitlesen

Web-App fürs Handy (und jeden Browser): Sie folgt dem Song, der gerade in Spotify läuft, und zeigt jede Zeile Wort für Wort –
Kyrillisch (betonte Silbe markiert), Aussprache in deutscher Schreibweise und deutsche Bedeutung.

**App:** https://vaigency.github.io/LyricsApp/

## Einrichtung

1. **Spotify-App** auf https://developer.spotify.com/dashboard → *Create app*
   - Redirect URI: `https://vaigency.github.io/LyricsApp/`
   - API: *Web API* anhaken
   - Client ID oben in `index.html` bei `SPOTIFY_CLIENT_ID` eintragen (ist nicht geheim).
2. **Auf dem Handy** die App-Adresse öffnen → Teilen → *Zum Home-Bildschirm*.
3. In der App ⚙︎ → *Mit Spotify verbinden* und einmalig den Claude API Key eintragen.

## Wie es funktioniert

- Spotify Web API: welcher Song läuft, an welcher Stelle (alle 1,5 s).
- [LRCLIB](https://lrclib.net): kostenlose Lyrics mit Zeitstempeln.
- Claude: übersetzt jeden Song einmal; das Ergebnis bleibt auf dem Gerät gespeichert.
  Der nächste Song in der Warteschlange wird schon vorab übersetzt.
- Läuft komplett im Browser, kein Server. Schlüssel bleiben auf dem Gerät.

## Playlist-Bibliothek (ohne API Key)

`library.enc` enthält Liedtexte und Übersetzungen der Playlist, verschlüsselt (AES-GCM, Schlüssel per PBKDF2 aus dem
Zugangscode). Freischalten: App einmal mit `#code=<Zugangscode>` am Ende der Adresse öffnen oder den Code unter ⚙︎ eintragen.

Neu bauen (Werkzeuge in `tools/`): Trackliste → `fetch_lyrics.py` → `make_batches.py` → Übersetzungen je Song als
`out/<spotify-id>.json` (geprüft mit `validate.py`) → `node tools/build_library.mjs <ordner> <code> library.enc`.
Die Rohdaten (Liedtexte, Übersetzungen) gehören nicht ins Repository.
