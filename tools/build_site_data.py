# -*- coding: utf-8 -*-
"""Сборка site/data.json из всех наработок."""
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
load = lambda n: json.load(open(P('data', n), encoding='utf-8'))

parsed = load('parsed.json')
p40 = parsed['Путь к вскрытию 4.0.txt']
p30 = parsed['Путь к вскрытию 3.0.txt']
verdicts = load('verdicts.json')
puzzles = load('puzzles.json')
url_problems = load('url_problems.json')
stats = load('stats.json')

# ---- опечатки и артефакты (курируемый список, с автоматическим подсчётом) ----
TYPOS = [
    ('Вскрыте 1-ГО УРОВНЯ', 'Вскрытие 1-ГО УРОВНЯ', 'заголовок 1-го уровня в 2.0/3.0 (в 4.0 исправлен)'),
    ('контороль', 'контроль', 'L8.27 Elite controls'),
    ('теорри', 'теорий', 'L8.15 «Куча теорри об Антарктиде»'),
    ('умерал', 'умирал', 'финал архива, «God\'s last wish»'),
    ('Страная', 'Странная', 'L7.6 «Страная болезнь Шанина Изом»'),
    ('polson', 'poison', 'L8.56 Air is polson (порча латиницы)'),
    ('Acosmlsm', 'Acosmism', 'L4.46'),
    ('Triasslc', 'Triassic', 'L4.60'),
    ('Intcrdimenslonal', 'Interdimensional', 'L5.23'),
    ('Die Clocke', 'Die Glocke', 'L3.34'),
    ('Отредачить', 'Отредактировать', 'пометка-таск L3.19'),
    ('\u00a0', ' ', 'неразрывные пробелы из вставки'),
]
raw40 = open(P('Путь к вскрытию 4.0.txt'), encoding='utf-8-sig', newline='').read()
typo_report = []
for bad, good, comment in TYPOS:
    n = raw40.count(bad)
    if n:
        typo_report.append({'bad': bad, 'good': good, 'count': n, 'comment': comment})

# ---- аномалии структуры ----
items = []
dup_items = []
stub_items = []
for lv in p40['levels']:
    for it in lv['items']:
        vid = f"L{lv['level']}.{it['num']}"
        v = verdicts['items'].get(vid)
        rec = {
            'id': vid, 'level': lv['level'], 'level_name': lv['name'],
            'num': it['num'], 'title': it['title'], 'body': '\n'.join(it['body']).strip(),
            'urls': it['urls'], 'amp': it['amp'], 'dup': it['dup'],
            'chars': it['text_len'], 'line': it['line'],
        }
        if v:
            rec['verdict'] = {'cat': v['cat'], 'text': v['verdict'], 'sources': v.get('sources', [])}
        items.append(rec)
        if it['dup']:
            dup_items.append(vid)
        if it['text_len'] < 25:
            stub_items.append(vid)

levels_meta = [
    {'level': 1, 'name': 'Вскрытие 1-го уровня', 'orig': 'Tier 1: Crazyhead', 'desc': 'Мейнстримные конспирологии и неразгаданные дела.'},
    {'level': 2, 'name': 'Глубокий исследователь', 'orig': 'Tier 2: Deep Researcher', 'desc': 'Уровень «Сумеречной зоны»: изучаемо по мейнстрим-источникам, но требует контекста.'},
    {'level': 3, 'name': 'Агент правды', 'orig': 'Tier 3: Truth Agent', 'desc': '«Точка невозврата»: с этой точки вы выглядите безумцем для обычных людей.'},
    {'level': 4, 'name': 'Принятие секретов', 'orig': 'Tier 4: Adept of Secrets', 'desc': 'Оккультные учения и «зловещие» начала. В русском переводе название потеряло «адепта».'},
    {'level': 5, 'name': 'АниМастер', 'orig': 'Tier 5: Animaster', 'desc': 'Знание, спрятанное на виду или в древних текстах.'},
    {'level': 6, 'name': '(без названия)', 'orig': 'Tier 6: Transcended', 'desc': 'В русской версии название уровня потерялось — это и есть оригинальный Tier 6 «Transcended».'},
    {'level': 7, 'name': 'Межпространственный монах', 'orig': 'Tier 7: Interdimensional Monk', 'desc': 'Тот, кто видит всю картину и отличает реальность от нереальности.'},
    {'level': 8, 'name': 'Хакер реальности', 'orig': 'Tier 8: Reality Hacker', 'desc': 'На предельных глубинах структура реальности исчезает.'},
]

