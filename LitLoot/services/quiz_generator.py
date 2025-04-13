import json
import logging
from collections import Counter

from .openai_client import ask_openai
from utils.cache import get_or_set

PROMPT_VERSION = "quiz-v2-multiple-choice"

def _generate_quiz_internal(title, text_chunk):
    prompt = f"""
You are a literary quiz generator. Create a structured quiz based on the excerpt from the book titled "{title}". Your questions should focus on **themes**, **character arcs**, **moral questions**, and **reader interpretation**.

Each quiz item must be a JSON object with:
- "question": The quiz question
- "correct_answer": The correct answer
- "incorrect_answers": A list of exactly 3 plausible but incorrect answers
- "difficulty": easy, medium, hard
- "type": theme, character, plot, moral, interpretation

The incorrect answers should be:
1. Plausible but wrong
2. Related to the topic
3. Not obviously incorrect
4. Different from each other

Return a JSON list of exactly 10 items.

Excerpt:
\"\"\"
{text_chunk}
\"\"\"
"""
    def task():
        response = ask_openai(prompt)
        try:
            parsed = json.loads(response)
            if isinstance(parsed, list) and all("question" in q and "correct_answer" in q and "incorrect_answers" in q for q in parsed):
                return parsed
        except Exception:
            pass
        return [{
            "question": "Could not generate a structured quiz.",
            "correct_answer": "N/A",
            "incorrect_answers": ["N/A", "N/A", "N/A"],
            "difficulty": "medium",
            "type": "error"
        }] * 10

    return get_or_set(f"{title}-quiz-{text_chunk[:80]}", task)

def is_too_difficult(quiz_items):
    difficulties = Counter(item["difficulty"] for item in quiz_items)
    return difficulties.get("hard", 0) >= 6

def regenerate_quiz_if_needed(title, chunk, original_quiz):
    if not is_too_difficult(original_quiz):
        return original_quiz

    previous_context = "\n".join(
        f"Q: {q['question']}\nA: {q['correct_answer']}" for q in original_quiz
    )

    prompt = f"""
The following quiz was too difficult. Please regenerate simpler questions using this context:

\"\"\"
{previous_context}
\"\"\"

Excerpt:
\"\"\"
{chunk}
\"\"\"

Return JSON list with fields: question, correct_answer, incorrect_answers (list of 3), difficulty, type.
"""

    def regen_task():
        response = ask_openai(prompt)
        try:
            return json.loads(response)
        except Exception:
            return original_quiz

    return get_or_set(f"{title}-regen-{chunk[:80]}", regen_task)

def log_quiz_metrics(title, quiz_items):
    difficulties = Counter(item["difficulty"] for item in quiz_items)
    types = Counter(item["type"] for item in quiz_items)
    logging.info(f"Quiz for '{title}': {dict(difficulties)} types: {dict(types)}")

def generate_quiz(title, chunk):
    quiz = _generate_quiz_internal(title, chunk)
    log_quiz_metrics(title, quiz)

    if is_too_difficult(quiz):
        logging.info(f"Regenerating quiz for '{title}' due to high difficulty...")
        quiz = regenerate_quiz_if_needed(title, chunk, quiz)
        log_quiz_metrics(f"{title} (regenerated)", quiz)

    return quiz
