# Economics Tutor Chatbot

An intelligent tutoring system that provides personalized economics education using PDF documents and Claude AI. The system features interactive conversations, document-based learning, and quiz generation capabilities.

## Features

- 🎓 Friendly, conversational economics tutoring
- 📚 PDF document integration for custom learning material
- 💬 Multilingual support (English and French)
- 🧠 Intelligent context-aware responses
- 📝 Interactive quiz generation
- 🔍 Semantic search across learning materials

## Prerequisites

- Python 3.8+
- Anthropic API key
- PDF documents for the knowledge base

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/economics-tutor-chatbot.git
cd economics-tutor-chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

4. Add PDF documents:
```bash
# Place your PDF documents in the initial_corpus directory
mkdir initial_corpus
# Copy your PDF files into initial_corpus/
```

## Usage

Basic usage example:

```python
from economics_tutor import EconomicsTutor

# Initialize the tutor
tutor = EconomicsTutor()

# Ask a question
response = tutor.handle_question(
    "Explain economic growth",
    language="en"  # or "fr" for French
)
print(response)

# Generate a quiz
quiz = tutor.generate_quiz(
    conversation_history=[],
    topic="economic growth",
    difficulty="intermediate"
)
print(quiz)
```

## Project Structure

```
economics-tutor-chatbot/
├── economics_tutor.py     # Main implementation
├── initial_corpus/        # Directory for PDF documents
├── chromadb_data/        # Persistent storage for embeddings
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables (not in git)
└── README.md            # This file
```

## Configuration

The system can be configured through environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
