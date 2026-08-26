<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/header.svg"/><img src="assets/header.svg" alt="RelativelyUnknown — data and AI engineering. I build tools that sit close to the code: static analysis, language grammars, and the editor surfaces around them." width="100%"/></picture>

<p align="center">
<a href="https://github.com/RelativelyUnknown/Mallard"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/repo-mallard.svg"/><img src="assets/repo-mallard.svg" alt="Mallard — a VS Code extension that tracks how much your AI coding assistant is actually costing you. TypeScript 82.9%, Python 14.3%." width="32%"/></picture></a>
<a href="https://github.com/RelativelyUnknown/burnt"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/repo-burnt.svg"/><img src="assets/repo-burnt.svg" alt="burnt — static analysis for Databricks and Spark pipelines: one code graph, 110 rules. Rust 63.8%, Python 35.8%." width="32%"/></picture></a>
<a href="https://github.com/RelativelyUnknown/tree-sitter-sql-extended"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/repo-grammar.svg"/><img src="assets/repo-grammar.svg" alt="tree-sitter-sql-extended — a tree-sitter SQL grammar: an ANSI base plus 22 independently compiled dialects." width="32%"/></picture></a>
</p>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/activity.svg"/><img src="assets/activity.svg" alt="Contribution heatmap: 537 commits authored across 4 public repositories in the last year, on 77 active days." width="100%"/></picture>

### How `burnt` reads a pipeline

```mermaid
flowchart LR
  PY["Python source"]:::src
  SQL["SQL source"]:::src
  PY --> TSP["tree-sitter-python"]:::parse
  SQL --> TSS["tree-sitter-sequel"]:::parse
  TSP --> CST["Concrete syntax tree<br/>errors stay local"]:::core
  TSS --> CST
  CST --> GRAPH["PyGraph<br/>nodes, edges, spans"]:::core
  GRAPH --> RULES["Rule engine<br/>110 graph-DSL rules"]:::core
  RULES --> SARIF["SARIF"]:::out
  RULES --> MD["Markdown report"]:::out

  classDef src fill:#0969da22,stroke:#0969da,color:#0969da
  classDef parse fill:#8250df22,stroke:#8250df,color:#8250df
  classDef core fill:#1a7f3722,stroke:#1a7f37,color:#1a7f37
  classDef out fill:#9a670022,stroke:#9a6700,color:#9a6700
```

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/stack.svg"/><img src="assets/stack.svg" alt="Stack: Python, Rust, TypeScript, Go, C; PyTorch, TensorFlow, scikit-learn, pandas, NumPy; Spark, Databricks, PostgreSQL, MySQL, Grafana; Docker, Kubernetes, Linux, Git, GitHub Actions." width="100%"/></picture>

<a href="https://www.linkedin.com/in/jurreandenys/"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/footer.svg"/><img src="assets/footer.svg" alt="Open to talk about developer tooling, static analysis, and anything AI-adjacent — linkedin.com/in/jurreandenys" width="100%"/></picture></a>