provenance = [
    {'date': '2017 (апрель)', 'text': 'Англоязычный «Conspiracy Theory Tier List» (Tier 1 Crazyhead … Tier 10 The Rebirth) обсуждают на r/conspiracy: спорят, почему Cicada 3301 попала в последний тир.', 'src': 'https://www.reddit.com/r/conspiracy/comments/63skmv/any_info_about_some_of_these_theories/'},
    {'date': '2018-10-27', 'text': 'Самая ранняя сохранённая копия оригинальной пасты (pastebin B6NrUiVt) в Wayback Machine — в ней список с ссылками по каждому пункту.', 'src': 'http://web.archive.org/web/20181027*/https://pastebin.com/B6NrUiVt'},
    {'date': '2018-12-08', 'text': 'Картинку со списком выкладывают на r/coolguides («Conspiracy Theories tiers») — начинается вирусное распространение.', 'src': 'https://www.reddit.com/r/coolguides/comments/a4dj4c/conspiracy_theories_tiers/'},
    {'date': '2019-06-07', 'text': 'Аноним публикует русский перевод «Путь к вскрытию 2.0» (pastebin M5rbLuF6) — 213 КБ, ~1983 строки, номера строк из редактора сохранились внутри текста. Просмотров сейчас: 2822. Паста жива.', 'src': 'https://pastebin.com/M5rbLuF6'},
    {'date': '2021-06-02 / 26', 'text': 'Amsedmens форматирует перевод: «Было ~2000 строк → 1900 → 1800», версия 3.0. Опечатка «Вскрыте 1-ГО УРОВНЯ» унаследована из 2.0.', 'src': 'см. заголовок файла 3.0'},
    {'date': '2022-09-24', 'text': 'Pastebin признаёт английский оригинал (B6NrUiVt) «потенциально вредным» и блокирует его. Русская ветка архива остаётся старшей живой версией.', 'src': 'https://pastebin.com/B6NrUiVt'},
    {'date': '2022-06 (?)', 'text': 'Собирается версия 4.0: 13 пунктов получают развёрнутые описания (по объёму +200…+490 символов), сверху появляется таблица «рейтинг достоверности» из 16 строк.', 'src': 'данные diff_3.0_4.0.md'},
    {'date': '2024-05-30', 'text': 'Репозиторий X-Files обновляется: добавлен AltYoutube3.txt — аудит ~100 YouTube-каналов «альтернативных исследователей» (3-я итерация, 30.05.24).', 'src': 'https://github.com/Amsedmens/X-Files'},
    {'date': '2026-09-25', 'text': 'Появление индекса: 492 пункта разобраны на структуру, собрана карта ссылок и этот разбор.', 'src': ''},
]

link_samples = [
    {'url': 'https://pastebin.com/M5rbLuF6', 'status': 'жива', 'note': 'Источник — русский «Путь к вскрытию 2.0» (7 июня 2019, гость, 213.30 КБ, 2822 просмотра).'},
    {'url': 'https://pastebin.com/B6NrUiVt', 'status': 'удалена модерацией', 'note': 'Английский оригинал со ссылками. Pastebin снял его 24.09.2022 как «potentially harmful». В Wayback сохранилась только страница-предупреждение.'},
    {'url': 'https://ifunny.co/meme/conspiracy-theory-tier-list-i-will-be-using-this-list-kezr6uZA8', 'status': 'жива', 'note': 'Полный текст интро всех десяти тиров (Tier 1…Tier 10) — благодаря ему восстановлено название потерянного 6-го уровня.'},
    {'url': 'https://www.reddit.com/r/coolguides/comments/a4dj4c/conspiracy_theories_tiers/', 'status': 'жива', 'note': 'Пост, с которого картинка ушла в вирус.'},
]
youtube_audit = {
    'title': 'AltYoutube3.txt — аудит каналов (30.05.24)',
    'lines': [
        'Из ~100 каналов с прошлого листа (апрель 2022 – 17.03.23): живых — 44, забанено — 2, умерло — 2, «пропало без вести» — 52.',
        'На май 2024: забанено — 4, заброшено — 4.',
        'Зафиксировано 3 случая массовой самоотписки от каналов.',
        'Хроника в файле делится на «идейные», «возможно коммерческие», «коммерческие», «архивные», «заброшенные» и «забаненные».',
    ]
}

site = {
    'generated': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
    'source': {
        'files': [
            {'name': 'Путь к вскрытию 4.0.txt', 'bytes': os.path.getsize(P('Путь к вскрытию 4.0.txt')), 'lines': len(raw40.split('\r\n'))},
            {'name': 'Путь к вскрытию 3.0.txt', 'bytes': os.path.getsize(P('Путь к вскрытию 3.0.txt')), 'lines': len(open(P('Путь к вскрытию 3.0.txt'), encoding='utf-8-sig', newline='').read().split('\r\n'))},
            {'name': 'AltYoutube3.txt', 'bytes': os.path.getsize(P('AltYoutube3.txt'))},
            {'name': 'README.md', 'bytes': os.path.getsize(P('README.md'))},
        ]
    },
    'stats': stats,
    'levels': levels_meta,
    'items': items,
    'integrity': {
        'typos': typo_report,
        'url_problems_count': len(url_problems),
        'url_problems': url_problems,
        'dup_items': dup_items,
        'stub_count': len(stub_items),
        'stubs_by_level': {str(l): sum(1 for i in stub_items if i.startswith(f'L{l}.')) for l in range(1, 9)},
    },
    'verdicts_legend': verdicts['legend'],
    'provenance': provenance,
    'puzzles': puzzles,
    'link_samples': link_samples,
    'youtube_audit': youtube_audit,
    'diff_md': open(P('data', 'diff_3.0_4.0.md'), encoding='utf-8').read(),
}
os.makedirs(P('site'), exist_ok=True)
json.dump(site, open(P('site', 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False)
size = os.path.getsize(P('site', 'data.json')) / 1024
print(f'site/data.json: {size:.0f} KB; items={len(items)}; verdicts={sum(1 for i in items if "verdict" in i)}; dup={len(dup_items)}; stubs={len(stub_items)}')
print('typos found:', len(typo_report))
for t in typo_report:
    print('  ', t['bad'], 'x', t['count'], '->', t['good'])
