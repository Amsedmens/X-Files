# -*- coding: utf-8 -*-
"""Проверка живости всех внешних ссылок из архива.

Требует открытого исходящего доступа в интернет (из закрытой песочницы curl отдаёт код 000).
Запуск:  python3 tools/check_links.py
Результат: data/links.json (все проверки) и data/links_alive.json (2xx).
"""
import json, os, re, subprocess, concurrent.futures as cf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = re.compile(r'(?:https?://|www\.)[^\s\)\]\>,]+')

def norm(u):
    u = u.rstrip('.,;')
    if u.startswith('www.'):
        u = 'http://' + u
    return u

def check(u):
    cmd = ['curl', '-sS', '-L', '--max-time', '12', '--connect-timeout', '6',
           '-o', '/dev/null', '-w', '%{http_code} %{url_effective} %{num_redirects}',
           '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36',
           u]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        out = r.stdout.strip().split(' ')
        code, eff, redir = (out + ['', '', ''])[:3]
        err = r.stderr.strip()[:120]
    except Exception as e:
        code, eff, redir, err = '', '', '', str(e)[:120]
    return {'url': u, 'code': code, 'final': eff, 'redirects': redir, 'err': err}

def main():
    urls = {}
    for f in ['Путь к вскрытию 3.0.txt', 'Путь к вскрытию 4.0.txt', 'AltYoutube3.txt']:
        t = open(os.path.join(ROOT, f), encoding='utf-8-sig', newline='').read()
        for u in URL.findall(t):
            urls.setdefault(norm(u), set()).add(f)
    lst = sorted(urls)
    print('checking', len(lst), 'urls')
    res = []
    with cf.ThreadPoolExecutor(max_workers=24) as ex:
        for i, r in enumerate(ex.map(check, lst), 1):
            r['files'] = sorted(urls[r['url']])
            res.append(r)
            if i % 25 == 0:
                print(' ', i, flush=True)
    json.dump(res, open(os.path.join(ROOT, 'data', 'links.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    from collections import Counter
    c = Counter(r['code'] for r in res)
    print('codes:', c.most_common())
    ok = [r for r in res if r['code'].startswith('2')]
    dead = [r for r in res if not r['code'].startswith('2')]
    print(f'alive(2xx): {len(ok)}  other: {len(dead)}')
    json.dump(ok, open(os.path.join(ROOT, 'data', 'links_alive.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
