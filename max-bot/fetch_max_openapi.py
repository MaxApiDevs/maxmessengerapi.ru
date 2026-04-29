# fetch_max_openapi.py
# Запуск: python fetch_max_openapi.py
# Зависимости: только стандартная библиотека

import re
import json
import urllib.request

BASE = "https://dev.max.ru"
DOCS_PAGE = f"{BASE}/docs-api"
OUTPUT = "max-bot-api-openapi.json"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def extract_openapi_json(js_text: str) -> dict | None:
    marker = "JSON.parse('"
    search_from = 0

    while True:
        idx = js_text.find(marker, search_from)
        if idx == -1:
            return None

        raw_start = idx + len(marker)
        # Собираем сырую строку до закрывающей неэкранированной '
        i = raw_start
        raw_chars = []
        while i < len(js_text):
            ch = js_text[i]
            if ch == "'" and js_text[i - 1] != "\\":
                break
            raw_chars.append(ch)
            i += 1
        raw = "".join(raw_chars)

        # Декодируем JS escape-последовательности
        try:
            json_str = raw.encode("utf-8").decode("unicode_escape")
        except Exception:
            search_from = idx + 1
            continue

        if not json_str.lstrip().startswith('{"openapi"'):
            search_from = idx + 1
            continue

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            search_from = idx + 1


def main():
    print("1. Загружаем страницу документации...")
    html = fetch(DOCS_PAGE)

    chunk_paths = list(dict.fromkeys(
        re.findall(r"/_next/static/chunks/\d+-[a-f0-9]+\.js", html)
    ))
    print(f"   Найдено чанков: {len(chunk_paths)}")

    print("2. Ищем чанк с OpenAPI спецификацией...")
    spec = None
    for path in chunk_paths:
        url = BASE + path
        js_text = fetch(url)
        if '"openapi"' not in js_text:
            continue
        print(f"   Найден: {url}")
        spec = extract_openapi_json(js_text)
        if spec:
            break

    if not spec:
        raise RuntimeError("OpenAPI спецификация не найдена!")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    print(f"3. Сохранено в {OUTPUT}")
    print(f"   Путей: {len(spec.get('paths', {}))}")
    print(f"   Схем: {len(spec.get('components', {}).get('schemas', {}))}")


if __name__ == "__main__":
    main()