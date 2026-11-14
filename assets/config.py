#!/usr/bin/env python3
"""Load profile.toml, the settings for what the blocks say and show.

Every key has a default here, so the generator runs with no profile.toml at
all and a partial one only overrides what it actually names. Reading is
tomllib from the standard library (3.11+), which is why the config is TOML
and not YAML: nothing to install, and the workflow already runs 3.12.

Each block owns a section carrying its own `enabled` flag, its title and its
settings, so switching a block off and editing its words are never in two
different places. Configuring a section is all it takes to put it on the
page - see BLOCKS in generate.py for how order is decided.

Two things the file will not do quietly. A key that isn't a real setting is
reported by name rather than ignored, because a typo that silently does
nothing is the worst kind; and a value of the wrong type stops the run with
the key path in the message instead of failing somewhere in the SVGs.

Layout - track width, card geometry, row heights - stays in generate.py, and
colours stay in generate.py and palette.py. Those are the design, not
settings.
"""
import copy
import json
import pathlib
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = ROOT / 'profile.toml'

DEFAULTS = {
    'profile': {
        'login': 'RelativelyUnknown',
        'window': 'past year',
    },
    'blocks': {
        # Order only. A block that is enabled and has something to show is
        # added even when it is missing from here.
        'order': ['header', 'repos', 'sankey', 'lines', 'tools', 'favourites', 'footer'],
    },
    'header': {
        'enabled': True,
        'eyebrow': '',
        # a string is wrapped to the header's measure; a list of strings is
        # taken as written, one line each
        'bio': '',
    },
    'repos': {
        'enabled': True,
        'title': '',
        'count': 3,
        'exclude': [],
    },
    'sankey': {
        'enabled': True,
        'title': 'Commit flow',
        'height': 460,
        'fold_repos_pct': 1.0,      # a repo under this share folds into "Other repos"
        'fold_langs_pct': 1.5,
    },
    'lines': {
        'enabled': True,
        'title': 'Lines by language',
        'top': 8,
        'icons': True,
        'devicon': {},              # Linguist language -> devicon icon name
    },
    'tools': {
        'enabled': True,
        'title': '',
        'items': [],                # {label, icon} per chip, and optional {color}
    },
    'favourites': {
        'enabled': True,
        'title': '',
        'items': [],                # {url, note} per card, and optional {owner, name}
        # Starred repos (stars.json, fetched by discover_stars.py) are added
        # after the hand-picked items.
        'stars': True,
        'stars_max': 0,             # most stars to show; 0 is all of them
        'stars_exclude': [],        # 'owner/name' entries to leave out
        # one column below this many cards in total, two from here up
        'two_columns_from': 6,
    },
    'footer': {
        'enabled': True,
        'text': '',
    },
}

# Sections whose keys are the user's own names, not settings, so an unknown
# one is the point rather than a typo.
FREE_FORM = ('lines.devicon',)

# Settings that used to live somewhere else. Naming the new address beats
# telling someone their own setting isn't a setting.
MOVED = {
    'profile.eyebrow': 'header.eyebrow',
    'profile.bio': 'header.bio',
    'profile.footer': 'footer.text',
}

# what a value looks like in a config file, rather than in Python
TYPE_NAMES = {bool: 'true or false', int: 'a number', float: 'a number',
              str: 'a string', list: 'a list', dict: 'a table'}


def _describe(value):
    return TYPE_NAMES.get(type(value), f'a {type(value).__name__}')


def _type_ok(base, value):
    if isinstance(base, bool) or isinstance(value, bool):
        return isinstance(base, bool) and isinstance(value, bool)
    if isinstance(base, (int, float)) and isinstance(value, (int, float)):
        return True
    if isinstance(base, str) and isinstance(value, list):
        return all(isinstance(v, str) for v in value)   # bio, as explicit lines
    return type(base) is type(value)


def _merge(base, over, path='', name='profile.toml'):
    out = dict(base)
    for key, value in over.items():
        where = f'{path}.{key}' if path else key
        if path in FREE_FORM:
            out[key] = value
        elif where in MOVED:
            print(f'{name}: "{where}" has moved to "{MOVED[where]}" - ignoring it here')
        elif key not in base:
            print(f'{name}: ignoring "{where}", which is not a setting')
        elif isinstance(base[key], dict) and isinstance(value, dict):
            out[key] = _merge(base[key], value, where, name)
        elif _type_ok(base[key], value):
            out[key] = value
        else:
            raise SystemExit(f'{name}: "{where}" takes {_describe(base[key])}, '
                             f'not {_describe(value)}')
    return out


def devicon_name(cfg, language):
    """The devicon icon for a Linguist language name. [lines.devicon] only
    lists the ones that differ; everything else is just the name lowered,
    which is already right for python, typescript, javascript and go."""
    return cfg['lines']['devicon'].get(language, language.lower())


def url_parts(url):
    """('pydantic', 'pydantic') out of https://github.com/pydantic/pydantic."""
    tail = url.split('github.com/', 1)[-1].strip('/')
    bits = [b for b in tail.split('/') if b]
    return (bits + [None, None])[:2]


def favourite_items(cfg):
    """Hand-picked [[favourites.items]] first, then starred repos from
    stars.json (newest star first) that are not already listed, up to
    favourites.stars_max. Both build_avatars.py and generate.py read this, so
    they always agree on who is on the page."""
    fav = cfg['favourites']
    items = list(fav['items'])
    if not fav['stars']:
        return items
    path = pathlib.Path(__file__).resolve().parent / 'stars.json'
    if not path.exists():
        return items
    skip = {x.lower() for x in fav['stars_exclude']}
    for it in items:
        skip.add('/'.join(p or '' for p in url_parts(it.get('url', ''))).lower())
    stars = []
    for star in json.loads(path.read_text()).get('stars', []):
        full = f"{star['owner']}/{star['repo']}"
        if full.lower() in skip:
            continue
        skip.add(full.lower())
        stars.append({'url': f'https://github.com/{full}', 'note': star.get('description', '')})
    return items + (stars[:fav['stars_max']] if fav['stars_max'] else stars)


def load(path=CONFIG):
    defaults = copy.deepcopy(DEFAULTS)
    if not path.exists():
        return defaults
    try:
        raw = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f'{path.name}: {exc}')
    return _merge(defaults, raw, name=path.name)


if __name__ == '__main__':
    import json
    print(json.dumps(load(), indent=2))
