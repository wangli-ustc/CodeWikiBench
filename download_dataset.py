#!/usr/bin/env python3
"""
Download CodeWikiBench dataset from HuggingFace and populate examples/ directory.

Usage:
    python download_dataset.py                    # Download all repositories
    python download_dataset.py --repos OpenHands  # Download specific repo
    python download_dataset.py --list             # List available repos
"""

import json
import os
import argparse
from pathlib import Path
from typing import List, Optional

try:
    from datasets import load_dataset
except ImportError:
    print("Error: 'datasets' library not found.")
    print("Please install it: pip install datasets")
    exit(1)


# Color codes for output
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color


def print_info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")


def print_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")


def print_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")


def download_dataset(repo_names: Optional[List[str]] = None, output_dir: str = "examples"):
    """
    Download CodeWikiBench dataset from HuggingFace.
    
    Args:
        repo_names: List of specific repository names to download (None = all)
        output_dir: Output directory (default: examples)
    """
    print_info("Loading CodeWikiBench dataset from HuggingFace...")
    print_info("Dataset: anhnh2002/codewikibench")
    
    try:
        # Load dataset
        dataset = load_dataset("anhnh2002/codewikibench")
        print_success(f"Dataset loaded: {len(dataset['train'])} repositories")
    except Exception as e:
        print_error(f"Failed to load dataset: {e}")
        return
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each repository
    total = len(dataset['train'])
    processed = 0
    skipped = 0
    
    for idx, repo_data in enumerate(dataset['train']):
        repo_name = repo_data['repo_name']
        
        # Filter by repo names if specified
        if repo_names and repo_name not in repo_names:
            continue
        
        print(f"\n{'='*60}")
        print(f"[{idx+1}/{total}] Processing: {repo_name}")
        print(f"{'='*60}")
        
        # Create repository directory
        repo_dir = output_path / repo_name
        repo_dir.mkdir(parents=True, exist_ok=True)
        
        # Create original directory
        original_dir = repo_dir / "original"
        original_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save metadata
            metadata = {
                "repo_name": repo_data['repo_name'],
                "repo_url": repo_data['repo_url'],
                "commit_id": repo_data['commit_id']
            }
            metadata_file = original_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print_info(f"Saved: {metadata_file}")
            
            # Save docs_tree
            docs_tree = json.loads(repo_data['docs_tree'])
            docs_tree_file = original_dir / "docs_tree.json"
            with open(docs_tree_file, 'w', encoding='utf-8') as f:
                json.dump(docs_tree, f, indent=2, ensure_ascii=False)
            print_info(f"Saved: {docs_tree_file}")
            
            # Save structured_docs
            structured_docs = json.loads(repo_data['structured_docs'])
            structured_docs_file = original_dir / "structured_docs.json"
            with open(structured_docs_file, 'w', encoding='utf-8') as f:
                json.dump(structured_docs, f, indent=2, ensure_ascii=False)
            print_info(f"Saved: {structured_docs_file}")
            
            # Save rubrics
            rubrics = json.loads(repo_data['rubrics'])
            rubrics_file = repo_dir / "rubrics.json"
            with open(rubrics_file, 'w', encoding='utf-8') as f:
                json.dump(rubrics, f, indent=2, ensure_ascii=False)
            print_info(f"Saved: {rubrics_file}")
            
            # Calculate sizes
            docs_tree_size = docs_tree_file.stat().st_size / 1024  # KB
            structured_docs_size = structured_docs_file.stat().st_size / 1024  # KB
            
            print_success(f"✓ {repo_name} downloaded successfully")
            print(f"  - docs_tree.json: {docs_tree_size:.1f} KB")
            print(f"  - structured_docs.json: {structured_docs_size:.1f} KB")
            
            processed += 1
            
        except Exception as e:
            print_error(f"Failed to process {repo_name}: {e}")
            skipped += 1
            continue
    
    # Summary
    print(f"\n{'='*60}")
    print(f"{Colors.GREEN}Download Complete!{Colors.NC}")
    print(f"{'='*60}")
    print(f"Total repositories: {total}")
    print(f"Downloaded: {processed}")
    print(f"Skipped: {skipped}")
    print(f"Output directory: {output_path.absolute()}")


