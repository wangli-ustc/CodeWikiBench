# Evaluation Framework

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [config.py](file://src/config.py)
- [utils.py](file://src/utils.py)
- [docs_navigator.py](file://src/tools/docs_navigator.py)
- [judge.py](file://src/judge/judge.py)
- [combine_evaluations.py](file://src/judge/combine_evaluations.py)
- [visualize_evaluation.py](file://src/judge/visualize_evaluation.py)
- [run_evaluation_pipeline.sh](file://src/run_evaluation_pipeline.sh)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py)
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py)
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh)
- [combined_rubrics.json](file://examples/OpenHands/rubrics/combined_rubrics.json)
- [combined_evaluation_results.json](file://examples/OpenHands/deepwiki/evaluation_results/combined_evaluation_results.json)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes the CodeWikiBench evaluation framework for multi-model assessment of documentation quality. It explains the hierarchical rubric-based evaluation methodology, batch processing and error handling, result combination strategies, statistical analysis, comparative assessment across LLM providers, and visualization/reporting options. Practical examples and guidance for parameter tuning and result interpretation are included.

## Project Structure
The repository organizes evaluation and rubrics generation into modular components:
- Data parsing and preparation (docs parser)
- Rubrics generation (multi-model)
- Evaluation pipeline (multi-model)
- Combination and visualization/reporting
- Example outputs demonstrating rubrics and evaluation results

```mermaid
graph TB
subgraph "Data Preparation"
DP1["docs_parser/parse_official_docs.py"]
DP2["docs_parser/parse_generated_docs.py"]
DP3["docs_parser/crawl_deepwiki_docs.py"]
end
subgraph "Rubrics Generation"
RG1["rubrics_generator/generate_rubrics.py"]
RG2["rubrics_generator/combine_rubrics.py"]
RG3["rubrics_generator/visualize_rubrics.py"]
RG4["rubrics_generator/assess_rubrics.py"]
end
subgraph "Evaluation"
EV1["judge/judge.py"]
EV2["judge/combine_evaluations.py"]
EV3["judge/visualize_evaluation.py"]
EV4["run_evaluation_pipeline.sh"]
end
subgraph "Tools"
T1["tools/docs_navigator.py"]
T2["utils.py"]
T3["config.py"]
end
DP1 --> RG1
DP2 --> RG1
DP3 --> RG1
RG1 --> RG2
RG2 --> RG3
RG2 --> RG4
DP1 --> EV1
DP2 --> EV1
DP3 --> EV1
EV1 --> EV2
EV2 --> EV3
EV4 --> EV1
EV4 --> EV2
EV4 --> EV3
T1 --> EV1
T1 --> RG1
T2 --> EV1
T2 --> RG1
T3 --> EV1
T3 --> RG1
```

**Diagram sources**
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L1-L257)
- [judge.py](file://src/judge/judge.py#L1-L551)
- [combine_evaluations.py](file://src/judge/combine_evaluations.py#L1-L375)
- [visualize_evaluation.py](file://src/judge/visualize_evaluation.py#L1-L250)
- [run_evaluation_pipeline.sh](file://src/run_evaluation_pipeline.sh#L1-L331)
- [docs_navigator.py](file://src/tools/docs_navigator.py#L1-L345)
- [utils.py](file://src/utils.py#L1-L86)
- [config.py](file://src/config.py#L1-L32)

**Section sources**
- [README.md](file://README.md#L1-L136)
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L1-L320)
- [run_evaluation_pipeline.sh](file://src/run_evaluation_pipeline.sh#L1-L331)

## Core Components
- Configuration and environment: centralized configuration for API keys, model selection, and token limits.
- LLM utilities: unified LLM initialization and native LLM invocation for fallbacks.
- Documentation navigator tool: navigates and retrieves content from structured docs and docs tree for evaluation.
- Evaluation engine: rubric traversal, leaf evaluation, batch processing, retry/error handling, and bottom-up scoring.
- Combination engine: combines multiple LLM evaluation results using configurable methods and computes standard deviations.
- Visualization/reporting: summary, detailed, CSV export, and Markdown report generation.
- Pipelines: end-to-end rubrics generation and evaluation pipelines with batch size and retry controls.

**Section sources**
- [config.py](file://src/config.py#L1-L32)
- [utils.py](file://src/utils.py#L1-L86)
- [docs_navigator.py](file://src/tools/docs_navigator.py#L1-L345)
- [judge.py](file://src/judge/judge.py#L1-L551)
- [combine_evaluations.py](file://src/judge/combine_evaluations.py#L1-L375)
- [visualize_evaluation.py](file://src/judge/visualize_evaluation.py#L1-L250)
- [run_evaluation_pipeline.sh](file://src/run_evaluation_pipeline.sh#L1-L331)
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L1-L320)

## Architecture Overview
The evaluation framework follows a hierarchical rubric system:
- Rubrics are generated by multiple LLMs and combined into a consensus structure.
- Documentation is parsed into a docs tree and structured docs.
- Evaluation compares documentation against rubric requirements using batched LLM calls.
- Results are combined across models with statistical aggregation and standard deviation computation.
- Visualization and reporting provide summary and detailed views, plus CSV and Markdown exports.

```mermaid
sequenceDiagram
participant User as "User"
participant Pipeline as "run_evaluation_pipeline.sh"
participant Judge as "judge/judge.py"
participant LLM as "LLM Provider"
participant Nav as "docs_navigator.py"
participant Combiner as "combine_evaluations.py"
participant Visual as "visualize_evaluation.py"
User->>Pipeline : Configure repo, models, batch size
Pipeline->>Judge : Invoke evaluation per model
Judge->>Nav : Use docs_navigator tool (optional)
Nav-->>Judge : Retrieved content for evaluation
Judge->>LLM : Submit batched evaluation prompts
LLM-->>Judge : Responses with scores and reasoning
Judge-->>Pipeline : Save per-model evaluation results
Pipeline->>Combiner : Combine results (average/majority/weighted)
Combiner-->>Pipeline : Combined rubrics with std
Pipeline->>Visual : Generate summary/detailed/CSV/Markdown
Visual-->>User : Reports and artifacts
```

**Diagram sources**
- [run_evaluation_pipeline.sh](file://src/run_evaluation_pipeline.sh#L1-L331)
- [judge.py](file://src/judge/judge.py#L1-L551)
- [docs_navigator.py](file://src/tools/docs_navigator.py#L1-L345)
- [combine_evaluations.py](file://src/judge/combine_evaluations.py#L1-L375)
- [visualize_evaluation.py](file://src/judge/visualize_evaluation.py#L1-L250)

## Detailed Component Analysis

### Hierarchical Rubric System
- Rubrics are hierarchical JSON structures with weights and nested sub-tasks.
- Leaf-level requirements carry the actual evaluation criteria.
- Rubrics are generated by multiple LLMs and combined into a consensus structure with metadata.

```mermaid
flowchart TD
A["Rubrics JSON"] --> B["Top-level categories"]
B --> C["Sub-tasks with weights"]
C --> D["Leaf requirements"]
D --> E["Evaluation criteria"]
```

**Diagram sources**
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L1-L257)
- [combined_rubrics.json](file://examples/OpenHands/rubrics/combined_rubrics.json#L1-L494)

**Section sources**
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L1-L257)
- [combined_rubrics.json](file://examples/OpenHands/rubrics/combined_rubrics.json#L1-L494)

### Evaluation Engine
- Traverses rubrics to collect leaf requirements.
- Supports batched asynchronous evaluation with configurable batch size.
- Implements robust retry and error handling for parsing failures and rate limits.
- Calculates scores bottom-up using weighted averages.
- Saves per-model evaluation results and prints summary statistics.

```mermaid
flowchart TD
Start(["Start Evaluation"]) --> Load["Load docs_tree.json and rubrics"]
Load --> Collect["Collect leaf requirements"]
Collect --> Batch["Batch processing loop"]
Batch --> Eval["Evaluate leaf with LLM/tool"]
Eval --> Retry{"Error or parsing failure?"}
Retry --> |Yes| ReEval["Retry with fallback parsing"]
Retry --> |No| Next["Next leaf"]
ReEval --> Next
Next --> More{"More leaves?"}
More --> |Yes| Batch
More --> |No| BottomUp["Bottom-up scoring with weights"]
BottomUp --> Save["Save evaluation results"]
Save --> End(["End"])
```

**Diagram sources**
- [judge.py](file://src/judge/judge.py#L1-L551)

**Section sources**
- [judge.py](file://src/judge/judge.py#L1-L551)

### Result Combination Strategies
- Supports multiple combination methods: average, majority vote, weighted average, max, min.
- Computes standard deviation per leaf and propagates std bottom-up.
- Adds metadata including combination method, number of evaluations, weights, and overall score range.

```mermaid
flowchart TD
A["Load per-model evaluation files"] --> B["Extract leaf evaluations"]
B --> C["Combine scores by method"]
C --> D["Compute std per leaf"]
D --> E["Propagate std bottom-up"]
E --> F["Add metadata (method, weights, counts)"]
F --> G["Save combined results"]
```

**Diagram sources**
- [combine_evaluations.py](file://src/judge/combine_evaluations.py#L1-L375)

**Section sources**
- [combine_evaluations.py](file://src/judge/combine_evaluations.py#L1-L375)

### Statistical Analysis and Comparative Assessment
- Overall score computed as weighted average across top-level rubrics.
- Standard deviation propagated from leaf-level to top-level rubrics.
- Comparative assessment across models via per-model evaluation files and combined results.
- Reliability assessment module computes inter-model consistency using semantic and structural similarity.

```mermaid
flowchart TD
A["Combined rubrics with std"] --> B["Top-level weighted score"]
B --> C["Std propagation bottom-up"]
C --> D["Confidence intervals"]
D --> E["Comparative ranking across models"]
```

**Diagram sources**
- [combine_evaluations.py](file://src/judge/combine_evaluations.py#L178-L214)
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py#L1-L308)

**Section sources**
- [combine_evaluations.py](file://src/judge/combine_evaluations.py#L178-L214)
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py#L1-L308)

### Visualization and Reporting
- Summary view: overall score, average leaf score, coverage percentage.
- Detailed view: per-requirement scores with reasoning and evidence.
- CSV export: flattened rubric items with path, requirement, score, weight, and evaluation details.
- Markdown report: hierarchical markdown with emoji indicators and evaluation metadata.

```mermaid
flowchart TD
A["Combined evaluation results"] --> B{"Select output format"}
B --> |summary| C["Print summary metrics"]
B --> |detailed| D["Print detailed breakdown"]
B --> |csv| E["Export CSV"]
B --> |markdown| F["Export Markdown"]
```

**Diagram sources**
- [visualize_evaluation.py](file://src/judge/visualize_evaluation.py#L1-L250)

**Section sources**
- [visualize_evaluation.py](file://src/judge/visualize_evaluation.py#L1-L250)

### End-to-End Pipelines
- Rubrics generation pipeline: multi-model rubrics generation, combination, optional visualization.
- Evaluation pipeline: multi-model evaluation, optional combination, optional visualization.

```mermaid
sequenceDiagram
participant User as "User"
participant RP as "run_rubrics_pipeline.sh"
participant RG as "generate_rubrics.py"
participant RC as "combine_rubrics.py"
participant RV as "visualize_rubrics.py"
User->>RP : Configure models and options
RP->>RG : Generate rubrics per model
RG-->>RP : Individual rubrics
RP->>RC : Combine rubrics
RC-->>RP : Combined rubrics
RP->>RV : Optional visualization
RV-->>User : Rubrics visualization
```

**Diagram sources**
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L1-L320)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L1-L257)

**Section sources**
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L1-L320)
- [run_evaluation_pipeline.sh](file://src/run_evaluation_pipeline.sh#L1-L331)

## Dependency Analysis
- Configuration and environment:
  - Centralized API keys, model names, base URLs, and token limits.
- LLM utilities:
  - Unified LLM initialization and native fallback invocation.
- Tools:
  - DocsNavigator integrates with structured docs and docs tree for targeted retrieval.
- Evaluation and combination:
  - Evaluation depends on rubrics, docs tree, and tools; combination depends on evaluation outputs.
- Visualization:
  - Reads combined or individual evaluation results and produces multiple output formats.

```mermaid
graph TB
CFG["config.py"] --> UTIL["utils.py"]
CFG --> JUDGE["judge/judge.py"]
CFG --> RUB_GEN["rubrics_generator/generate_rubrics.py"]
UTIL --> JUDGE
UTIL --> RUB_GEN
NAV["tools/docs_navigator.py"] --> JUDGE
NAV --> RUB_GEN
JUDGE --> COMB["judge/combine_evaluations.py"]
COMB --> VIS["judge/visualize_evaluation.py"]
```

**Diagram sources**
- [config.py](file://src/config.py#L1-L32)
- [utils.py](file://src/utils.py#L1-L86)
- [docs_navigator.py](file://src/tools/docs_navigator.py#L1-L345)
- [judge.py](file://src/judge/judge.py#L1-L551)
- [combine_evaluations.py](file://src/judge/combine_evaluations.py#L1-L375)
- [visualize_evaluation.py](file://src/judge/visualize_evaluation.py#L1-L250)

**Section sources**
- [config.py](file://src/config.py#L1-L32)
- [utils.py](file://src/utils.py#L1-L86)
- [docs_navigator.py](file://src/tools/docs_navigator.py#L1-L345)
- [judge.py](file://src/judge/judge.py#L1-L551)
- [combine_evaluations.py](file://src/judge/combine_evaluations.py#L1-L375)
- [visualize_evaluation.py](file://src/judge/visualize_evaluation.py#L1-L250)

## Performance Considerations
- Batch size optimization:
  - Larger batches increase throughput but risk rate limits; tune based on provider quotas and latency.
  - Use the pipeline’s batch size parameter to balance speed and stability.
- Token limits:
  - Content is truncated to configured token limits to prevent oversized requests.
- Retry and resilience:
  - Automatic retries for parsing failures and rate-limit errors; adjust max retries for stability vs. runtime.
- Cost estimation:
  - The evaluation prints total tokens and estimated cost; monitor and budget accordingly.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Rate limit errors:
  - The evaluation detects rate limit indicators and adds delays; reduce batch size or increase delays.
- Parsing failures:
  - Automatic fallback parsing attempts; enable retries to improve robustness.
- Missing files:
  - Ensure docs_tree.json and rubrics files exist; the pipeline validates inputs and exits with clear errors if missing.
- Tool availability:
  - When using tools, confirm docs_tree.json and structured_docs.json exist in the reference directory.

**Section sources**
- [judge.py](file://src/judge/judge.py#L317-L332)
- [run_evaluation_pipeline.sh](file://src/run_evaluation_pipeline.sh#L169-L185)

## Conclusion
CodeWikiBench provides a robust, multi-model evaluation framework that leverages hierarchical rubrics, batched asynchronous evaluation, resilient error handling, and comprehensive result combination with statistical analysis. The pipelines and visualization tools enable practitioners to compare LLM providers, interpret assessment scores, and generate actionable reports.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Practical Examples and Interpretation Guidelines
- Running evaluations with multiple models:
  - Use the evaluation pipeline script with multiple models and batch sizes; optionally enable tools and retries.
  - Example invocation patterns are provided in the repository README.
- Interpreting assessment scores:
  - Overall score is a weighted average across top-level rubrics; higher scores indicate better documentation coverage.
  - Leaf-level scores near 1.0 indicate clear coverage; scores below 0.5 suggest missing or weak coverage.
  - Standard deviations quantify variability across models; lower std indicates more consistent assessments.
- Generating comprehensive reports:
  - Use visualization options to produce summary, detailed, CSV, and Markdown outputs.
  - Combined results include metadata such as combination method and overall score range.

**Section sources**
- [README.md](file://README.md#L79-L108)
- [run_evaluation_pipeline.sh](file://src/run_evaluation_pipeline.sh#L1-L331)
- [visualize_evaluation.py](file://src/judge/visualize_evaluation.py#L1-L250)
- [combined_evaluation_results.json](file://examples/OpenHands/deepwiki/evaluation_results/combined_evaluation_results.json#L1-L782)