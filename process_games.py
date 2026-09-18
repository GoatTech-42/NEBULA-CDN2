#!/usr/bin/env python3
"""
NEBULA CDN Game Processor - Memory-Efficient Version
=====================================================
Renames, cleans, minifies, tags, and catalogs all game files.
Processes files one at a time to avoid memory issues.
"""

import os
import re
import json
import hashlib
import unicodedata
import gc
from collections import Counter
from datetime import datetime

GAMES_DIR = "games"
CATALOG_FILE = "games.json"

CATEGORY_RULES = {
    "Minecraft": ["minecraft", "eaglercraft", "minceraft", "eaglerforge", "eagler", "clayuncraft", "codercraft", "blockcraft", "helios-offline", "zetaclient", "gxclient", "dragonxclient", "astraclient", "archimedes", "tuff-client", "eb-client", "nautilusos"],
    "Sonic": ["sonic", "segasonic", "metalsonic"],
    "Mario": ["mario", "smb", "smw", "sm64", "luigi", "yoshi", "donkeykong", "dk-nes", "wario"],
    "Pokemon": ["pokemon", "poke", "moemon"],
    "Zelda": ["zelda", "oot", "botw", "link"],
    "Fighting": ["streetfighter", "ssf2", "marvel-vs", "x-men", "bleachvsnaruto", "dbz", "dragonball", "boxing", "wrestl", "brawl", "punch-out", "smash", "mortal", "tekken", "fighter", "duel"],
    "Shooter": ["doom", "cod", "cs1", "cs6", "csds", "counter-strike", "bullet", "sniper", "shooting", "shooter", "gunfight", "halo", "quake", "wolfenstein", "blood", "duke-nukem", "half-life", "codename-gordon"],
    "Racing": ["racing", "kart", "drift", "car-", "drive", "rider", "racer", "race", "bike", "motocross", "motorcycle", "excitebike", "outrun", "road-", "nascar", "truck"],
    "Sports": ["soccer", "football", "basketball", "baseball", "tennis", "hockey", "nba", "nfl", "fifa", "bowling", "cricket", "golf", "pool", "8-ball", "volleyball"],
    "Platformer": ["run3", "jump", "climb", "tower", "bounce", "dash", "flappy", "geometry-dash", "celeste", "earthworm", "crash-bandicoot", "megaman", "castlevania", "kirby", "metroid"],
    "Puzzle": ["puzzle", "2048", "tetris", "sudoku", "chess", "checkers", "maze", "match", "block-blast", "bloxorz", "sort", "escape", "riddle", "quiz"],
    "RPG": ["rpg", "quest", "adventure-", "earthbound", "chrono", "final-fantasy", "ff3", "golden-sun", "dragon-quest", "diablo", "undertale", "deltarune"],
    "Strategy": ["tower-defense", "btd", "bloons", "war", "command", "empire", "clash", "defense", "tycoon"],
    "Horror": ["fnaf", "horror", "creepy", "scary", "backroom", "baldi", "dead-", "zombie", "evil", "buckshot"],
    "Retro": ["retro", "nes", "snes", "n64", "gba", "genesis", "arcade", "atari"],
    "Simulation": ["simulator", "simulation", "farming", "cooking", "life"],
    "Action": [],
}


def clean_game_name(filename):
    """Strip file extension and produce a raw name; slugify + title_from_slug does the rest."""
    name = filename
    name = re.sub(r'\.(html|htm|txt|docx)$', '', name)
    if len(name) > 2 and name[:2] == 'cl' and (name[2:3].isupper() or name[2:3].isdigit() or name[2:3].isalpha()):
        name = name[2:]
    name = re.sub(r'\s*\(\d+\)\s*', '', name)
    name = name.replace('_', ' ')
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', name)
    name = name.replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    if not name:
        name = filename.replace('.html', '')
    return name


