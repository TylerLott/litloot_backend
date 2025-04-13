from typing import Dict, Any, List, Tuple
from services.vector_store import search

def search_book(query: str, k: int = 1) -> List[Dict[str, Any]]:
    """
    Search for books in the vector index and return detailed information.
    
    Args:
        query: The search query
        k: Number of results to return
        
    Returns:
        List of book dictionaries with title, author, and content
    """
    results = search(query, k=k)
    books = []
    
    for result, idx in results:
        # Get the book content
        with open(result["source_file"], "r", encoding="utf-8") as f:
            words = f.read().split()
            start = result["book_index"] * 400
            chunk = " ".join(words[start:start+500])
            
        books.append({
            "title": result["title"],
            "author": result["author"],
            "content": chunk
        })
    
    return books 