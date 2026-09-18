#!/usr/bin/env python3
"""split_large_games.py - make >20MB single-file games servable through jsDelivr.

jsDelivr refuses individual files over ~20MB. Three known packing patterns get
rewritten so the HTML shell stays small and the bulk moves to chunked assets
under games/assets/ (each chunk safely under the limit):

A. Eaglercraft-style: giant data:application/octet-stream;base64 blobs that the
   in-page loader retrieves via fetch(). Blob is extracted; if it exceeds the
   limit it is split into byte chunks and a tiny fetch() interceptor (injected
   before the game script) reassembles it at load time.
B. compressedString-style: one giant single-quoted JS string literal consumed
   synchronously. Payload moves into external chunk scripts (each a string
   piece, pushed onto a global array) loaded before the inline script; the
   literal is replaced with a join of the pieces.
C. TurboWarp/Scratch-style: thousands of <script data="...">decodeChunk(65536)
   </script> tags. The base85 payloads move to external text parts, reassembled
   by an inline loader that feeds each original chunk to the same decoder.

Files that match no known pattern are left untouched and reported.

Usage: python3 scripts/split_large_games.py [file ...]   (default: all >20MB)
"""
import base64
import os
import re
import sys

GAMES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'games')
LIMIT = 19_000_000          # keep every emitted file under jsDelivr's ~20MB wall
CHUNK = 15_000_000          # raw chunk size (bytes for blobs, chars for strings)
SEP = '\n@@NBCHUNK@@\n'

OCT_RE = re.compile(r'data:application/octet-stream;base64,([A-Za-z0-9+/=]{100000,})')
CSTR_RE = re.compile(r"(let|var|const)\s+([A-Za-z_$][\w$]*)\s*=\s*'((?:[^'\\]|\\.){1000000,})'")
B85_RE = re.compile(r'<script data="([^"]{1000,})">decodeChunk\(65536\)</script>')

FETCH_SHIM = """<script>window.__NBCHUNKS=%s;(function(){var of=window.fetch.bind(window);window.fetch=function(u,o){try{var k=typeof u==='string'?u:(u&&u.url)||'';for(var key in window.__NBCHUNKS){if(k.indexOf(key)!==-1){return Promise.all(window.__NBCHUNKS[key].map(function(p){return of(p,{cache:'force-cache'}).then(function(r){return r.arrayBuffer()})})).then(function(bs){var n=0,i;for(i=0;i<bs.length;i++)n+=bs[i].byteLength;var out=new Uint8Array(n),off=0;for(i=0;i<bs.length;i++){out.set(new Uint8Array(bs[i]),off);off+=bs[i].byteLength}return new Response(out)})}}}catch(e){}return of(u,o)}})();</script>"""


def rel_assets(slug):
    return os.path.join(GAMES, 'assets')


def safe_cuts(s, size):
    """Split string s into <=size pieces, never right after an odd backslash run
    (which would split a JS escape across chunk literals)."""
    out, i, n = [], 0, len(s)
    while i < n:
        j = min(i + size, n)
        if j < n:
            k = j
            while k > i:
                bs = 0
                p = k - 1
                while p >= 0 and s[p] == '\\':
                    bs += 1
                    p -= 1
                if bs % 2 == 0:
                    break
                k -= 1
            if k == i:
                k = j  # pathological; accept the split
            j = k
        out.append(s[i:j])
        i = j
    return out


def pattern_a(slug, txt):
    """Extract octet-stream blobs. Returns (new_txt, manifest, files) or None."""
    blobs = list(OCT_RE.finditer(txt))
    if not blobs:
        return None
    # Only safe when the page fetches the blob (eaglercraft loader marker).
    head = txt[:max(blobs[0].start(), 20000)]
    if 'fetch' not in head:
        return None
    manifest = {}
    files = {}          # relpath -> bytes
    out = txt
    for i, m in enumerate(blobs):
        raw = base64.b64decode(m.group(1))
        base = f'assets/{slug}.blob{i}.bin'
        if len(raw) <= LIMIT:
            files[base] = raw
        else:
            parts = [raw[o:o + CHUNK] for o in range(0, len(raw), CHUNK)]
            names = []
            for c, part in enumerate(parts):
                p = f'{base}.{c}'
                files[p] = part
                names.append(p)
            manifest[base] = names
        out = out.replace(m.group(0), base, 1)
    if manifest:
        shim = FETCH_SHIM % __import__('json').dumps(manifest)
        j = out.find('<script')
        out = out[:j] + shim + out[j:]
    return out, files