def title_from_slug(slug):
    """
    Convert a slug into a proper Title Case display name.
    Uses dash word boundaries and number/letter splits within segments.
    Articles (a, an, the, of, …) are kept lowercase unless they are the first word.
    """
    ARTICLES = {'a', 'an', 'the', 'and', 'or', 'but', 'of', 'in', 'on', 'at',
                'to', 'for', 'with', 'by', 'from', 'vs'}

    dash_parts = slug.split('-')
    all_words = []

    for part in dash_parts:
        if not part:
            continue
        sub = part
        # "boxing2" -> "boxing 2"
        sub = re.sub(r'([a-zA-Z]{2,})(\d+)', r'\1 \2', sub)
        # "2doom" -> "2 doom"
        sub = re.sub(r'(\d+)([a-zA-Z]{2,})', r'\1 \2', sub)
        for w in sub.split():
            if w:
                all_words.append(w)

    if not all_words:
        return slug.capitalize()

    result = []
    for i, word in enumerate(all_words):
        w_lower = word.lower()
        if i == 0 or w_lower not in ARTICLES:
            result.append(word[0].upper() + word[1:].lower())
        else:
            result.append(w_lower)

    return ' '.join(result)


def slugify(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip('-')
    return name if name else 'unknown'


def categorize_game(slug, display_name):
    combined = (slug + " " + display_name).lower()
    for category, keywords in CATEGORY_RULES.items():
        if category in ("Retro", "Action"):
            continue
        for kw in keywords:
            if kw in combined:
                return category
    return "Other"


def generate_tags(slug, display_name, file_size):
    combined = (slug + " " + display_name).lower()
    tags = ["offline", "browser", "html5"]
    tag_checks = {
        "multiplayer": ["1v1", "2-player", "2player", "multiplayer", "coop", "pvp", "1on1", "vs-"],
        "retro": ["nes", "snes", "n64", "gba", "genesis", "arcade", "atari"],
        "3d": ["3d"],
        "clicker": ["clicker", "idle", "incremental"],
        "horror": ["fnaf", "horror", "creepy", "scary", "backroom", "baldi", "zombie"],
        "emulator": ["nes", "snes", "n64", "gba", "genesis", "ds", "psx"],
    }
    for tag, keywords in tag_checks.items():
        for kw in keywords:
            if kw in combined:
                if tag not in tags:
                    tags.append(tag)
                break
    if "multiplayer" not in tags:
        tags.append("singleplayer")
    if file_size > 5_000_000:
        tags.append("large-file")
    return tags


def generate_description(display_name, category):
    return f"Play {display_name} - {category.lower()} game playable directly in your browser. No downloads required."


def strip_and_minify(content):
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    # Remove google analytics
    content = re.sub(r'<script[^>]*googletagmanager\.com[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<script>\s*window\.dataLayer.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script>\s*\(function\(i,s,o,g,r,a,m\).*?</script>', '', content, flags=re.DOTALL)
    # Remove sidebar ad divs
    content = re.sub(r'<div\s+id="sidebarad[12]".*?</div>\s*</div>', '', content, flags=re.DOTALL | re.IGNORECASE)
    # Collapse whitespace between tags  
    content = re.sub(r'>\s+<', '><', content)
    # Collapse blank lines
    content = re.sub(r'\n\s*\n+', '\n', content)
    # Strip line-level whitespace
    lines = content.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(lines)


def main():
    print("NEBULA CDN Game Processor")
    print("=" * 50)
    
    # Phase 1: Build name mapping (low memory - just strings)
    print("\n[Phase 1] Building name map...")
    all_files = sorted(os.listdir(GAMES_DIR))
    game_files = [f for f in all_files if f.endswith(('.html', '.htm', '.txt', '.docx'))]
    print(f"  Found {len(game_files)} files")
    
    slug_map = {}
    for filename in game_files:
        display_name = clean_game_name(filename)
        slug = slugify(display_name)
        if slug not in slug_map:
            slug_map[slug] = []
        slug_map[slug].append((filename, display_name))
    
    # Resolve collisions
    final_mapping = {}
    for slug, entries in slug_map.items():
        if len(entries) == 1:
            final_mapping[entries[0][0]] = (slug, entries[0][1])
        else:
            def sort_key(e):
                has_num = bool(re.search(r'\(\d+\)', e[0]))
                return (has_num, e[0])
            sorted_entries = sorted(entries, key=sort_key)
            final_mapping[sorted_entries[0][0]] = (slug, sorted_entries[0][1])
            for i, entry in enumerate(sorted_entries[1:], 2):
                final_mapping[entry[0]] = (f"{slug}-v{i}", f"{entry[1]} (v{i})")
    
    print(f"  Mapped {len(final_mapping)} files")
    del slug_map
    gc.collect()
    
    # Phase 2: Process files one at a time
    print("\n[Phase 2] Processing files...")
    catalog = []
    processed = 0
    errors = []
    
    # Sort by original filename for consistent order
    sorted_items = sorted(final_mapping.items())
    
    for original_filename, (new_slug, display_name) in sorted_items:
        original_path = os.path.join(GAMES_DIR, original_filename)
        new_filename = f"{new_slug}.html"
        new_path = os.path.join(GAMES_DIR, new_filename)
        
        try:
            # Read file
            with open(original_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            original_size = os.path.getsize(original_path)
            
            # Minify
            minified = strip_and_minify(content)
            del content
            gc.collect()
            
            # Use slug-derived Title Case name
            display_name = title_from_slug(new_slug)
            
            # Add header
            header = (
                f"<!-- NEBULA CDN | GoatTech Industries | "
                f"Game: {display_name} | "
                f"File: {new_filename} | "
                f"https://github.com/GoatTech-42/NEBULA-CDN -->\n"
            )
            final_content = header + minified
            del minified
            
            final_size = len(final_content.encode('utf-8', errors='replace'))
            content_hash = hashlib.sha256(final_content.encode('utf-8', errors='replace')).hexdigest()[:16]
            
            category = categorize_game(new_slug, display_name)
            tags = generate_tags(new_slug, display_name, final_size)
            description = generate_description(display_name, category)
            
            # Remove old file if name changed
            if original_filename != new_filename and os.path.exists(original_path):
                os.remove(original_path)
            
            # Write new file
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            del final_content
            gc.collect()
            
            catalog.append({
                "id": new_slug,
                "name": display_name,
                "slug": new_slug,
                "file": f"games/{new_filename}",
                "filename": new_filename,
                "category": category,
                "tags": tags,
                "description": description,
                "size": final_size,
                "originalSize": original_size,
                "hash": content_hash,
            })
            
            processed += 1
            if processed % 100 == 0:
                print(f"  {processed}/{len(final_mapping)}...")
                gc.collect()
            
        except Exception as e:
            errors.append((original_filename, str(e)))
    
    print(f"  Done: {processed} processed, {len(errors)} errors")
    
    # Phase 3: Cleanup orphans
    print("\n[Phase 3] Cleaning orphaned files...")
    expected = set(e["filename"] for e in catalog)
    current = set(os.listdir(GAMES_DIR))
    orphans = current - expected
    removed = 0
    for orphan in orphans:
        p = os.path.join(GAMES_DIR, orphan)
        if os.path.isfile(p):
            os.remove(p)
            removed += 1
    print(f"  Removed {removed} orphans")
    
    # Phase 4: Write catalog
    print("\n[Phase 4] Writing catalog...")
    catalog.sort(key=lambda x: x["name"].lower().lstrip('0123456789 '))
    
    cat_counts = Counter(g["category"] for g in catalog)
    total_size = sum(g["size"] for g in catalog)
    
    catalog_data = {
        "$schema": "https://raw.githubusercontent.com/GoatTech-42/NEBULA-CDN/main/schema/games.schema.json",
        "name": "NEBULA CDN",
        "description": "A free, open-source CDN of browser-playable HTML games. Hosted on GitHub and served via jsDelivr.",
        "version": "1.0.0",
        "author": "GoatTech Industries",
        "repository": "https://github.com/GoatTech-42/NEBULA-CDN",
        "cdn_base": "https://cdn.jsdelivr.net/gh/GoatTech-42/NEBULA-CDN2@main",
        "license": "MIT",
        "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stats": {
            "totalGames": len(catalog),
            "totalSizeBytes": total_size,
            "totalSizeMB": round(total_size / 1_048_576, 2),
            "categories": dict(cat_counts.most_common()),
        },
        "categories": sorted(cat_counts.keys()),
        "games": catalog,
    }
    
    with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nCOMPLETE! {processed} games, {len(cat_counts)} categories, {total_size/1048576:.1f} MB")
    if errors:
        print(f"Errors: {len(errors)}")
        for fn, err in errors[:10]:
            print(f"  {fn}: {err}")
    
    return catalog_data


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
