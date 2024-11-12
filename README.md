# AI Assessment Tutor for Macroeconomics

An AI system that evaluates student understanding of macroeconomics through adaptive assessment, real-time feedback, and performance tracking.

## Features

- 📊 Real-time assessment and progress tracking
- 📝 Adaptive questioning and difficulty adjustment
- 🎯 Instant feedback on responses and misconceptions
- 📈 Performance analytics and gap identification
- 🎓 Evaluates key competencies:
  - Concept mastery
  - Math skills
  - Graph analysis
  - Policy understanding
  - Data interpretation
- 📚 Course material integration
- 💬 English and French support

## Prerequisites

- Python 3.8+
- Anthropic API key
- PDF documents for the knowledge base

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/macroeconomics-tutor-chatbot.git
cd macroeconomics-tutor-chatbot
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
from macroeconomics_tutor import MacroeconomicsTutor

# Initialize the tutor
tutor = MacroeconomicsTutor()

# Ask a question
response = tutor.handle_question(
    "Explain how monetary policy affects aggregate demand",
    language="en"  # or "fr" for French
)
print(response)

# Generate a quiz
quiz = tutor.generate_quiz(
    conversation_history=[],
    topic="monetary policy",
    difficulty="intermediate"
)
print(quiz)
```

## Topics Covered

The tutor is designed to help with various macroeconomic topics including:
- Aggregate Supply and Demand
- Monetary and Fiscal Policy
- Economic Growth and Development
- Inflation and Price Levels
- International Trade and Exchange Rates
- Business Cycles
- Employment and Unemployment
- National Income Accounting

## Project Structure

```
macroeconomics-tutor-chatbot/
├── macroeconomics_tutor.py     # Main implementation
├── initial_corpus/        # Directory for PDF documents
├── chromadb_data/        # Persistent storage for embeddings
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables (not in git)
└── README.md            # This file
```

## Configuration

The system can be configured through environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key

## License

This project is licensed under the MIT License - see the LICENSE file for details.
