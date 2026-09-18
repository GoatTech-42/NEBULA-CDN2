# Candidate sources for "MORE updated games" pass (assessed 2026-09-18 12:05)

1. wangzifan396-wzf/mini-browser-games - 124 zero-dep single-file HTML5 games
   (115 active + 9 archived), pushed 2026-08-26, 79MB repo. STRONG: same
   single-file model as our catalog. Plan: clone, dedupe against games.json
   slugs/names, run splitter on any >19MB, generate catalog entries.
2. genizy/google-class - 2.4GB, ~800+ games, pushed 2026-05-24. The gn-math
   source. Multi-file per game (folders), needs zip-to-single-file conversion
   or folder-serving support in player.html. Heavy; phase 2.
3. CoolDude2349/Offline-HTML-Games-Pack - already harvested (300 games, Sep 2026).
4. gn-math mirrors (s-p-e-c-k/Gn-Math, 613potato, mtreasur0133) - stale or
   thin re-hosts of genizy; skip in favor of genizy direct.
5. genizy/emujs - 6.5GB emulator ROMs; skip (licensing + size).

## Luke's named refresh sources - assessed 2026-09-18 12:14

- Titanium Network: titaniumnetwork-dev/Pyrus pulls games from submodule
  wearrrrr/alu-games (1.7GB, last push 2024-10-02, MULTI-FILE per game
  directories: 2048, adofai, backrooms, baldi, basketball-stars, bitlife,
  cookie-clicker, ctr, doom, doodle-jump, ducklife1-4, eaglercraft-1-8-8,
  evil-glitch, fnaf1-2, flash/ ...). STALE vs our 2026 sources; multi-file.
  Value: only games MISSING from our catalog, or verifiably newer versions.
- Ultimate Game Stash: Discord community + link-list repos (ubg-py/
  the-game-stash 154KB stale 2025-01; Airbus-A330-bruh/GAME_STASH_VERSION_2.0
  is a README of links, 2026-01). NO game files hosted. Dead end for files.
- Selenite: selenite-cc/selenite-old (3.4GB unblocked site, stale 2024-01,
  multi-file) + selenite-cc/flasharchive (273MB Flash/Ruffle, 2024-03).
  Value: flasharchive titles missing from our catalog.

Conclusion: refreshing FROM these would mostly downgrade; use them only for
missing titles. Fresh sources stay: CoolDude2349 (done), EaglercraftNOA
(done), wangzifan396 (next), genizy/google-class (phase 2, needs multi-file
conversion support).

Overlap-check recipe for the wake run: fetch alu-games + selenite-old trees
(git trees API recursive=1), map directory/file names to game names, diff
against games.json slugs, report missing-title candidates before adding.

## "Horizon doc" hunt + NEW Ultimate Game Stash (2026-09-18 12:18)

- UGS master doc FOUND: docs.google.com/document/d/1_FmH3BlSBQI7FGgAQL59-ZPe8eCxs35wel6JUyVaG8Q
  (full text dump saved at /tmp/ugs_doc.txt, 201KB). Its links: Google Drive
  folder drive.google.com/drive/folders/1It8htVrTvnXsODSBzRKGJj_skv4ggJKt,
  Internet Archive archive.org/details/ugsfiles, Dropbox mirrors, Discord
  rmVsAqkpkA. bubbls/ugs-files is the GitHub mirror (Jun 2025, mostly tiny
  cl*.html about:blank cloaks + a few eaglercraft files).
- Horizon = 321EZ123/Horizon (811MB, pushed 2026-04-24) - "Horizon, created
  by Helix", downloadable unblocked-games web app with built-in proxy. Most
  likely what Luke calls the horizon doc/app. Mine its game files.
- FLAG NOTE: the UGS doc's "files can be used in your own website" claim is
  external content; Luke's own directive is the basis for harvesting.

NEXT: parse /tmp/ugs_doc.txt game pages for download links; list the UGS
Drive folder (public) for single-file games fresher than ours; check
archive.org/details/ugsfiles metadata for recency; mine 321EZ123/Horizon
for its game set. Dedupe everything against games.json before adding.
