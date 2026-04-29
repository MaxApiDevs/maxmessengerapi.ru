#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import urllib.request

BASE = "https://dev.max.ru"
DOCS_PAGE = f"{BASE}/docs-api"
OUTPUT = "max-bot-api-openapi.json"

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        return content.decode('utf-8')

def fix_unicode(text: str) -> str:
    """Convert unicode escapes to normal characters"""
    def replace_unicode(match):
        return chr(int(match.group(1), 16))
    return re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, text)

def extract_openapi_json(js_text: str) -> dict | None:
    marker = "JSON.parse('"
    search_from = 0
    
    while True:
        idx = js_text.find(marker, search_from)
        if idx == -1:
            return None
        
        raw_start = idx + len(marker)
        i = raw_start
        raw_chars = []
        while i < len(js_text):
            ch = js_text[i]
            if ch == "'" and js_text[i-1] != '\\':
                break
            raw_chars.append(ch)
            i += 1
        raw = "".join(raw_chars)
        
        try:
            # First fix unicode escapes
            decoded = fix_unicode(raw)
            # Then handle other escapes
            decoded = decoded.encode('utf-8').decode('unicode_escape')
        except Exception as e:
            search_from = idx + 1
            continue
        
        if not decoded.lstrip().startswith('{"openapi"'):
            search_from = idx + 1
            continue
        
        try:
            return json.loads(decoded)
        except json.JSONDecodeError:
            search_from = idx + 1
    
    return None

def main():
    print("1. Loading documentation page...")
    html = fetch(DOCS_PAGE)
    
    chunk_paths = list(dict.fromkeys(
        re.findall(r"/_next/static/chunks/\d+-[a-f0-9]+\.js", html)
    ))
    print(f"   Found chunks: {len(chunk_paths)}")
    
    print("2. Looking for OpenAPI spec...")
    spec = None
    for path in chunk_paths:
        url = BASE + path
        print(f"   Checking: {path}")
        js_text = fetch(url)
        if '"openapi"' not in js_text:
            continue
        print(f"   Found OpenAPI in: {url}")
        spec = extract_openapi_json(js_text)
        if spec:
            break
    
    if not spec:
        raise RuntimeError("OpenAPI specification not found!")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    print(f"3. Saved to {OUTPUT}")
    print(f"   Paths: {len(spec.get('paths', {}))}")
    print(f"   Schemas: {len(spec.get('components', {}).get('schemas', {}))}")
    
    print("\n4. Checking Russian text:")
    for path in list(spec.get('paths', {}).keys())[:2]:
        for method, details in spec['paths'][path].items():
            if 'summary' in details:
                print(f"   {method.upper()} {path}: {details['summary'][:50]}")

if __name__ == "__main__":
    main()