def pattern_b(slug, txt):
    m = CSTR_RE.search(txt)
    if not m:
        return None
    var, payload = m.group(2), m.group(3)
    pieces = safe_cuts(payload, CHUNK)
    arr = f'__NBSTR_{var}'
    files = {}
    tags = []
    for i, piece in enumerate(pieces):
        p = f'assets/{slug}.str{i}.js'
        files[p] = (f"window.{arr}=(window.{arr}||[]);window.{arr}.push('" + piece + "');\n").encode()
        tags.append(f'<script src="{p}"></script>')
    out = txt[:m.start(3) - 1] + f'window.{arr}.join("")' + txt[m.end(3) + 1:]
    anchor = out.rfind('<script', 0, m.start())
    if anchor == -1:
        return None
    out = out[:anchor] + ''.join(tags) + out[anchor:]
    return out, files


def pattern_c(slug, txt):
    runs = list(B85_RE.finditer(txt))
    if len(runs) < 3:
        return None
    attrs = [m.group(1) for m in runs]
    joined = SEP.join(attrs)
    parts = []
    buf, cur = [], 0
    for a in attrs:
        add = len(a) + (len(SEP) if buf else 0)
        if cur + add > LIMIT and buf:
            parts.append(SEP.join(buf))
            buf, cur = [], 0
        buf.append(a)
        cur += add
    if buf:
        parts.append(SEP.join(buf))
    files = {}
    for i, p in enumerate(parts):
        files[f'assets/{slug}.b85.{i}'] = p.encode()
    urls = ','.join(f"'assets/{slug}.b85.{i}'" for i in range(len(parts)))
    sep_js = "'" + SEP.replace('\\', '\\\\').replace('\n', '\\n') + "'"
    loader = ("<script>(function(){function g(u){var x=new XMLHttpRequest();x.open('GET',u,false);"
              "x.send(null);return x.responseText}var t=[" + urls + "].map(g).join(" + sep_js + ").split(" + sep_js + ");"
              "for(var i=0;i<t.length;i++){base85decode(t[i],projectDecodeBuffer,projectDecodeIndex);projectDecodeIndex+=65536}})();</script>")
    out = txt[:runs[0].start()] + loader + txt[runs[-1].end():]
    return out, files


def process(path):
    slug = os.path.basename(path)[:-5]
    txt = open(path, encoding='utf-8', errors='replace').read()
    if len(txt.encode('utf-8', errors='replace')) <= LIMIT:
        return None
    for fn in (pattern_a, pattern_b, pattern_c):
        r = fn(slug, txt)
        if r:
            new_txt, files = r
            adir = rel_assets(slug)
            os.makedirs(adir, exist_ok=True)
            for rel, data in files.items():
                with open(os.path.join(GAMES, rel), 'wb') as fh:
                    fh.write(data)
            open(path, 'w', encoding='utf-8').write(new_txt)
            return fn.__name__, len(files), sum(len(v) for v in files.values())
    return ('NOMATCH', 0, 0)


def main():
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
    else:
        targets = [os.path.join(GAMES, f) for f in os.listdir(GAMES)
                   if f.endswith('.html') and os.path.getsize(os.path.join(GAMES, f)) > 20_000_000]
    for path in sorted(targets):
        slug = os.path.basename(path)
        before = os.path.getsize(path)
        r = process(path)
        if r is None:
            print(f'SKIP   {slug} (already small)')
        elif r[0] == 'NOMATCH':
            print(f'NOMATCH {slug} ({before/1e6:.1f}MB) - needs manual pattern analysis')
        else:
            after = os.path.getsize(path)
            print(f'{r[0]:10s} {slug}: html {before/1e6:.1f}MB -> {after/1e6:.2f}MB, {r[1]} asset files ({r[2]/1e6:.1f}MB)')


if __name__ == '__main__':
    main()