def list_repositories():
    """List all available repositories in the dataset."""
    print_info("Loading CodeWikiBench dataset...")
    
    try:
        dataset = load_dataset("anhnh2002/codewikibench")
        print_success(f"Found {len(dataset['train'])} repositories:\n")
        
        # Group by language
        repos_by_lang = {}
        for repo_data in dataset['train']:
            repo_name = repo_data['repo_name']
            repo_url = repo_data['repo_url']
            
            # Infer language from README (simplified)
            lang = "Unknown"
            if any(x in repo_url for x in ['Chart.js', 'marktext', 'puppeteer', 'storybook', 'mermaid', 'svelte']):
                lang = "JavaScript/TypeScript"
            elif any(x in repo_url for x in ['graphrag', 'rasa', 'OpenHands']):
                lang = "Python"
            elif any(x in repo_url for x in ['qmk_firmware', 'libsql', 'sumatrapdf', 'wazuh']):
                lang = "C"
            elif any(x in repo_url for x in ['electron', 'x64dbg', 'json']):
                lang = "C++"
            elif any(x in repo_url for x in ['FluentValidation', 'git-credential-manager', 'ml-agents']):
                lang = "C#"
            elif any(x in repo_url for x in ['logstash', 'material-components-android', 'trino']):
                lang = "Java"
            
            if lang not in repos_by_lang:
                repos_by_lang[lang] = []
            repos_by_lang[lang].append((repo_name, repo_url))
        
        # Print grouped by language
        for lang, repos in sorted(repos_by_lang.items()):
            print(f"{Colors.BLUE}{lang}:{Colors.NC}")
            for repo_name, repo_url in repos:
                print(f"  - {repo_name}")
                print(f"    {repo_url}")
            print()
        
    except Exception as e:
        print_error(f"Failed to load dataset: {e}")


def create_dataset_summary(output_dir: str = "examples"):
    """Create a summary JSON file of all downloaded repositories."""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print_error(f"Directory not found: {output_dir}")
        return
    
    summary = {
        "total_repositories": 0,
        "repositories": []
    }
    
    for repo_dir in sorted(output_path.iterdir()):
        if not repo_dir.is_dir():
            continue
        
        metadata_file = repo_dir / "original" / "metadata.json"
        if not metadata_file.exists():
            continue
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Count pages and requirements
            docs_tree_file = repo_dir / "original" / "docs_tree.json"
            rubrics_file = repo_dir / "rubrics.json"
            
            pages = 0
            requirements = 0
            
            if docs_tree_file.exists():
                with open(docs_tree_file, 'r') as f:
                    docs_tree = json.load(f)
                    # Count pages (count subpages only, not root)
                    def count_pages(node):
                        count = 0
                        if isinstance(node, dict) and 'subpages' in node:
                            for subpage in node['subpages']:
                                count += 1
                                count += count_pages(subpage)
                        return count
                    pages = count_pages(docs_tree)
            
            if rubrics_file.exists():
                with open(rubrics_file, 'r') as f:
                    rubrics_data = json.load(f)
                    # Handle both formats: direct list or dict with 'rubrics' key
                    rubrics = rubrics_data.get('rubrics', rubrics_data) if isinstance(rubrics_data, dict) and 'rubrics' in rubrics_data else rubrics_data
                    # Count requirements (leaf nodes)
                    def count_requirements(items):
                        count = 0
                        for item in items:
                            if 'sub_tasks' in item and item['sub_tasks']:
                                count += count_requirements(item['sub_tasks'])
                            else:
                                count += 1
                        return count
                    requirements = count_requirements(rubrics)
            
            summary["repositories"].append({
                "name": metadata['repo_name'],
                "url": metadata['repo_url'],
                "commit": metadata['commit_id'],
                "pages": pages,
                "requirements": requirements
            })
            summary["total_repositories"] += 1
            
        except Exception as e:
            print_warning(f"Could not process {repo_dir.name}: {e}")
            continue
    
    # Save summary
    summary_file = output_path / "dataset_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print_success(f"Summary saved to: {summary_file}")
    print(f"Total repositories: {summary['total_repositories']}")


def main():
    parser = argparse.ArgumentParser(
        description="Download CodeWikiBench dataset from HuggingFace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all repositories
  python download_dataset.py
  
  # Download specific repositories
  python download_dataset.py --repos OpenHands Chart.js
  
  # List available repositories
  python download_dataset.py --list
  
  # Create summary after download
  python download_dataset.py --summary
  
  # Download to custom directory
  python download_dataset.py --output my_examples
        """
    )
    
    parser.add_argument(
        '--repos',
        nargs='+',
        help='Specific repository names to download (default: all)'
    )
    
    parser.add_argument(
        '--output',
        default='examples',
        help='Output directory (default: examples)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available repositories'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Create dataset summary JSON'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_repositories()
    elif args.summary:
        create_dataset_summary(args.output)
    else:
        download_dataset(args.repos, args.output)
        
        # Optionally create summary after download
        if not args.repos:  # Only if downloading all
            print("\nCreating dataset summary...")
            create_dataset_summary(args.output)


if __name__ == "__main__":
    main()
