from openai import OpenAI
import logging
from config import OPENAI_API_KEY
from utils.decorators import with_retry

# Initialize the client with the API key
client = OpenAI()

@with_retry()
def ask_openai(prompt, temperature=0.7, model="gpt-3.5-turbo", max_tokens=800):
    logging.info(f"Querying OpenAI with prompt of length {len(prompt)}")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
