# -*- coding: utf-8 -*-
"""Парсер 'Путь к вскрытию' (3.0 / 4.0) -> структурированный JSON."""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEVEL_HEADER = re.compile(r'^\s*(?:Вскрыт\w*\s+(\d+)\s*-?\s*ГО\s+УРОВНЯ|УРОВЕНЬ\s+(\d+)|(\d+)\s*уровень)\s*$', re.I)
LEVEL_NAMES = {
    '1': 'Вскрытие 1-го уровня',
    '2': 'Глубокий исследователь',
    '3': 'Агент правды',
    '4': 'Принятие секретов',
    '5': 'АниМастер',
    '6': '(без названия)',
    '7': 'Межпространственный монах',
    '8': 'Хакер реальности',
}
ITEM = re.compile(r'^\s*(\d{1,3})\s*[\.\)]\s*(\S.*)$')
URL  = re.compile(r'(?:https?://|www\.)[^\s\)\]\>,]+')

def parse(path):
    text = open(os.path.join(ROOT, path), encoding='utf-8-sig', newline='').read()
    lines = text.split('\r\n')
    doc = {'file': path, 'bytes': os.path.getsize(os.path.join(ROOT, path)),
           'lines': len(lines), 'levels': [], 'preamble': [], 'appendix': []}
    cur_level = None
    cur_item = None
    in_appendix = False
    seen_items = set()

    def flush_item():
        nonlocal cur_item
        if cur_item:
            cur_level['items'].append(cur_item)
            cur_item = None

    def flush_level():
        nonlocal cur_level
        flush_item()
        if cur_level:
            doc['levels'].append(cur_level)
            cur_level = None

    for idx, raw in enumerate(lines, 1):
        s = raw.strip()
        if 'НИЖЕ НЕФОРМАТИРОВАННЫЙ' in s:
            in_appendix = True
        m = LEVEL_HEADER.match(s)
        if m and not in_appendix:
            lvl = next(g for g in m.groups() if g)
            flush_level()
            cur_level = {'level': int(lvl), 'name': LEVEL_NAMES.get(lvl, ''), 'line': idx, 'items': [], 'desc': []}
            seen_items = set()
            continue
        if in_appendix:
            doc['appendix'].append(s)
            continue
        if cur_level is None:
            doc['preamble'].append(s)
            continue
        if not s:
            if cur_item:
                cur_item['body'].append('')
            continue
        mi = ITEM.match(s)
        if mi and len(mi.group(1)) <= 3 and (not cur_item or True):
            num, title = mi.group(1), mi.group(2)
            flush_item()
            cur_item = {'num': int(num), 'num_raw': num, 'title': title.strip(),
                        'line': idx, 'body': [], 'urls': [], 'amp': '(&)' in title,
                        'dup': (int(num) in seen_items)}
            seen_items.add(int(num))
            continue
        if cur_item:
            cur_item['body'].append(s)
            cur_item['urls'] += URL.findall(s)
        else:
            cur_level['desc'].append(s)
            cur_level.setdefault('urls', [])
            cur_level['urls'] += URL.findall(s)
    flush_level()
    # post
    for lv in doc['levels']:
        for it in lv['items']:
            it['urls'] = sorted(set(it['urls']))
            it['text_len'] = len(it['title']) + sum(len(b) for b in it['body'])
    return doc

def main():
    out = {}
    for f in ['Путь к вскрытию 3.0.txt', 'Путь к вскрытию 4.0.txt']:
        d = parse(f)
        out[f] = d
        print(f"== {f}")
        print("  levels:", [(l['level'], len(l['items'])) for l in d['levels']])
        print("  total items:", sum(len(l['items']) for l in d['levels']))
        print("  appendix lines:", len(d['appendix']), " preamble lines:", len([x for x in d['preamble'] if x]))
        nd = sum(1 for l in d['levels'] for i in l['items'] if i['dup'])
        print("  dup numbers:", nd, " amp-marked:", sum(1 for l in d['levels'] for i in l['items'] if i['amp']))
        empty = sum(1 for l in d['levels'] for i in l['items'] if i['text_len'] < 25)
        print("  'empty' stubs (<25 chars):", empty)
    with open(os.path.join(ROOT, 'data', 'parsed.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("written data/parsed.json")

if __name__ == '__main__':
    main()
