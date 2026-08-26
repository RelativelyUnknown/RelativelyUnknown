# Credits

Artwork vendored into `icons.json` as path data:

| Source | Licence | Used for |
| --- | --- | --- |
| [Simple Icons](https://github.com/simple-icons/simple-icons) | CC0-1.0 | brand marks in the stack block |
| [Primer Octicons](https://github.com/primer/octicons) | MIT | repo, code, history, graph, terminal and link glyphs |

Brand marks remain trademarks of their respective owners and are used here
only to identify the tools they belong to.

Colours are GitHub's own: [Primer](https://primer.style/) design tokens for
the interface, and [Linguist](https://github.com/github-linguist/linguist)
language colours for the repository language bars.

## Regenerating

```sh
python3 build_data.py ~/path/to/clones   # recount commits and languages
python3 generate.py                      # rewrite every SVG, light and dark
```
