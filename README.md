# NEBULA CDN

**A free, open-source CDN of 2,790+ browser-playable HTML games — no downloads, no installs, just play.**

> Built & maintained by [GoatTech Industries](https://github.com/GoatTech-42)

---

## Quick Links

| Resource | URL |
|---|---|
| **Game Browser** | [`player.html`](https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main/player.html) |
| **Game Catalog (JSON API)** | [`games.json`](https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main/games.json) |
| **CDN Base URL** | `https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main/` |
| **Single Game Example** | `https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main/games/doom.html` |

---

## Source rename (2026-09-18)

This repository was renamed `NEBULA-CDN` -> `NEBULACDN`. The old jsDelivr
source URL (`cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main`) got
blocklisted; the rename gives jsDelivr a fresh source path:

- New CDN base: `https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main/`
- GitHub redirects the old repo URL, but all jsDelivr references in this repo
  (README, `player.html`, `process_games.py`) now point at the new name.
- If this path gets blocked again, rename the repo once more (single-character
  change is enough) and update the same three files.

## What Is NEBULA CDN?

NEBULA CDN is a collection of **3,076 browser games**. Most are single `.html` files that run entirely in your browser; titles tagged `cdn-streamed` stream their game files through jsDelivr from their upstream source repos. No downloads, no logins, no ads.

Every game has been:

- **Minified** — tracking scripts, analytics, and bloat removed; whitespace collapsed
- **Cataloged** — rich metadata in `games.json` with name, category, tags, file size, and hash
- **Served free** — via [jsDelivr](https://www.jsdelivr.com/)'s global CDN (backed by GitHub, no API keys needed)
- **Properly named** — Title Case display names generated from slugs

---

## Fresh additions (2026-09-18)

21 games added from current public single-file packs (source:
[CoolDude2349/Offline-HTML-Games-Pack](https://github.com/CoolDude2349/Offline-HTML-Games-Pack),
deduped against the existing catalog): Geometry Dash, Super Mario 63,
Super Mario 64, six more Minecraft browser versions (1.12 / 1.5 / 1.8 /
Alpha 1.2.6 / Beta 1.3 / Indev), Papa's Burgeria/Donuteria/Pizzeria,
Candy Crush, Minesweeper, Stack, Wordle Unlimited, Sand Game,
3D Flight Simulator, Crazy Crash Landing, Super Bike The Champion and
Super Star Car.

Note: jsDelivr refuses to serve individual files over ~20 MB. Games above
that line (incl. some of these additions and ~36 older entries) still ship
in the repo but may 403 through the CDN link; pull them from the repo
directly if needed.

## Stats

| Metric | Value |
|---|---|
| Total Games | **3,076** |
| Total Size | ~2.08 GB |
| Categories | **16** |
| File Format | Single-file HTML5 |
| CDN Provider | jsDelivr (GitHub-backed) |

---

## Categories

Categories are sorted by game count in the browser. The top categories are:

| Category | Count | Category | Count |
|---|---|---|---|
| Other | 1,802 | Platformer | 105 |
| Pokemon | 134 | Mario | 104 |
| Sonic | 74 | Racing | 72 |
| Strategy | 72 | Fighting | 71 |
| Sports | 68 | Shooter | 51 |
| Horror | 51 | Puzzle | 46 |
| Minecraft | 41 | Zelda | 37 |
| RPG | 33 | Simulation | 29 |

---

## Game Browser Features

`player.html` is a fully self-contained viewer you can host anywhere. Features include:

- **Category sidebar** — click any category to filter instantly; sorted by game count
- **Search** — search by name, category, slug, or tag; press `/` to focus
- **Sort** — A→Z, Z→A, largest first, smallest first, or by category
- **Grid & List view** — toggle between compact grid and spacious list layout
- **In-page player** — games run directly inside the page in an iframe; no new tabs needed
- **Fullscreen** — F key or the toolbar button puts the game into fullscreen
- **Stealth tab** — opens the game inside an `about:blank` tab (school-friendly)
- **New tab** — opens the raw game URL in a new browser tab
- **Infinite scroll** — automatically loads more games as you scroll
- **Keyboard shortcuts**:
  - `/` — focus the search box
  - `Esc` — close the game player (or blur search)
  - `F` — toggle fullscreen while a game is open
- **Mobile-friendly** — responsive layout with horizontal category chips on small screens
- **Loading skeleton** — shimmering placeholders shown while the catalog loads

---

## API — `games.json`

The catalog is a single JSON file served via jsDelivr:

```
https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main/games.json
```

### Top-level structure

```json
{
  "name": "NEBULA CDN",
  "version": "1.0.0",
  "generated": "2026-04-16T00:00:00Z",
  "stats": {
    "totalGames": 2790,
    "totalSizeBytes": 1714000000,
    "totalSizeMB": 1634.0,
    "categories": { "Other": 1802, "Pokemon": 134, ... }
  },
  "categories": ["Fighting", "Horror", "Mario", ...],
  "games": [ ... ]
}
```

### Game object

```json
{
  "id":           "doom",
  "name":         "Doom",
  "slug":         "doom",
  "file":         "games/doom.html",
  "filename":     "doom.html",
  "category":     "Shooter",
  "tags":         ["offline", "browser", "html5", "retro", "singleplayer"],
  "description":  "Play Doom — a shooter game playable directly in your browser. No downloads required.",
  "size":         2048576,
  "originalSize": 2500000,
  "hash":         "a1b2c3d4e5f60708"
}
```

### Fetching a game

```js
const CDN = 'https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main';
const catalog = await fetch(`${CDN}/games.json`).then(r => r.json());

// Get URL for a game
const game = catalog.games.find(g => g.slug === 'doom');
const gameUrl = `${CDN}/${game.file}`;

// Load in an iframe
document.querySelector('iframe').src = gameUrl;
```

---

## Processing Games — `process_games.py`

The `process_games.py` script processes raw HTML game files and rebuilds the catalog.

```
python3 process_games.py
```

It will:
1. **Scan** `./games/` for all `.html` files
2. **Rename** files to clean slugs (e.g. `MyGame(2).html` → `my-game.html`)
3. **Minify** each file — strips comments, analytics, and excess whitespace
4. **Generate** a proper Title Case display name from the slug
5. **Categorize** each game using keyword rules
6. **Tag** each game (offline, browser, html5, retro, multiplayer, etc.)
7. **Write** an updated `games.json` catalog, sorted alphabetically

### Category detection

Categories are assigned by matching slug keywords:

| Category | Example keywords |
|---|---|
| Minecraft | `minecraft`, `eaglercraft`, `eagler` |
| Mario | `mario`, `smb`, `luigi`, `yoshi` |
| Pokemon | `pokemon`, `poke`, `moemon` |
| Fighting | `streetfighter`, `boxing`, `brawl`, `smash`, `fighter` |
| Shooter | `doom`, `bullet`, `sniper`, `shooter`, `quake` |
| Racing | `racing`, `kart`, `drift`, `car`, `racer` |
| Sports | `soccer`, `football`, `basketball`, `nba`, `nfl` |
| Puzzle | `puzzle`, `tetris`, `sudoku`, `chess`, `match` |
| Horror | `fnaf`, `horror`, `zombie`, `creepy`, `backroom` |
| Strategy | `tower-defense`, `btd`, `war`, `tycoon` |

Unmatched games fall into **Other**.

---

## File Structure

```
NEBULA-CDN/
├── games/              # 2,790 single-file HTML games
│   ├── doom.html
│   ├── mario.html
│   └── ...
├── schema/
│   └── games.schema.json
├── games.json          # Machine-readable catalog (2790 entries)
├── player.html         # Game browser web app
├── process_games.py    # Catalog generation script
└── README.md
```

---

## Using in Your Project

### Embed a random game

```html
<script>
fetch('https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main/games.json')
  .then(r => r.json())
  .then(data => {
    const game = data.games[Math.floor(Math.random() * data.games.length)];
    const base = 'https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main';
    document.getElementById('game-frame').src = base + '/' + game.file;
    document.getElementById('game-title').textContent = game.name;
  });
</script>
<h2 id="game-title"></h2>
<iframe id="game-frame"
  sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-modals allow-pointer-lock"
  allowfullscreen
  style="width:100%;height:600px;border:none">
</iframe>
```

### Filter by category

```js
const CDN = 'https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULACDN@main';
const { games } = await fetch(`${CDN}/games.json`).then(r => r.json());

const shooters = games.filter(g => g.category === 'Shooter');
const puzzles  = games.filter(g => g.category === 'Puzzle');
```

---

## License

MIT — see [LICENSE](./LICENSE) for details.

Games are served as-is. Each game's original license and copyright belong to its respective creator.

---

*NEBULA CDN — GoatTech Industries*

## Latest additions (v1.4.0, 2026-09-18)

133 titles mined from the Horizon doc and the new Ultimate Game Stash master
doc (the current UGS distribution is launcher HTML backed by jsDelivr-hosted
asset repos). 4 ship as real single files (Block Blast 2, EaglerCraft Odd
Future, Amazing Strange Rope Police, Granny Online); the rest are tagged
`cdn-streamed` like the existing launcher-based catalog entries. Upstream
analytics (Google tag) stripped on import.

## Latest additions (v1.3.0, 2026-09-18)

125 zero-dependency single-file HTML5 games from
github.com/wangzifan396-wzf/mini-browser-games (actively maintained,
quality-tiered; tier tags included in the catalog). All under the CDN size
limit as-is.

## Latest additions (v1.2.0, 2026-09-18)

8 Eaglercraft ports from the EaglercraftNOA organization: Eaglercraft 26.2,
26.1.2 (Novix WASM), and Minecraft 1.13.2 / 1.14.4 / 1.16.5 / 1.17 / 1.20.6 /
1.21.11 WASM builds. All split for CDN delivery with
`scripts/split_large_games.py`.

## Large game splitting

jsDelivr refuses to serve files over ~20MB, so the 43 games whose original
single-file HTML exceeded that are split at build time by
`scripts/split_large_games.py`. The HTML stays the entry point; embedded
assets move to `games/assets/` and load at runtime. Five patterns are
handled: `data:application/octet-stream` (and Shockwave Flash) blobs fetched
by the page, `compressedString` JS literals, `decodeChunk` base85 script
tags, `<script id="payload">` pack loaders, `<option value>` launcher packs,
and oversized inline code scripts. Blobs over 19MB are chunked with a fetch
interceptor that reassembles them transparently. Run the script after adding
a new oversized game; it only rewrites files over the limit.
