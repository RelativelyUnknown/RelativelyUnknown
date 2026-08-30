# Credits

Artwork vendored into `icons.json` as path data:

| Source | Licence | Used for |
| --- | --- | --- |
| [Primer Octicons](https://github.com/primer/octicons) | MIT | the repo, code and history glyphs |
| [Devicon](https://github.com/devicons/devicon) | MIT | language glyphs in the lines chart, and the tool chips |
| [Simple Icons](https://github.com/simple-icons/simple-icons) | CC0 1.0 | tool chips devicon has no icon for, Databricks among them |

Icons are vendored into `icons.json` as path data, not linked. They have to be:
GitHub serves these SVGs through `<img>`, which puts them in the browser's
secure static mode with external references switched off, so an
`<image href="https://cdn...">` inside one of them silently never loads.
`build_icons.py` fetches whatever `profile.toml` names and only what is
missing. Avatars on the favourite-project cards are embedded the same way, as
base64 by `build_avatars.py`.

Brand marks remain trademarks of their respective owners and are used here
only to identify the tools they belong to.

Every colour is one of GitHub's. The chrome uses [Primer](https://primer.style/)
neutrals, with Primer's link blue and success green as the only accents. Repo
colours in the Sankey are Primer foreground tokens too, handed out one per repo
by `discover_repos.py` and then frozen in `repos.json` so a repo's colour stays
put - see `palette.py`. Language colours are
[Linguist's](https://github.com/github-linguist/linguist): `lang-colors.json` is
rebuilt straight from Linguist's own `languages.yml` by `build_lang_colors.py`,
so it stays current as Linguist adds or recolours languages.

Line counts are counted the crude way by `build_data.py`: every line of every
file with a source extension, blanks and comments included, in the repos I own.
Machine-written files are left out of that count only - `parser.c` from a
tree-sitter grammar, minified bundles - since nobody typed them. The block
appears once `data.json` has line counts in it; before that the README simply
skips it.

What the blocks say and how much each one shows lives in `profile.toml` at the
repo root - the copy, which blocks appear and in what order, how many repo
cards, how many languages in the lines chart. Every key has a default in
`config.py`, so a partial file only overrides what it names. Colours and
layout are deliberately not settings.

`README.md` is generated, not written. `generate.py` emits it alongside the
SVGs so the card links, the alt text and the images can't drift apart - edit
the generator, not the README.

## Regenerating

```sh
python3 discover_repos.py <login>        # refresh repos.json (needs GITHUB_TOKEN for the
                                          # contributed-repos pass; owned repos work without one)
python3 build_lang_colors.py             # refresh lang-colors.json from Linguist
python3 build_icons.py                   # vendor any icon profile.toml names and icons.json lacks
python3 build_avatars.py                 # vendor the avatars for [[favourites.items]]
python3 build_data.py ~/path/to/clones   # recount commits and languages for everything in repos.json
python3 generate.py                      # rewrite every SVG, light and dark, and README.md
```
