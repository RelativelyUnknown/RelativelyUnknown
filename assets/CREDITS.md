# Credits

Artwork and data vendored from other projects:

| Source | Licence | Used for |
| --- | --- | --- |
| [Primer Octicons](https://github.com/primer/octicons) | MIT | the repo, code and history glyphs, as path data in `icons.json` |
| [ozh/github-colors](https://github.com/ozh/github-colors) | MIT | `lang-colors.json` - a mirror of Linguist's `languages.yml` colours |

Brand marks remain trademarks of their respective owners and are used here
only to identify the tools they belong to.

Chrome colours are GitHub's own: [Primer](https://primer.style/) design
tokens for the interface, and GitHub's published brand green
(brand.github.com) as the one accent. Language colours are Linguist's, via
the table above. A repo's Sankey colour is neither - it's an analogous hue
assigned once by `discover_repos.py` and frozen in `repos.json`; see
`hues.py`.

## Regenerating

```sh
python3 discover_repos.py <login>        # refresh repos.json (needs GITHUB_TOKEN for the
                                          # contributed-repos pass; owned repos work without one)
python3 build_data.py ~/path/to/clones   # recount commits and languages for everything in repos.json
python3 generate.py                      # rewrite every SVG, light and dark
```
