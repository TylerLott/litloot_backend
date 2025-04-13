from typing import Dict, Any, List, Tuple
import random
import json
from flask import Blueprint, request, jsonify, Response
from services.vector_store import search
from services.quiz_generator import generate_quiz
from utils.logging import log_response
import logging

quiz_bp: Blueprint = Blueprint("quiz", __name__)

def shuffle_answers(question: Dict[str, Any]) -> Dict[str, Any]:
    """Shuffle the answers and add the correct answer index."""
    all_answers = [question["correct_answer"]] + question["incorrect_answers"]
    random.shuffle(all_answers)
    correct_index = all_answers.index(question["correct_answer"])
    
    return {
        "question": question["question"],
        "answers": all_answers,
        "correct_index": correct_index,
        "difficulty": question["difficulty"],
        "type": question["type"]
    }

@quiz_bp.route("/api/quiz", methods=["POST"])
@log_response
def quiz() -> Response:
    query: str = request.json["query"]
    
    # Search for the book in the vector index
    try:
        results: List[Tuple[Dict[str, Any], int]] = search(query, k=1)
        if not results:
            return jsonify({
                "error": f"No books found matching '{query}'",
                "book": query,
                "questions": []
            }), 404
            
        result: Dict[str, Any]
        idx: int
        result, idx = results[0]
        
        # Get the book content
        with open(result["source_file"], "r", encoding="utf-8") as f:
            words: List[str] = f.read().split()
            start: int = result["book_index"] * 400
            chunk: str = " ".join(words[start:start+500])
            
        # Generate quiz questions
        quiz_data: List[Dict[str, Any]] = generate_quiz(result["title"], chunk)
        shuffled_questions = [shuffle_answers(q) for q in quiz_data]
        
        response_data = {
            "book": result["title"],
            "questions": shuffled_questions,
            "error": None
        }
        
        # Log the response data
        logging.info(f"Response data: {json.dumps(response_data, indent=2)}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error generating quiz: {str(e)}")
        return jsonify({
            "error": f"Failed to generate quiz: {str(e)}",
            "book": query,
            "questions": []
        }), 500
