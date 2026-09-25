# -*- coding: utf-8 -*-
"""Сравнение 3.0 и 4.0 на уровне пунктов."""
import json, os, difflib, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, 'data', 'parsed.json'), encoding='utf-8'))

def flat(doc):
    out = {}
    seen = {}
    for lv in doc['levels']:
        for it in lv['items']:
            occ = seen.get((lv['level'], it['num']), 0)
            seen[(lv['level'], it['num'])] = occ + 1
            out[(lv['level'], it['num'], occ)] = it
    return out

A = flat(d['Путь к вскрытию 3.0.txt'])
B = flat(d['Путь к вскрытию 4.0.txt'])
only_a = sorted(set(A) - set(B))
only_b = sorted(set(B) - set(A))
def txt(it):
    return (it['title'] + '\n' + '\n'.join(it['body'])).strip()
changed, same = [], 0
for k in sorted(set(A) & set(B)):
    ta, tb = txt(A[k]), txt(B[k])
    if ta == tb:
        same += 1
    else:
        ratio = difflib.SequenceMatcher(None, ta, tb).ratio()
        changed.append((k, ratio, len(ta), len(tb), A[k]['title'][:60], B[k]['title'][:60]))

lines = ['# 3.0 → 4.0: что изменилось', '',
         f'- Пунктов в 3.0: **{len(A)}**, в 4.0: **{len(B)}**',
         f'- Идентичных пунктов: **{same}**',
         f'- Изменённых пунктов: **{len(changed)}**',
         f'- Только в 3.0: **{len(only_a)}**, только в 4.0: **{len(only_b)}**', '',
         '## Пункты, добавленные в 4.0', '']
for k in only_b:
    lines.append(f"- L{k[0]}.{k[1]} — {B[k]['title']}")
lines += ['', '## Пункты, исчезнувшие из 4.0', '']
for k in only_a:
    lines.append(f"- L{k[0]}.{k[1]} — {A[k]['title']}")
lines += ['', '## Переписанные пункты (по убыванию объёма правок)', '',
          '| уровень | было | стало | похожесть | заголовок |', '|---|---|---|---|---|']
for k, ratio, la, lb, ta, tb in sorted(changed, key=lambda x: x[1]):
    lines.append(f"| L{k[0]}.{k[1]} | {la} | {lb} | {ratio:.2f} | {tb} |")
open(os.path.join(ROOT, 'data', 'diff_3.0_4.0.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[:12]))
print()
print('переписано сильнее всего:')
for k, ratio, la, lb, ta, tb in sorted(changed, key=lambda x: x[1])[:15]:
    print(f"  L{k[0]}.{k[1]}  {ratio:.2f}  {la}->{lb}  {tb[:60]}")
print()
print('добавлено в 4.0:')
for k in only_b: print('  ', k, B[k]['title'][:70])
print('удалено из 4.0:')
for k in only_a: print('  ', k, A[k]['title'][:70])
