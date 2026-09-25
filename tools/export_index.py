# -*- coding: utf-8 -*-
"""Экспорт индекса пунктов в CSV/JSON + сбор статистики."""
import json, os, csv, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, 'data', 'parsed.json'), encoding='utf-8'))
doc = d['Путь к вскрытию 4.0.txt']

rows = []
for lv in doc['levels']:
    for it in lv['items']:
        body = ' '.join(it['body']).strip()
        rows.append({
            'level': lv['level'], 'level_name': lv['name'], 'num': it['num'],
            'title': it['title'], 'amp': int(it['amp']), 'dup_num': int(it['dup']),
            'chars': it['text_len'], 'has_urls': int(bool(it['urls'])),
            'urls': ' | '.join(it['urls']), 'body': body[:4000], 'line': it['line'],
        })

csvp = os.path.join(ROOT, 'data', 'index_4.0.csv')
with open(csvp, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
json.dump(rows, open(os.path.join(ROOT, 'data', 'index_4.0.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- статистика ----
st = {}
st['items_total'] = len(rows)
st['per_level'] = {str(lv['level']): len(lv['items']) for lv in doc['levels']}
st['stubs'] = sum(1 for r in rows if r['chars'] < 25)
st['with_urls'] = sum(1 for r in rows if r['has_urls'])
st['amp'] = sum(1 for r in rows if r['amp'])
st['dup_num'] = sum(1 for r in rows if r['dup_num'])
st['empty_or_question'] = sum(1 for r in rows if r['body'].strip() in ('', '???') or r['chars'] < 12)
st['chars_median'] = sorted(r['chars'] for r in rows)[len(rows)//2]
st['title_latin'] = sum(1 for r in rows if re.search(r'[A-Za-z]', r['title']) and not re.search(r'[А-Яа-яЁё]', r['title']))
json.dump(st, open(os.path.join(ROOT, 'data', 'stats.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(st, ensure_ascii=False, indent=1))

# ---- топ слов в заголовках ----
words = collections.Counter()
for r in rows:
    for w in re.findall(r'[А-Яа-яЁёA-Za-z\-]{4,}', r['title'].lower()):
        words[w] += 1
print('\nчастые слова в заголовках:', words.most_common(25))
