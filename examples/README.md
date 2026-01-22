# CodeWikiBench Dataset Examples

This directory contains the official documentation and evaluation rubrics for 22 repositories from the CodeWikiBench dataset.

## Structure

Each repository has the following structure:

```
examples/
├── <repo_name>/
│   ├── original/
│   │   ├── docs_tree.json          # Documentation structure
│   │   ├── structured_docs.json    # Full documentation content
│   │   └── metadata.json           # Repository metadata
│   └── rubrics.json                # Evaluation criteria
```

## Repositories (22 total)

- **Chart.js** - 162 pages, 61 requirements
  - https://github.com/chartjs/Chart.js
  - Commit: `63722800`

- **FluentValidation** - 31 pages, 48 requirements
  - https://github.com/FluentValidation/FluentValidation
  - Commit: `298069b4`

- **OpenHands** - 78 pages, 67 requirements
  - https://github.com/All-Hands-AI/OpenHands
  - Commit: `30604c40`

- **electron** - 270 pages, 92 requirements
  - https://github.com/electron/electron
  - Commit: `828fd59a`

- **git-credential-manager** - 27 pages, 70 requirements
  - https://github.com/git-ecosystem/git-credential-manager
  - Commit: `b62021fd`

- **graphrag** - 42 pages, 56 requirements
  - https://github.com/microsoft/graphrag
  - Commit: `a398cc38`

- **json** - 259 pages, 57 requirements
  - https://github.com/nlohmann/json
  - Commit: `4bc4e37f`

- **libsql** - 13 pages, 37 requirements
  - https://github.com/tursodatabase/libsql
  - Commit: `6e55668c`

- **logstash** - 110 pages, 57 requirements
  - https://github.com/elastic/logstash
  - Commit: `895cfa5b`

- **marktext** - 46 pages, 57 requirements
  - https://github.com/marktext/marktext
  - Commit: `11c8cc1e`

- **material-components-android** - 63 pages, 96 requirements
  - https://github.com/material-components/material-components-android
  - Commit: `c2051db2`

- **mermaid** - 102 pages, 67 requirements
  - https://github.com/mermaid-js/mermaid
  - Commit: `82800a2c`

- **ml-agents** - 58 pages, 46 requirements
  - https://github.com/Unity-Technologies/ml-agents
  - Commit: `4cf2f49a`

- **puppeteer** - 606 pages, 82 requirements
  - https://github.com/puppeteer/puppeteer
  - Commit: `c1105f12`

- **qmk_firmware** - 205 pages, 110 requirements
  - https://github.com/qmk/qmk_firmware
  - Commit: `1a58fce0`

- **rasa** - 112 pages, 70 requirements
  - https://github.com/RasaHQ/rasa
  - Commit: `f28c69e4`

- **storybook** - 804 pages, 78 requirements
  - https://github.com/storybookjs/storybook
  - Commit: `f739234e`

- **sumatrapdf** - 40 pages, 40 requirements
  - https://github.com/sumatrapdfreader/sumatrapdf
  - Commit: `cdadfde7`

- **svelte** - 101 pages, 96 requirements
  - https://github.com/sveltejs/svelte
  - Commit: `be645b4d`

- **trino** - 656 pages, 68 requirements
  - https://github.com/trinodb/trino
  - Commit: `d1501ee5`

- **wazuh** - 46 pages, 46 requirements
  - https://github.com/wazuh/wazuh
  - Commit: `44b7cd33`

- **x64dbg** - 553 pages, 107 requirements
  - https://github.com/x64dbg/x64dbg
  - Commit: `134e7ebb`


## Usage

### Load a specific repository

```python
import json

# Load OpenHands documentation
with open('examples/OpenHands/original/docs_tree.json', 'r') as f:
    docs_tree = json.load(f)

with open('examples/OpenHands/original/structured_docs.json', 'r') as f:
    structured_docs = json.load(f)

with open('examples/OpenHands/rubrics.json', 'r') as f:
    rubrics = json.load(f)
```

### Compare with AI-generated docs

For repositories with AI-generated documentation (like OpenHands), you can compare:

```
examples/OpenHands/
├── original/          # Official documentation (from dataset)
├── deepwiki/          # DeepWiki AI-generated docs
├── codewiki/          # CodeWiki AI-generated docs
└── rubrics/           # Multi-LLM generated rubrics
```

## Dataset Information

- **Source**: [anhnh2002/codewikibench](https://huggingface.co/datasets/anhnh2002/codewikibench)
- **Paper**: [arXiv:2510.24428](https://arxiv.org/abs/2510.24428)
- **Total Pages**: 4384
- **Total Requirements**: 1508

## Statistics

- **Largest documentation**: storybook (804 pages)
- **Most complex evaluation**: qmk_firmware (110 requirements)
- **Average pages per repo**: 199.3
- **Average requirements per repo**: 68.5
