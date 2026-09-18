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
