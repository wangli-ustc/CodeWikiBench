#!/bin/bash

# CodeWikiBench Quickstart Automation Script
# This script automates the complete evaluation pipeline for repository documentation

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
REPO_NAME=""
GITHUB_REPO_URL=""
DOCS_FOLDER="docs"
MODELS="iflow/qwen3-coder-plus,github_copilot/gpt-4o"
BATCH_SIZE=4
TEMPERATURE=0.1
VISUALIZE=false
SKIP_DEEPWIKI=false
SKIP_CODEWIKI=false
REPO_CLONE_PATH=""

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Required:
  --repo-name NAME              Repository name (e.g., AdalFlow)
  --github-repo-url URL         GitHub repository URL (e.g., https://github.com/SylphAI-Inc/AdalFlow)

Optional:
  --docs-folder PATH            Documentation folder path in repo (default: docs)
  --models MODELS               Comma-separated list of models (default: iflow/qwen3-coder-plus,github_copilot/gpt-4o)
  --batch-size SIZE             Concurrent evaluations per batch (default: 4)
  --temperature TEMP            LLM temperature (default: 0.1)
  --visualize                   Generate visualizations
  --skip-deepwiki               Skip DeepWiki documentation generation
  --skip-codewiki               Skip CodeWiki documentation generation
  --repo-clone-path PATH        Path to cloned repository (for CodeWiki, default: ../{repo-name})
  -h, --help                    Display this help message

Example:
  $0 --repo-name AdalFlow \\
     --github-repo-url https://github.com/SylphAI-Inc/AdalFlow \\
     --visualize

EOF
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo-name)
            REPO_NAME="$2"
            shift 2
            ;;
        --github-repo-url)
            GITHUB_REPO_URL="$2"
            shift 2
            ;;
        --docs-folder)
            DOCS_FOLDER="$2"
            shift 2
            ;;
        --models)
            MODELS="$2"
            shift 2
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        --temperature)
            TEMPERATURE="$2"
            shift 2
            ;;
        --visualize)
            VISUALIZE=true
            shift
            ;;
        --skip-deepwiki)
            SKIP_DEEPWIKI=true
            shift
            ;;
        --skip-codewiki)
            SKIP_CODEWIKI=true
            shift
            ;;
        --repo-clone-path)
            REPO_CLONE_PATH="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required arguments
if [[ -z "$REPO_NAME" ]]; then
    print_error "Repository name is required"
    usage
fi

if [[ -z "$GITHUB_REPO_URL" ]]; then
    print_error "GitHub repository URL is required"
    usage
fi

# Set default repo clone path if not provided
if [[ -z "$REPO_CLONE_PATH" ]]; then
    REPO_CLONE_PATH="../${REPO_NAME}"
fi

# Build visualization flag
VIZ_FLAG=""
if [[ "$VISUALIZE" == true ]]; then
    VIZ_FLAG="--visualize"
fi

print_info "Starting CodeWikiBench evaluation pipeline"
print_info "Repository: $REPO_NAME"
print_info "GitHub URL: $GITHUB_REPO_URL"
print_info "Models: $MODELS"
print_info "Batch Size: $BATCH_SIZE"

# Check prerequisites
print_step "Checking Prerequisites"

if ! command -v python &> /dev/null; then
    print_error "Python is not installed"
    exit 1
fi
print_success "Python found"

if ! command -v git &> /dev/null; then
    print_error "Git is not installed"
    exit 1
fi
print_success "Git found"

# Dependencies are managed via uv - skipping pip install

# Step 1: Download Official Documentation
print_step "Step 1: Downloading Official Documentation"

print_info "Downloading $DOCS_FOLDER folder from $GITHUB_REPO_URL..."
bash src/download_github_folder.sh \
    --github_repo_url "$GITHUB_REPO_URL" \
    --folder_path "$DOCS_FOLDER"

print_success "Documentation downloaded to data/${REPO_NAME}/original/${DOCS_FOLDER}/"

# Step 2: Parse Official Documentation
print_step "Step 2: Parsing Official Documentation"

print_info "Parsing documentation into structured format..."
python src/docs_parser/parse_official_docs.py --repo_name "$REPO_NAME"

print_success "Documentation parsed"
print_info "Created: data/${REPO_NAME}/original/docs_tree.json"
print_info "Created: data/${REPO_NAME}/original/structured_docs.json"

# Step 3: Generate and Combine Rubrics
print_step "Step 3: Generating and Combining Rubrics"

print_info "Generating evaluation rubrics using models: $MODELS..."
bash src/run_rubrics_pipeline.sh \
    --repo-name "$REPO_NAME" \
    --models "$MODELS" \
    --temperature "$TEMPERATURE" \
    $VIZ_FLAG

print_success "Rubrics generated and combined"
print_info "Results saved to data/${REPO_NAME}/rubrics/"

