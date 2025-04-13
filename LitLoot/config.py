from typing import Final
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY: Final[str] = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Vector Index Paths
VECTOR_INDEX_PATH: Final[str] = "vector_index/books.index"
METADATA_PATH: Final[str] = "vector_index/metadata.json"

# Debug Mode
DEBUG: Final[bool] = os.getenv("LITLOOT_DEBUG", "false").lower() == "true"
print(f"Debug mode is {'enabled' if DEBUG else 'disabled'}")
