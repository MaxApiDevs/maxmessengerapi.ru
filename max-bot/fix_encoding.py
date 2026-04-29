#!/usr/bin/env python3
import json
import re

# Читаем испорченный файл
with open('max-bot-api-openapi.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Функция для исправления кракозябр
def fix_russian(text):
    if not isinstance(text, str):
        return text
    
    # Пробуем разные варианты декодирования
    try:
        # Пробуем исправить через latin1 -> utf-8
        fixed = text.encode('latin1').decode('utf-8')
        if any('\u0400' <= c <= '\u04FF' for c in fixed):
            return fixed
    except:
        pass
    
    try:
        # Пробуем через cp1251
        fixed = text.encode('latin1').decode('cp1251')
        if any('\u0400' <= c <= '\u04FF' for c in fixed):
            return fixed
    except:
        pass
    
    return text

# Рекурсивно обходим все строки
def fix_dict(obj):
    if isinstance(obj, dict):
        return {fix_dict(k): fix_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_dict(item) for item in obj]
    elif isinstance(obj, str):
        return fix_russian(obj)
    else:
        return obj

# Загружаем JSON
print("Загрузка JSON...")
data = json.loads(content)

print("Исправление кодировки...")
data_fixed = fix_dict(data)

# Сохраняем исправленный файл
with open('max-bot-api-openapi-fixed.json', 'w', encoding='utf-8') as f:
    json.dump(data_fixed, f, ensure_ascii=False, indent=2)

print("Сохранено в max-bot-api-openapi-fixed.json")

# Проверяем результат
print("\nПроверка исправленного текста:")
for path in list(data_fixed.get('paths', {}).keys())[:2]:
    for method, details in data_fixed['paths'][path].items():
        if 'summary' in details:
            print(f"{method.upper()} {path}: {details['summary'][:50]}")
