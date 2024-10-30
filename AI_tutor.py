from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
from anthropic import Anthropic
import os
import glob
import json
from typing import List, Dict, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EconomicsTutor:
    """A chatbot tutor that provides economics education using PDF documents and LLM."""
    
    def __init__(self, persist_directory: str = "chromadb_data", 
                 collection_name: str = "initial_corpus",
                 corpus_dir: str = "initial_corpus"):
        """Initialize the tutor with necessary configurations and clients."""
        self.PERSIST_DIRECTORY = persist_directory
        self.COLLECTION_NAME = collection_name
        self.INITIAL_CORPUS_DIR = corpus_dir
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not found")
        self.anthropic = Anthropic(api_key=api_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=self.PERSIST_DIRECTORY
        ))
        self.hf_embed = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Ensure corpus directory exists
        os.makedirs(self.INITIAL_CORPUS_DIR, exist_ok=True)

        # Teaching patterns and instructions by language
        self.instructions = {
            "fr": {
                "reflect": "Qu'en pensez-vous",
                "consider": "Regardons ensemble",
                "why": "Pourquoi",
                "experience": "Avez-vous déjà remarqué",
                "understand": "Je vous suis ?",
                "challenge": "Petit défi amusant",
                "imagine": "Imaginez avec moi",
                "great_q": "Excellente question !",
                "interesting": "C'est intéressant que vous posiez cette question"
            },
            "en": {
                "reflect": "What do you think",
                "consider": "Let's look together at",
                "why": "Why",
                "experience": "Have you noticed",
                "understand": "Am I making sense?",
                "challenge": "Fun quick challenge",
                "imagine": "Imagine with me",
                "great_q": "Great question!",
                "interesting": "That's an interesting question"
            }
        }
        
    def initialize_corpus(self):
        """Initialize or get the document collection."""
        try:
            collection = self.chroma_client.get_collection(
                name=self.COLLECTION_NAME,
                embedding_function=self.hf_embed
            )
            print(f"Found existing collection with {collection.count()} documents")
        except ValueError:
            collection = self.chroma_client.create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=self.hf_embed
            )
            print("Created new collection")
            
            pdf_files = glob.glob(os.path.join(self.INITIAL_CORPUS_DIR, "*.pdf"))
            if pdf_files:
                print(f"Found {len(pdf_files)} PDF files in {self.INITIAL_CORPUS_DIR}")
                for pdf_path in pdf_files:
                    self.add_document_to_corpus(pdf_path, collection)
                    print(f"Added {pdf_path} to corpus")
            else:
                print(f"No PDF files found in {self.INITIAL_CORPUS_DIR}.")
        
        return collection
    
    def add_document_to_corpus(self, pdf_path: str, 
                             collection: Optional[chromadb.Collection] = None) -> chromadb.Collection:
        """Add a new PDF document to the corpus."""
        if collection is None:
            collection = self.get_persistent_collection()
        
        reader = PdfReader(pdf_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        )
        chunks = text_splitter.split_text(text)
        
        start_id = collection.count()
        
        collection.add(
            documents=chunks,
            metadatas=[{"source": os.path.basename(pdf_path), "page": i} 
                      for i in range(len(chunks))],
            ids=[f"doc_{start_id + i}" for i in range(len(chunks))]
        )
        
        return collection

    def get_persistent_collection(self) -> chromadb.Collection:
        """Get or create the persistent collection."""
        try:
            return self.chroma_client.get_collection(
                name=self.COLLECTION_NAME,
                embedding_function=self.hf_embed
            )
        except ValueError:
            return self.initialize_corpus()

    def query_documents(self, query: str, n_results: int = 3) -> Dict:
        """Query the collection for relevant documents."""
        collection = self.get_persistent_collection()
        return collection.query(
            query_texts=[query],
            n_results=n_results
        )

    def generate_response(self, query: str, context: str, 
                         sources: List[str], language: str = "fr") -> str:
        """Generate a friendly, engaging response using Claude."""
        explanation_indicators = {
            "fr": ["explique", "expliques", "décris", "comment", "pourquoi", 
                  "qu'est-ce que", "quel est", "quelle est", "quels sont", "quelles sont"],
            "en": ["explain", "describe", "how", "why", "what is", "what are"]
        }

        is_explanation_request = any(
            indicator in query.lower() 
            for indicator in explanation_indicators[language]
        )

        prompt = f"""{self.anthropic.HUMAN_PROMPT}
You are a friendly and encouraging economics tutor who makes learning feel like an exciting conversation between friends. Your tone is warm and supportive, and you're genuinely interested in your student's thoughts and experiences.

Context from materials:
{context}

Student question: {query}

Personality traits to convey:
- Warm and welcoming
- Genuinely enthusiastic about economics
- Encouraging and supportive
- Patient and understanding
- Interested in student's perspectives

Communication style:
- Use friendly openings like "{'Ah, belle question!' if language == 'fr' else 'Ah, great question!'}"
- Add encouraging phrases
- Show enthusiasm with occasional "!" and positive reinforcement
- Use inclusive language to create a collaborative feeling
- Keep a conversational, natural tone

Choose ONE of these teaching patterns (or blend naturally if appropriate):

1. Friendly Socratic
2. Relatable Examples
3. Interactive Scenario
4. Comparative Discussion
5. Personal Connection

Style requirements:
- Keep responses warm and encouraging
- Use **bold** for key concepts
- Stay concise but friendly
- End with an inviting question

Response language: {'French' if language == 'fr' else 'English'}

Create a friendly, engaging response using your chosen pattern.{self.anthropic.AI_PROMPT}"""

        try:
            response = self.anthropic.completions.create(
                model="claude-2",
                prompt=prompt,
                max_tokens_to_sample=800,
                temperature=0.75
            )
            
            return response.completion.strip()
        except Exception as e:
            return f"{'Désolé, une erreur s\'est produite' if language == 'fr' else 'Sorry, an error occurred'}: {str(e)}"

    def handle_question(self, query: str, language: str = "fr") -> str:
        """Main handler for processing questions."""
        try:
            collection = self.get_persistent_collection()
            
            if collection.count() == 0:
                return "Le corpus est vide." if language == "fr" else "The corpus is empty."
                
            results = self.query_documents(query)
            context = " ".join(results["documents"][0])
            sources = [meta["source"] for meta in results["metadatas"][0]]
            
            return self.generate_response(query, context, sources, language)
            
        except Exception as e:
            return f"{'Erreur' if language == 'fr' else 'Error'}: {str(e)}"

    def generate_quiz(self, conversation_history: List[Dict], 
                     topic: str, difficulty: str = "intermediate", 
                     language: str = "fr") -> str:
        """
        Generate an interactive quiz about the given topic.
        
        Args:
            conversation_history: List of conversation messages with 'role' and 'content'
            topic: The economics topic to generate questions about
            difficulty: Difficulty level of the quiz (beginner, intermediate, advanced)
            language: Language for the quiz (fr or en)
            
        Returns:
            JSON string containing quiz questions and answers
        """
        try:
            results = self.query_documents(topic)
            corpus_context = " ".join(results["documents"][0]) if results["documents"] else ""
            
            conv_text = "\n".join([
                f"Q: {msg['content']}" if msg['role'] == 'user' else f"A: {msg['content']}"
                for msg in conversation_history
            ])

            prompt = f"""{self.anthropic.HUMAN_PROMPT}
Create an interactive economics quiz about {topic}. Return ONLY the JSON structure below with no additional text or explanations.

Context from materials:
{corpus_context}
{conv_text}

Return EXACTLY this structure and nothing else (no introduction or extra text):
{{
    "questions": [
        {{
            "question": "Write the first question here",
            "options": [
                {{
                    "text": "Correct answer",
                    "correct": true,
                    "explanation": "Why this is correct"
                }},
                {{
                    "text": "Wrong answer 1",
                    "correct": false,
                    "explanation": "Why this is incorrect"
                }},
                {{
                    "text": "Wrong answer 2",
                    "correct": false,
                    "explanation": "Why this is incorrect"
                }}
            ]
        }},
        {{
            "question": "Write the second question here",
            "options": [Similar structure]
        }},
        {{
            "question": "Write the third question here",
            "options": [Similar structure]
        }}
    ]
}}{self.anthropic.AI_PROMPT}"""

            response = self.anthropic.completions.create(
                model="claude-2",
                prompt=prompt,
                max_tokens_to_sample=2000,
                temperature=0.7
            )

            # Clean and validate the response
            cleaned_response = response.completion.strip()
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                cleaned_response = cleaned_response[start_idx:end_idx]

            # Validate JSON structure
            quiz_json = json.loads(cleaned_response)
            self._validate_quiz_structure(quiz_json)
            
            return cleaned_response
            
        except Exception as e:
            return json.dumps({
                "error": f"Quiz generation failed: {str(e)}",
                "raw_response": ""
            })

    def _validate_quiz_structure(self, quiz_json: Dict) -> None:
        """Validate the structure of the generated quiz JSON."""
        if not isinstance(quiz_json, dict) or "questions" not in quiz_json:
            raise ValueError("Invalid quiz structure")
        if len(quiz_json["questions"]) != 3:
            raise ValueError("Quiz must have exactly 3 questions")
        for question in quiz_json["questions"]:
            if not all(key in question for key in ["question", "options"]):
                raise ValueError("Question missing required fields")
            if len(question["options"]) != 3:
                raise ValueError("Each question must have exactly 3 options")
            if sum(1 for opt in question["options"] if opt.get("correct")) != 1:
                raise ValueError("Each question must have exactly one correct answer")

def main():
    """Main function to demonstrate usage."""
    # Initialize the tutor
    tutor = EconomicsTutor()
    
    # Example questions
    questions = [
        "Explique moi la croissance économique",
        "Quel est le meilleur taux d'inflation?",
        "Comment fonctionne le marché du travail?",
        "Est-ce que le chômage peut être égal à zéro?"
    ]
    
    # Process each question
    for question in questions:
        print("\nQuestion:", question)
        response = tutor.handle_question(question)
        print("\nResponse:", response)

    # Example quiz generation
    conversation_history = [
        {"role": "user", "content": "Explain economic growth"},
        {"role": "assistant", "content": "Economic growth refers to..."}
    ]
    quiz = tutor.generate_quiz(conversation_history, "economic growth")
    print("\nGenerated Quiz:", quiz)

if __name__ == "__main__":
    main()