# LitLoot - Book Search and Quiz Generator

LitLoot is a Flask-based web application that provides two main functionalities:
1. Book Search: Ask questions about books and literature
2. Quiz Generator: Generate multiple-choice quizzes based on book content

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd litloot_backend/LitLoot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
LITLOOT_DEBUG=true  # Set to false for production
```

## Running the Application

1. Start the Flask server:
```bash
python run.py
```

2. Access the test application in your web browser:
```
http://127.0.0.1:5001
```

## API Endpoints

### 1. Book Search (`/api/chat`)
- **Method**: POST
- **Endpoint**: `/api/chat`
- **Request Body**:
```json
{
    "query": "Your question about books or literature"
}
```
- **Response**:
```json
{
    "response": "Answer to your question"
}
```

### 2. Quiz Generator (`/api/quiz`)
- **Method**: POST
- **Endpoint**: `/api/quiz`
- **Request Body**:
```json
{
    "query": "Book topic or title"
}
```
- **Response**:
```json
{
    "book": "Book Title",
    "questions": [
        {
            "question": "Quiz question",
            "answers": ["Answer 1", "Answer 2", "Answer 3", "Answer 4"],
            "correct_index": 0,
            "difficulty": "easy|medium|hard",
            "type": "theme|character|plot|moral|interpretation"
        }
    ]
}
```

## Features

- **Book Search**: Ask questions about books and get AI-generated responses
- **Quiz Generator**: Create multiple-choice quizzes based on book content
- **Multiple Choice**: Each quiz question includes one correct answer and three plausible incorrect answers
- **Difficulty Levels**: Questions are categorized as easy, medium, or hard
- **Question Types**: Questions cover themes, characters, plot points, moral questions, and reader interpretation

## Project Structure

```
LitLoot/
├── app.py              # Main Flask application
├── run.py              # Application runner
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
├── templates/          # HTML templates
│   └── index.html      # Main web interface
├── static/             # Static files (CSS, JS, etc.)
├── routes/             # API route handlers
│   ├── chat.py         # Book search endpoint
│   └── quiz.py         # Quiz generation endpoint
├── services/           # Business logic
│   ├── openai_client.py
│   ├── quiz_generator.py
│   └── vector_store.py
├── utils/              # Utility functions
│   ├── logging.py
│   └── moderation.py
└── vector_index/       # Book data and embeddings
```

## Debug Mode

Debug mode can be enabled by setting `LITLOOT_DEBUG=true` in your `.env` file. When enabled:
- Detailed logs are printed to the console
- Debug information is saved to `litloot_debug.log`
- API responses include additional debugging information

## Troubleshooting

If you encounter a 403 error:
1. Ensure you're using port 5001 (not 5000)
2. Check that your `.env` file is properly configured
3. Verify that all dependencies are installed correctly
4. Make sure the virtual environment is activated

## License

[Add your license information here] 