# Step 4: Generate AI Documentation (DeepWiki)
if [[ "$SKIP_DEEPWIKI" == false ]]; then
    print_step "Step 4: Generating AI Documentation (DeepWiki)"
    
    print_info "Crawling and generating DeepWiki documentation..."
    python src/docs_parser/crawl_deepwiki_docs.py \
        --url "$GITHUB_REPO_URL.git" \
        --output-dir "data/${REPO_NAME}/deepwiki/doc"
    
    print_info "Parsing DeepWiki documentation..."
    python src/docs_parser/parse_generated_docs.py \
        --input-dir "data/${REPO_NAME}/deepwiki/doc" \
        --output "data/${REPO_NAME}/deepwiki"
    
    print_success "DeepWiki documentation generated and parsed"
    print_info "Created: data/${REPO_NAME}/deepwiki/docs_tree.json"
    print_info "Created: data/${REPO_NAME}/deepwiki/structured_docs.json"
else
    print_warning "Skipping DeepWiki documentation generation"
fi

# Step 5: Generate AI Documentation (CodeWiki)
if [[ "$SKIP_CODEWIKI" == false ]]; then
    print_step "Step 5: Generating AI Documentation (CodeWiki)"
    
    # Check if repository is cloned
    if [[ ! -d "$REPO_CLONE_PATH" ]]; then
        print_info "Repository not found at $REPO_CLONE_PATH"
        print_info "Cloning repository..."
        git clone "$GITHUB_REPO_URL" "$REPO_CLONE_PATH"
    else
        print_info "Using existing repository at $REPO_CLONE_PATH"
    fi
    
    # Check if codewiki is installed
    if ! command -v codewiki &> /dev/null; then
        print_warning "codewiki command not found. Please install CodeWiki first."
        print_info "Skipping CodeWiki generation..."
    else
        print_info "Generating CodeWiki documentation..."
        cd "$REPO_CLONE_PATH"
        codewiki generate -o .codewiki
        cd - > /dev/null
        
        print_info "Parsing CodeWiki documentation..."
        python src/docs_parser/parse_generated_docs.py \
            --input-dir "${REPO_CLONE_PATH}/.codewiki" \
            --output "data/${REPO_NAME}/codewiki"
        
        print_success "CodeWiki documentation generated and parsed"
        print_info "Created: data/${REPO_NAME}/codewiki/docs_tree.json"
        print_info "Created: data/${REPO_NAME}/codewiki/structured_docs.json"
    fi
else
    print_warning "Skipping CodeWiki documentation generation"
fi

# Step 6: Evaluate Documentation
print_step "Step 6: Evaluating Documentation"

# Evaluate DeepWiki
if [[ "$SKIP_DEEPWIKI" == false ]] && [[ -d "data/${REPO_NAME}/deepwiki" ]]; then
    print_info "Evaluating DeepWiki documentation..."
    bash ./src/run_evaluation_pipeline.sh \
        --repo-name "$REPO_NAME" \
        --models "$MODELS" \
        --batch-size "$BATCH_SIZE" \
        --reference "deepwiki" \
        $VIZ_FLAG
    
    print_success "DeepWiki evaluation completed"
    print_info "Results saved to data/${REPO_NAME}/deepwiki/evaluation_results/"
fi

# Evaluate CodeWiki
if [[ "$SKIP_CODEWIKI" == false ]] && [[ -d "data/${REPO_NAME}/codewiki" ]]; then
    print_info "Evaluating CodeWiki documentation..."
    bash ./src/run_evaluation_pipeline.sh \
        --repo-name "$REPO_NAME" \
        --models "$MODELS" \
        --batch-size "$BATCH_SIZE" \
        --reference "codewiki" \
        $VIZ_FLAG
    
    print_success "CodeWiki evaluation completed"
    print_info "Results saved to data/${REPO_NAME}/codewiki/evaluation_results/"
fi

# Final summary
print_step "Pipeline Completed Successfully!"

echo -e "${GREEN}All steps completed!${NC}\n"
echo "Results directory structure:"
echo "data/${REPO_NAME}/"
echo "├── original/"
echo "│   ├── ${DOCS_FOLDER}/                    # Downloaded official docs"
echo "│   ├── docs_tree.json                     # Parsed structure"
echo "│   └── structured_docs.json               # Parsed content"
echo "├── rubrics/"
echo "│   ├── {model}.json                       # Rubrics from each model"
echo "│   └── combined_rubrics.json              # Unified rubrics"

if [[ "$SKIP_DEEPWIKI" == false ]]; then
echo "├── deepwiki/"
echo "│   ├── doc/                               # Generated DeepWiki docs"
echo "│   ├── docs_tree.json                     # Parsed structure"
echo "│   ├── structured_docs.json               # Parsed content"
echo "│   └── evaluation_results/"
echo "│       ├── {model}.json                   # Evaluation from each model"
echo "│       └── combined_evaluation.json       # Combined results"
fi

if [[ "$SKIP_CODEWIKI" == false ]]; then
echo "└── codewiki/"
echo "    ├── docs_tree.json                     # Parsed structure"
echo "    ├── structured_docs.json               # Parsed content"
echo "    └── evaluation_results/"
echo "        ├── {model}.json                   # Evaluation from each model"
echo "        └── combined_evaluation.json       # Combined results"
fi

echo ""
print_info "You can now analyze the evaluation results and compare documentation quality!"
