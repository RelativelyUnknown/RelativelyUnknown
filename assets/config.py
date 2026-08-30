#!/usr/bin/env python3
"""Load profile.toml, the settings for what the blocks say and show.

Every key has a default here, so the generator runs with no profile.toml at
all and a partial one only overrides what it actually names. Reading is
tomllib from the standard library (3.11+), which is why the config is TOML
and not YAML: nothing to install, and the workflow already runs 3.12.

Two things the file will not do quietly. A key that isn't a real setting is
reported by name rather than ignored, because a typo that silently does
nothing is the worst kind; and a value of the wrong type stops the run with
the key path in the message instead of failing somewhere in the SVGs.

Layout - track width, card geometry, row heights - stays in generate.py, and
colours stay in generate.py and palette.py. Those are the design, not
settings.
"""
import copy
import pathlib
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = ROOT / 'profile.toml'

DEFAULTS = {
    'profile': {
        'login': 'RelativelyUnknown',
        'eyebrow': 'Data and AI engineering',
        # a string is wrapped to the header's width; a list of strings is
        # taken as written, one line each
        'bio': '',
        'footer': '',
        'window': 'past year',
    },
    'blocks': {
        'order': ['header', 'repos', 'sankey', 'lines', 'footer'],
    },
    'repos': {
        'count': 3,
        'exclude': [],
    },
    'sankey': {
        'title': 'Commit flow',
        'height': 460,
        'fold_repos_pct': 1.0,      # a repo under this share folds into "Other repos"
        'fold_langs_pct': 1.5,
    },
    'lines': {
        'title': 'Lines by language',
        'top': 8,
        'icons': True,
        'devicon': {},              # Linguist language -> devicon icon name
    },
    'tools': {
        'title': 'Day to day',
        'items': [],                # {label, icon} per chip
    },
    'favourites': {
        'items': [],                # {url, note} per card, and optional {owner, name}
    },
}

# Sections whose keys are the user's own names, not settings, so an unknown
# one is the point rather than a typo.
FREE_FORM = ('lines.devicon',)


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
