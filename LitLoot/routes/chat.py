from typing import Dict, Any, List
from flask import Blueprint, request, jsonify, Response, session
from utils.openai_client import get_client
from utils.logging import log_response
from services.book_search import search_book
import logging
import json

chat_bp: Blueprint = Blueprint("chat", __name__)

def get_conversation_history() -> List[Dict[str, str]]:
    """Get the conversation history from the session"""
    if "conversation_history" not in session:
        session["conversation_history"] = []
    return session["conversation_history"]

def add_to_history(role: str, content: str, books: List[Dict[str, Any]] = None) -> None:
    """Add a message to the conversation history"""
    history = get_conversation_history()
    message = {"role": role, "content": content}
    if books:
        message["books"] = books
    history.append(message)
    session["conversation_history"] = history

def clear_history() -> None:
    """Clear the conversation history"""
    session["conversation_history"] = []

@chat_bp.route("/api/chat", methods=["POST"])
@log_response
def chat() -> Response:
    try:
        # Validate request
        if not request.json or "query" not in request.json:
            return jsonify({
                "error": "Missing 'query' in request body"
            }), 400
            
        query: str = request.json["query"]
        logging.info(f"Received chat query: {query}")
        
        # Add user message to history
        add_to_history("user", query)
        
        # Get conversation history
        history = get_conversation_history()
        logging.debug(f"Current conversation history: {json.dumps(history)}")
        
        # Prepare system message with tools
        system_message = """You are a helpful assistant that provides information about books and literature.
        You have access to a book search tool that can find books based on queries.
        When recommending books, use the search_book tool to find relevant books and include their content in your response.
        """
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": system_message},
            *history
        ]
        
        # Get OpenAI client
        client = get_client()
        
        # Define available tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_book",
                    "description": "Search for books in the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find relevant books"
                            },
                            "k": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 1
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        # Get response from OpenAI
        logging.info("Sending request to OpenAI")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=500
        )
        
        # Process the response
        message = response.choices[0].message
        logging.debug(f"OpenAI response: {message}")
        
        found_books = None
        
        # If the model wants to use a tool
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            if tool_call.function.name == "search_book":
                try:
                    # Parse arguments
                    args = json.loads(tool_call.function.arguments)
                    logging.info(f"Searching books with args: {args}")
                    
                    # Search for books
                    found_books = search_book(args["query"], args.get("k", 1))
                    logging.info(f"Found {len(found_books)} books")
                    
                    # Add tool response to history
                    add_to_history("assistant", f"I found these books: {json.dumps(found_books)}", found_books)
                    
                    # Get final response
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages + [
                            {"role": "assistant", "content": f"I found these books: {json.dumps(found_books)}"}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    message = response.choices[0].message
                except Exception as e:
                    logging.error(f"Error in book search: {str(e)}")
                    return jsonify({
                        "error": f"Failed to search books: {str(e)}"
                    }), 500
        
        # Add assistant response to history
        add_to_history("assistant", message.content, found_books)
        
        return jsonify({
            "response": message.content,
            "books": found_books
        })
        
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "error": f"Failed to get response from OpenAI: {str(e)}"
        }), 500

@chat_bp.route("/api/chat/clear", methods=["POST"])
def clear_chat() -> Response:
    """Clear the conversation history"""
    try:
        clear_history()
        return jsonify({"status": "success"})
    except Exception as e:
        logging.error(f"Error clearing chat history: {str(e)}")
        return jsonify({
            "error": f"Failed to clear chat history: {str(e)}"
        }), 500
