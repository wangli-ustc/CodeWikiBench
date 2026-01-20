# Rubrics Generation Pipeline

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py)
- [combine_rubrics.py](file://src/rubrics_generator/combine_rubrics.py)
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py)
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py)
- [docs_navigator.py](file://src/tools/docs_navigator.py)
- [utils.py](file://src/utils.py)
- [config.py](file://src/config.py)
- [claude-sonnet-4.json](file://examples/OpenHands/rubrics/claude-sonnet-4.json)
- [combined_rubrics.json](file://examples/OpenHands/rubrics/combined_rubrics.json)
- [reliability_assessment.json](file://examples/OpenHands/rubrics/reliability_assessment.json)
- [requirements.txt](file://requirements.txt)
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
This document explains the AI-powered hierarchical rubric generation pipeline that transforms parsed documentation into structured evaluation rubrics. The system supports multiple LLM providers (Claude, Kimi, Gemini) and uses an agent-based architecture with optional tool-enabled navigation to iteratively refine rubrics. It documents the workflow from ingestion to final combined rubrics, including hierarchical structure semantics, weight assignments, reference path collection, leaf rubric requirements, and output formats. Practical examples, model selection criteria, and debugging strategies are included.

## Project Structure
The rubrics pipeline is organized around a shell orchestration script and Python modules that implement generation, combination, visualization, and reliability assessment. The repository also includes example outputs demonstrating rubric formats and evaluation results.

```mermaid
graph TB
subgraph "Shell Orchestration"
RUN["run_rubrics_pipeline.sh"]
end
subgraph "Generation"
GEN["generate_rubrics.py"]
NAV["docs_navigator.py"]
CFG["config.py"]
UTL["utils.py"]
end
subgraph "Combination"
COMB["combine_rubrics.py"]
end
subgraph "Assessment"
ASSESS["assess_rubrics.py"]
end
subgraph "Visualization"
VIZ["visualize_rubrics.py"]
end
subgraph "Examples"
EX1["claude-sonnet-4.json"]
EX2["combined_rubrics.json"]
EX3["reliability_assessment.json"]
end
RUN --> GEN
GEN --> NAV
GEN --> CFG
GEN --> UTL
RUN --> COMB
COMB --> CFG
COMB --> UTL
RUN --> VIZ
RUN --> ASSESS
ASSESS --> CFG
ASSESS --> UTL
EX1 -.-> VIZ
EX2 -.-> VIZ
EX3 -.-> ASSESS
```

**Diagram sources**
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L1-L320)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L1-L257)
- [combine_rubrics.py](file://src/rubrics_generator/combine_rubrics.py#L1-L306)
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py#L1-L308)
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py#L1-L168)
- [docs_navigator.py](file://src/tools/docs_navigator.py#L1-L345)
- [config.py](file://src/config.py#L1-L32)
- [utils.py](file://src/utils.py#L1-L86)
- [claude-sonnet-4.json](file://examples/OpenHands/rubrics/claude-sonnet-4.json#L1-L440)
- [combined_rubrics.json](file://examples/OpenHands/rubrics/combined_rubrics.json#L1-L494)
- [reliability_assessment.json](file://examples/OpenHands/rubrics/reliability_assessment.json#L1-L19)

**Section sources**
- [README.md](file://README.md#L73-L77)
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L1-L320)

## Core Components
- Shell orchestration script: Orchestrates generation, combination, and optional visualization for multiple models, with flags for tool usage, temperature, and retries.
- Generation module: Builds an agent with system prompts, optionally enables a documentation navigator tool, and extracts rubrics from LLM outputs.
- Combination module: Uses an LLM to semantically merge rubrics from multiple models, with fallback merging and robust JSON parsing.
- Assessment module: Computes inter-model consistency and an overall reliability score using semantic and structural similarity.
- Visualization module: Converts rubrics to a graph and prints an ASCII tree for quick inspection.
- Tools: A documentation navigator tool that safely retrieves content from structured docs and limits depth to manage token limits.
- Utilities and configuration: LLM initialization, native LLM calls, token truncation, and environment-based configuration.

**Section sources**
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L167-L265)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L14-L257)
- [combine_rubrics.py](file://src/rubrics_generator/combine_rubrics.py#L22-L306)
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py#L14-L308)
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py#L1-L168)
- [docs_navigator.py](file://src/tools/docs_navigator.py#L11-L345)
- [utils.py](file://src/utils.py#L12-L86)
- [config.py](file://src/config.py#L14-L32)

## Architecture Overview
The pipeline follows a multi-stage workflow:
1. Documentation ingestion: Parsed docs and docs tree are prepared in the data directory.
2. Rubric generation: For each model, an agent constructs hierarchical rubrics either with or without tool-enabled navigation.
3. Rubric combination: A semantic LLM merges rubrics from multiple models into a consolidated set.
4. Reliability assessment: Consistency metrics and an overall score quantify rubric trustworthiness.
5. Visualization: Optional ASCII tree rendering for quick inspection.

```mermaid
sequenceDiagram
participant SH as "Shell Script"
participant GEN as "generate_rubrics.py"
participant AG as "Agent"
participant NAV as "docs_navigator.py"
participant COMB as "combine_rubrics.py"
participant ASSESS as "assess_rubrics.py"
participant VIZ as "visualize_rubrics.py"
SH->>GEN : "--repo-name, --model, [--use-tools]"
GEN->>AG : "initialize with system prompt"
alt Tool-enabled mode
AG->>NAV : "docs_navigator_tool(paths)"
NAV-->>AG : "content with depth limits"
end
AG-->>GEN : "rubrics JSON"
GEN-->>SH : "save model.json"
SH->>COMB : "--repo-name [--temperature, --max-retries]"
COMB->>COMB : "semantic LLM merge"
COMB-->>SH : "combined_rubrics.json"
SH->>ASSESS : "--repo-name"
ASSESS-->>SH : "reliability_assessment.json"
SH->>VIZ : "--rubrics-path"
VIZ-->>SH : "ASCII tree"
```

**Diagram sources**
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L167-L265)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L170-L257)
- [docs_navigator.py](file://src/tools/docs_navigator.py#L261-L285)
- [combine_rubrics.py](file://src/rubrics_generator/combine_rubrics.py#L22-L306)
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py#L22-L308)
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py#L129-L168)

## Detailed Component Analysis

### Agent-Based Rubric Generation
The generation module defines two system prompts:
- Tool-enabled mode: Guides constructing hierarchical rubrics with explicit weights and reference paths for leaf rubrics.
- Tool-disabled mode: Focuses on reverse-engineering internal architecture from usage-oriented documentation.

Key behaviors:
- Iterative refinement: The agent updates rubrics progressively as it accesses documentation.
- Output extraction: Parses JSON from LLM output, saving raw output if JSON parsing fails.
- Visualization: Automatically renders rubrics after generation.

```mermaid
flowchart TD
Start(["Start Generation"]) --> LoadTree["Load docs_tree.json"]
LoadTree --> ChoosePrompt{"Use tools?"}
ChoosePrompt --> |Yes| PromptWithTools["Use SYSTEM_PROMPT"]
ChoosePrompt --> |No| PromptWithoutTools["Use SYSTEM_PROMPT_WO_TOOLS"]
PromptWithTools --> InitAgent["Initialize Agent with tools"]
PromptWithoutTools --> InitAgentNoTools["Initialize Agent without tools"]
InitAgent --> RunAgent["Agent.run(prompt, deps)"]
InitAgentNoTools --> RunAgent
RunAgent --> ExtractJSON["Extract JSON from output"]
ExtractJSON --> ValidJSON{"Valid JSON?"}
ValidJSON --> |Yes| SaveRubrics["Save rubrics.json"]
ValidJSON --> |No| SaveRaw["Save raw_output.txt"]
SaveRubrics --> End(["End"])
SaveRaw --> End
```

**Diagram sources**
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L25-L167)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L170-L257)

**Section sources**
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L25-L167)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L170-L257)

### Tool-Enabled vs Tool-Disabled Modes
- Tool-enabled mode: Uses the documentation navigator to retrieve specific content nodes, enabling precise, iterative refinement guided by the docs tree.
- Tool-disabled mode: Requires the LLM to synthesize rubrics from the docs tree alone, focusing on inferring internal structure from usage-oriented content.

Mode differences:
- Tool-enabled: Prompts emphasize hierarchical construction with weights and leaf rubric reference paths.
- Tool-disabled: Prompts emphasize transforming usage instructions into architectural insights.

**Section sources**
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L25-L98)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L100-L167)

### Hierarchical Rubric Structure and Weights
The rubric format uses a nested structure with weights:
- Essential: 3
- Important: 2
- Supportive: 1

Leaf rubrics include reference paths pointing to documentation sources. The structure supports recursive sub_tasks to arbitrary depth.

```mermaid
classDiagram
class Rubric {
+string requirements
+int weight
+Rubric[] sub_tasks
+string[] reference
}
```

**Diagram sources**
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py#L7-L12)
- [claude-sonnet-4.json](file://examples/OpenHands/rubrics/claude-sonnet-4.json#L1-L440)
- [combined_rubrics.json](file://examples/OpenHands/rubrics/combined_rubrics.json#L1-L494)

**Section sources**
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py#L7-L12)
- [claude-sonnet-4.json](file://examples/OpenHands/rubrics/claude-sonnet-4.json#L1-L440)
- [combined_rubrics.json](file://examples/OpenHands/rubrics/combined_rubrics.json#L1-L494)

### Documentation Navigator Tool
The tool safely navigates the docs tree and structured docs, retrieving content with depth-limited truncation to respect token limits. It supports:
- Listing sections at a given path
- Retrieving content for specific paths
- Searching content across the docs structure

```mermaid
classDiagram
class DocsNavigator {
+string docs_tree_path
+string structured_docs_path
+list_sections(path) List
+get_content(path) Dict
+search_content(query, ...) List
-_navigate_to_path(data, path, max_depth) Any
-_limit_content_depth(data, max_depth, current_depth) Any
}
class AgentDeps {
+DocsNavigator docs_navigator
+__init__(docs_path)
}
class Tool_docs_navigator {
+run_docs_navigator(ctx, paths) str
}
AgentDeps --> DocsNavigator : "creates"
Tool_docs_navigator --> DocsNavigator : "uses"
```

**Diagram sources**
- [docs_navigator.py](file://src/tools/docs_navigator.py#L11-L345)

**Section sources**
- [docs_navigator.py](file://src/tools/docs_navigator.py#L11-L345)
- [utils.py](file://src/utils.py#L12-L27)

### Semantic Combination of Rubrics
The combination module:
- Loads rubrics from multiple models
- Calls an LLM to merge rubrics into a single, coherent structure
- Implements robust JSON extraction with multiple fallbacks
- Calculates statistics and metadata for the combined rubrics

```mermaid
flowchart TD
Start(["Start Combination"]) --> LoadFiles["Load all model rubrics"]
LoadFiles --> SingleOrMultiple{"Single or multiple?"}
SingleOrMultiple --> |Single| Copy["Copy to combined"]
SingleOrMultiple --> |Multiple| CallLLM["Call LLM to merge"]
CallLLM --> ParseResp["Parse JSON response"]
ParseResp --> Success{"Parsed?"}
Success --> |Yes| Save["Save combined_rubrics.json"]
Success --> |No| Fallback["Fallback simple merge"]
Fallback --> Save
Copy --> Save
Save --> Stats["Compute statistics"]
Stats --> End(["End"])
```

**Diagram sources**
- [combine_rubrics.py](file://src/rubrics_generator/combine_rubrics.py#L22-L306)

**Section sources**
- [combine_rubrics.py](file://src/rubrics_generator/combine_rubrics.py#L22-L306)

### Reliability Assessment
The assessment module computes:
- Inter-model consistency using semantic similarity and structural similarity
- An overall reliability score as a weighted average
- Detailed metrics including average semantic consistency, structural consistency, and standard deviation

```mermaid
flowchart TD
Start(["Start Assessment"]) --> LoadCombined["Load combined rubrics"]
LoadCombined --> LoadModels["Load individual rubrics"]
LoadModels --> Pairwise["Compute pairwise similarities"]
Pairwise --> Semantic["Semantic similarity"]
Pairwise --> Structural["Structural similarity"]
Semantic --> AvgSem["Average semantic consistency"]
Structural --> AvgStr["Average structural consistency"]
AvgSem --> Score["Overall reliability score"]
AvgStr --> Score
Score --> Save["Save reliability_assessment.json"]
Save --> End(["End"])
```

**Diagram sources**
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py#L22-L308)

**Section sources**
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py#L22-L308)
- [reliability_assessment.json](file://examples/OpenHands/rubrics/reliability_assessment.json#L1-L19)

### Visualization
The visualization module converts rubrics into a directed graph and prints an ASCII tree representation, highlighting weights and leaf nodes.

```mermaid
flowchart TD
Start(["Start Visualization"]) --> Load["Load rubrics.json"]
Load --> BuildGraph["Build directed graph"]
BuildGraph --> Tree["Print ASCII tree"]
Tree --> End(["End"])
```

**Diagram sources**
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py#L129-L168)

**Section sources**
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py#L129-L168)

## Dependency Analysis
The pipeline relies on:
- LLM providers (Anthropic, OpenAI-compatible endpoints) configured via environment variables
- Tokenization utilities for safe tool responses
- NetworkX for graph visualization
- Scikit-learn and NumPy for similarity computations

```mermaid
graph TB
GEN["generate_rubrics.py"] --> UTL["utils.py"]
GEN --> CFG["config.py"]
GEN --> NAV["docs_navigator.py"]
COMB["combine_rubrics.py"] --> UTL
COMB --> CFG
ASSESS["assess_rubrics.py"] --> UTL
ASSESS --> CFG
VIZ["visualize_rubrics.py"] --> NET["networkx"]
```

**Diagram sources**
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L1-L20)
- [combine_rubrics.py](file://src/rubrics_generator/combine_rubrics.py#L1-L12)
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py#L1-L12)
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py#L1-L6)
- [utils.py](file://src/utils.py#L1-L11)
- [config.py](file://src/config.py#L1-L32)

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L107)
- [config.py](file://src/config.py#L14-L32)
- [utils.py](file://src/utils.py#L12-L86)

## Performance Considerations
- Token limits: The documentation navigator truncates content to respect maximum tokens per tool response, preventing oversized tool outputs.
- Retry strategy: The combination module retries LLM calls with exponential backoff and falls back to simple merging when API calls fail.
- Depth control: Content depth is limited during navigation to reduce token consumption and improve response speed.
- Parallel model execution: The shell script processes models sequentially; parallelization could be introduced at the cost of increased resource usage.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Missing data directory: Ensure the repository name corresponds to a data directory with docs_tree.json and structured_docs.json.
- LLM API failures: Increase max retries or adjust temperature; verify BASE_URL and API_KEY in environment variables.
- JSON parsing errors: The generator saves raw output for debugging; inspect the raw output file to identify formatting issues.
- Tool navigation errors: Verify paths in the docs tree; the navigator raises descriptive errors for invalid indices or missing content.
- Reliability assessment failures: Ensure multiple rubrics are present for comparison; otherwise, the assessment returns an error indicating insufficient rubrics.

**Section sources**
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L142-L158)
- [generate_rubrics.py](file://src/rubrics_generator/generate_rubrics.py#L244-L251)
- [docs_navigator.py](file://src/tools/docs_navigator.py#L39-L43)
- [combine_rubrics.py](file://src/rubrics_generator/combine_rubrics.py#L141-L151)
- [assess_rubrics.py](file://src/rubrics_generator/assess_rubrics.py#L51-L52)

## Conclusion
The rubrics generation pipeline provides a robust, agent-based approach to constructing hierarchical rubrics from documentation. By supporting multiple LLMs, optional tool-enabled navigation, semantic combination, and reliability assessment, it delivers trustworthy, interpretable rubrics suitable for evaluating documentation quality. The modular design allows easy extension and debugging, while the visualization and assessment tools facilitate quick inspection and validation.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Practical Examples
- Generate rubrics with multiple models:
  - bash ./run_rubrics_pipeline.sh --repo-name OpenHands --models claude-sonnet-4,kimi-k2-instruct --visualize
- Generate rubrics with tools disabled:
  - bash ./run_rubrics_pipeline.sh --repo-name OpenHands --no-tools
- Combine rubrics with custom temperature and retries:
  - python rubrics_generator/combine_rubrics.py --repo-name OpenHands --temperature 0.1 --max-retries 3

**Section sources**
- [README.md](file://README.md#L73-L77)
- [run_rubrics_pipeline.sh](file://src/run_rubrics_pipeline.sh#L61-L74)

### Output File Formats
- Individual model rubrics: {model}.json (e.g., claude-sonnet-4.json)
- Combined rubrics: combined_rubrics.json (includes rubrics and combination_metadata)
- Reliability assessment: reliability_assessment.json (inter-model consistency and overall score)
- Visualization: ASCII tree printed to console

**Section sources**
- [claude-sonnet-4.json](file://examples/OpenHands/rubrics/claude-sonnet-4.json#L1-L440)
- [combined_rubrics.json](file://examples/OpenHands/rubrics/combined_rubrics.json#L1-L494)
- [reliability_assessment.json](file://examples/OpenHands/rubrics/reliability_assessment.json#L1-L19)
- [visualize_rubrics.py](file://src/rubrics_generator/visualize_rubrics.py#L129-L168)

### Model Selection Criteria
- Claude models: Strong performance on structured reasoning and hierarchical tasks.
- Kimi models: Good balance of reasoning and code understanding.
- Gemini models: Effective for multimodal and structured outputs.
- Selection depends on availability, cost, latency, and quality trade-offs.

[No sources needed since this section provides general guidance]