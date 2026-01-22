# CodeWikiBench Quickstart Guide

This guide walks you through running a complete evaluation pipeline for a repository's documentation using CodeWikiBench.

## Example: Evaluating AdalFlow Repository

### Prerequisites

- Python 3.8+
- Git
- Required Python packages (install with `pip install -r requirements.txt`)
- API keys configured in `.env` file (see `src/config.py` for required variables)

### Step 1: Download Official Documentation

Download the official documentation from the repository:

```bash
bash src/download_github_folder.sh \
  --github_repo_url https://github.com/SylphAI-Inc/AdalFlow \
  --folder_path docs
```

This downloads the `docs` folder from the repository to `data/AdalFlow/original/docs/`.

### Step 2: Parse Official Documentation

Parse the downloaded documentation into a structured format:

```bash
python src/docs_parser/parse_official_docs.py --repo_name AdalFlow
```

This creates:
- `data/AdalFlow/original/docs_tree.json` - Hierarchical structure
- `data/AdalFlow/original/structured_docs.json` - Flattened content

### Step 3: Generate and Combine Rubrics

Generate evaluation rubrics using multiple LLMs and combine them:

```bash
bash src/run_rubrics_pipeline.sh \
  --repo-name AdalFlow \
  --visualize \
  --models "iflow/qwen3-coder-plus,github_copilot/gpt-4o"
```

This:
- Generates rubrics using each specified model
- Combines rubrics into a unified evaluation framework
- Saves to `data/AdalFlow/rubrics/`
- Optionally visualizes the rubric hierarchy

### Step 4: Generate AI Documentation (DeepWiki)

Generate documentation using DeepWiki:

```bash
# Crawl and generate DeepWiki documentation
python src/docs_parser/crawl_deepwiki_docs.py \
  --url https://github.com/SylphAI-Inc/AdalFlow.git \
  --output-dir data/AdalFlow/deepwiki/doc

# Parse the generated documentation
python src/docs_parser/parse_generated_docs.py \
  --input-dir data/AdalFlow/deepwiki/doc \
  --output data/AdalFlow/deepwiki
```

This creates:
- `data/AdalFlow/deepwiki/docs_tree.json`
- `data/AdalFlow/deepwiki/structured_docs.json`

### Step 5: Generate AI Documentation (CodeWiki)

Generate documentation using CodeWiki:

```bash
# Generate CodeWiki documentation (run from repository root)
cd ../AdalFlow
codewiki generate -o .codewiki
cd ../CodeWikiBench

# Parse the generated documentation
python src/docs_parser/parse_generated_docs.py \
  --input-dir ../AdalFlow/.codewiki \
  --output data/AdalFlow/codewiki
```

This creates:
- `data/AdalFlow/codewiki/docs_tree.json`
- `data/AdalFlow/codewiki/structured_docs.json`

### Step 6: Evaluate Documentation

Evaluate each documentation set against the rubrics:

```bash
# Evaluate DeepWiki documentation
bash ./src/run_evaluation_pipeline.sh \
  --repo-name AdalFlow \
  --models iflow/qwen3-coder-plus,github_copilot/gpt-4o \
  --visualize \
  --batch-size 4 \
  --reference "deepwiki"

# Evaluate CodeWiki documentation
bash ./src/run_evaluation_pipeline.sh \
  --repo-name AdalFlow \
  --models iflow/qwen3-coder-plus,github_copilot/gpt-4o \
  --visualize \
  --batch-size 4 \
  --reference "codewiki"
```

This:
- Evaluates documentation against generated rubrics
- Uses multiple models for evaluation
- Combines evaluation results
- Generates visualization reports
- Saves results to `data/AdalFlow/{reference}/evaluation_results/`

## Results

After running all steps, you'll find:

```
data/AdalFlow/
├── original/
│   ├── docs/                          # Downloaded official docs
│   ├── docs_tree.json                 # Parsed structure
│   └── structured_docs.json           # Parsed content
├── rubrics/
│   ├── {model1}.json                  # Rubrics from model 1
│   ├── {model2}.json                  # Rubrics from model 2
│   └── combined_rubrics.json          # Unified rubrics
├── deepwiki/
│   ├── doc/                           # Generated DeepWiki docs
│   ├── docs_tree.json                 # Parsed structure
│   ├── structured_docs.json           # Parsed content
│   └── evaluation_results/
│       ├── {model1}.json              # Evaluation from model 1
│       ├── {model2}.json              # Evaluation from model 2
│       └── combined_evaluation.json   # Combined results
└── codewiki/
    ├── docs_tree.json                 # Parsed structure
    ├── structured_docs.json           # Parsed content
    └── evaluation_results/
        ├── {model1}.json              # Evaluation from model 1
        ├── {model2}.json              # Evaluation from model 2
        └── combined_evaluation.json   # Combined results
```

## Pipeline Options

### run_rubrics_pipeline.sh Options

- `--repo-name`: Repository name (required)
- `--models`: Comma-separated list of models
- `--visualize`: Generate visualization
- `--skip-generation`: Skip rubric generation (use existing)
- `--skip-combination`: Skip combining results
- `--temperature`: LLM temperature (default: 0.1)

### run_evaluation_pipeline.sh Options

- `--repo-name`: Repository name (required)
- `--reference`: Documentation folder to evaluate (required)
- `--models`: Comma-separated list of models
- `--batch-size`: Concurrent evaluations per batch (default: 5)
- `--visualize`: Generate visualization
- `--skip-evaluation`: Skip evaluation (only combine)
- `--skip-combination`: Skip combining results
- `--use-tools`: Enable document navigation tools
- `--enable-retry`: Retry failed evaluations
- `--max-retries`: Maximum retry attempts (default: 2)

## Supported Models

Configure your preferred models via environment variables or use defaults:
- `iflow/qwen3-coder-plus`
- `github_copilot/gpt-4o`
- `anthropic/claude-sonnet-4`
- Any model supported by your LLM provider

## Troubleshooting

1. **Import errors**: Ensure you're running commands from the project root
2. **API errors**: Check your `.env` file has valid API keys
3. **Missing data**: Ensure previous steps completed successfully
4. **Rate limits**: Reduce `--batch-size` or add delays between calls

## Next Steps

- Compare evaluation scores across different documentation systems
- Analyze which rubric criteria are well/poorly covered
- Iterate on documentation based on evaluation feedback
- Customize rubric generation prompts for domain-specific needs
