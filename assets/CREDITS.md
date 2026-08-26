# Credits

Artwork vendored into `icons.json` as path data:

| Source | Licence | Used for |
| --- | --- | --- |
| [Primer Octicons](https://github.com/primer/octicons) | MIT | the repo, code and history glyphs |

Brand marks remain trademarks of their respective owners and are used here
only to identify the tools they belong to.

Chrome colours are GitHub's own: [Primer](https://primer.style/) design
tokens for the interface, and GitHub's published brand green
(brand.github.com) as the one accent. Language colours are
[Linguist's](https://github.com/github-linguist/linguist) - `lang-colors.json`
is rebuilt straight from Linguist's own `languages.yml` by
`build_lang_colors.py`, not copied from a third-party mirror, so it stays
current as Linguist adds or recolours languages. A repo's Sankey colour is
neither of those - it's an analogous hue assigned once by
`discover_repos.py` and frozen in `repos.json`; see `hues.py`.

## Regenerating

```sh
python3 discover_repos.py <login>        # refresh repos.json (needs GITHUB_TOKEN for the
                                          # contributed-repos pass; owned repos work without one)
python3 build_lang_colors.py             # refresh lang-colors.json from Linguist
python3 build_data.py ~/path/to/clones   # recount commits and languages for everything in repos.json
python3 generate.py                      # rewrite every SVG, light and dark
```
