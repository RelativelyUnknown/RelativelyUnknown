# Credits

Artwork vendored into `icons.json` as path data:

| Source | Licence | Used for |
| --- | --- | --- |
| [Primer Octicons](https://github.com/primer/octicons) | MIT | the repo, code and history glyphs |

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

`README.md` is generated, not written. `generate.py` emits it alongside the
SVGs so the card links, the alt text and the images can't drift apart - edit
the generator, not the README.

## Regenerating

```sh
python3 discover_repos.py <login>        # refresh repos.json (needs GITHUB_TOKEN for the
                                          # contributed-repos pass; owned repos work without one)
python3 build_lang_colors.py             # refresh lang-colors.json from Linguist
python3 build_data.py ~/path/to/clones   # recount commits and languages for everything in repos.json
python3 generate.py                      # rewrite every SVG, light and dark, and README.md
```
