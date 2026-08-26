<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/header.svg"/><img src="assets/header.svg" alt="RelativelyUnknown — data and AI engineering. I build tools that sit close to the code: static analysis, language grammars, and the editor surfaces around them. TypeScript, Python and Rust. 483 commits in the last year across 6 public repositories, on 63 days, peaking at 60 in one day." width="100%"/></picture>

<p align="center">
<a href="https://github.com/RelativelyUnknown/Mallard"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/repo-mallard.svg"/><img src="assets/repo-mallard.svg" alt="Mallard — a VS Code extension that tracks how much your AI coding assistant is actually costing you. TypeScript 82.9%, Python 14.3%, JavaScript 1.7%. 129 commits by me." width="49%"/></picture></a>
<a href="https://github.com/RelativelyUnknown/tree-sitter-sql-extended"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/repo-grammar.svg"/><img src="assets/repo-grammar.svg" alt="tree-sitter-sql-extended — a tree-sitter SQL grammar: an ANSI base plus 22 independently compiled dialects. JavaScript 88.3%, Python 6.1%, Scheme 2.9%. 199 commits by me." width="49%"/></picture></a>
</p>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/activity.svg"/><img src="assets/activity.svg" alt="Contribution heatmap: 483 commits authored across 6 public repositories in the last year, on 63 active days, peaking at 60 in one day." width="100%"/></picture>

### How the SQL dialects inherit

Each dialect compiles to its own parser, but most are a delta on something else
rather than a rewrite — six of the twenty-two inherit from another dialect.

```mermaid
flowchart LR
  ANSI(["ANSI base"]):::base

  ANSI --> HIVE["hive"]:::mid
  HIVE --> SPARK["spark"]:::mid
  SPARK --> DBX["databricks"]:::leaf

  ANSI --> MYSQL["mysql"]:::mid
  MYSQL --> MARIA["mariadb"]:::leaf

  ANSI --> PG["postgres"]:::mid
  PG --> CRDB["cockroachdb"]:::leaf

  ANSI --> BQ["bigquery"]:::mid
  BQ --> SPAN["spanner"]:::leaf

  ANSI --> TRINO["trino"]:::mid
  TRINO --> ATHENA["athena"]:::leaf

  ANSI --> REST["11 more, straight off the base<br/>clickhouse · db2 · duckdb · flink · hana<br/>oracle · redshift · snowflake · sqlite · teradata · tsql"]:::rest

  classDef base fill:#1569FF22,stroke:#1569FF,stroke-width:2px,color:#1569FF
  classDef mid fill:#31DB9222,stroke:#31DB92,color:#1B8F5F
  classDef leaf fill:#FF583122,stroke:#FF5831,color:#FF5831
  classDef rest fill:#FF7BDD1A,stroke:#FF7BDD,color:#B8489B
```

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/languages.svg"/><img src="assets/languages.svg" alt="Languages across every public non-fork repository: TypeScript 85.1%, Python 8.5%, CSS 2.3%, JavaScript 1.9%, SCSS 0.9%, Shell 0.5%, Vue 0.4%, HTML 0.3%." width="100%"/></picture>

<a href="https://www.linkedin.com/in/jurreandenys/"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/footer.svg"/><img src="assets/footer.svg" alt="Open to talk about developer tooling, static analysis, and anything AI-adjacent — linkedin.com/in/jurreandenys" width="100%"/></picture></a>
