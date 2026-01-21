import os
from pathlib import Path
from dotenv import load_dotenv

# Project root detection - find the directory containing this config file's parent
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Load .env file from multiple possible locations
env_file = None
possible_env_locations = [
    PROJECT_ROOT / ".env",           # Project root
    Path(__file__).parent / ".env",  # src directory
    Path.cwd() / ".env",             # Current working directory
]

for env_path in possible_env_locations:
    if env_path.exists():
        env_file = env_path
        break

if env_file:
    load_dotenv(env_file)
    print(f"Loaded .env from: {env_file}")
else:
    print(f"Warning: No .env file found. Searched in: {[str(p) for p in possible_env_locations]}")
    load_dotenv()  # Try default behavior as fallback

# Common data paths relative to project root
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"

API_KEY = os.getenv("API_KEY", "sk-1234")
MODEL = os.getenv("MODEL", "claude-sonnet-4")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
BASE_URL = os.getenv("BASE_URL", "http://localhost:4000/")
print(f"Using MODEL: {MODEL}, BASE_URL: {BASE_URL}")

def get_project_path(*paths):
    """Get a path relative to the project root"""
    return str(PROJECT_ROOT.joinpath(*paths))

def get_data_path(*paths):
    """Get a path relative to the data directory"""
    return str(DATA_DIR.joinpath(*paths))

# max tokens per tool response
MAX_TOKENS_PER_TOOL_RESPONSE = 36_000



