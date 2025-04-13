import os
from typing import Final
from openai import OpenAI
from config import OPENAI_API_KEY

# Set the API key in the environment
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def get_client() -> OpenAI:
    return OpenAI(api_key=OPENAI_API_KEY) 