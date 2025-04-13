import os
import json
import faiss
import requests
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer

# --- Config ---
OUTPUT_DIR = "vector_index"
BOOKS_DIR = os.path.join(OUTPUT_DIR, "books")
NUM_BOOKS = 2
CHUNK_SIZE = 500
OVERLAP = 100

# --- Setup ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(BOOKS_DIR, exist_ok=True)
model = SentenceTransformer("all-MiniLM-L6-v2")
BASE_URL = "https://www.gutenberg.org"

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in " .-_").rstrip()

def get_top_book_urls(limit=NUM_BOOKS):
    print("Fetching top books...")
    resp = requests.get(BASE_URL + "/browse/scores/top")
    soup = BeautifulSoup(resp.text, "html.parser")
    top_ebooks = soup.find("h2", string="Top 100 EBooks yesterday")
    links = top_ebooks.find_next("ol").find_all("a", limit=limit)
    return [BASE_URL + link["href"] for link in links]

def get_plaintext_link(book_page_url):
    resp = requests.get(book_page_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    for link in soup.select("a[href]"):
        href = link["href"]
        if "txt" in href and "zip" not in href:
            return BASE_URL + href if href.startswith("/") else href
    return None

def download_book(book_url):
    try:
        response = requests.get(book_url)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return None

def chunk_text(text):
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE - OVERLAP):
        chunk = " ".join(words[i:i + CHUNK_SIZE])
        if chunk:
            chunks.append(chunk)
    return chunks

def process_books():
    all_chunks = []
    all_meta = []
    urls = get_top_book_urls()
    book_count = 0

    for url in tqdm(urls):
        if book_count >= NUM_BOOKS:
            break

        book_id = url.split("/")[-1]
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        title = soup.find("h1").text.strip()
        author_tag = soup.find("a", rel="marcrel:aut")
        author = author_tag.text.strip() if author_tag else "Unknown"

        txt_url = get_plaintext_link(url)
        if not txt_url:
            continue

        text = download_book(txt_url)
        if not text or len(text.split()) < 1000:
            continue

        filename = sanitize_filename(title) + ".txt"
        local_path = os.path.join(BOOKS_DIR, filename)

        with open(local_path, "w", encoding="utf-8") as f:
            f.write(text)

        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_meta.append({
                "title": title,
                "author": author,
                "book_index": i,
                "source_file": local_path,
                "gutenberg_url": txt_url
            })

        book_count += 1
        print(f"✔ {title} by {author} - {len(chunks)} chunks")

    return all_chunks, all_meta

def build_vector_index(chunks, metadata):
    print("Generating embeddings...")
    embeddings = model.encode(chunks, convert_to_numpy=True)

    print("Saving vector DB...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, os.path.join(OUTPUT_DIR, "books.index"))
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    chunks, meta = process_books()
    build_vector_index(chunks, meta)
    print(f"✅ Done! Embedded {len(chunks)} chunks from {len(set(m['title'] for m in meta))} books.")
