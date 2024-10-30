import streamlit as st
import os
import tempfile
import json
from AI_tutor import EconomicsTutor
from datetime import datetime

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "fr"
if "show_quiz" not in st.session_state:
    st.session_state.show_quiz = False
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "tutor" not in st.session_state:
    st.session_state.tutor = EconomicsTutor()

def display_interactive_quiz():
    """Display the interactive quiz with visual feedback"""
    if not st.session_state.current_quiz:
        return

    try:
        quiz = json.loads(st.session_state.current_quiz)
        
        if "questions" not in quiz:
            st.error("Erreur de format dans le quiz")
            return
            
        st.subheader("📝 Quiz")
        
        for i, question in enumerate(quiz["questions"]):
            st.markdown(f"### Question {i+1}: {question['question']}")
            question_key = f"q_{i}"
            
            for j, option in enumerate(question["options"]):
                answered = question_key in st.session_state.quiz_answers
                
                if answered:
                    if option["correct"]:
                        st.success(f"✅ {option['text']}")
                        if st.session_state.quiz_answers[question_key] == j:
                            st.markdown("*Votre réponse - Correct!*")
                            st.info(option["explanation"])
                    elif st.session_state.quiz_answers[question_key] == j:
                        st.error(f"❌ {option['text']}")
                        st.info(option["explanation"])
                    else:
                        st.write(option["text"])
                else:
                    if st.button(option["text"], key=f"{question_key}_opt_{j}", use_container_width=True):
                        st.session_state.quiz_answers[question_key] = j
                        st.rerun()
            
            st.markdown("---")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Recommencer", use_container_width=True):
                st.session_state.quiz_answers = {}
                st.rerun()
        with col2:
            if st.button("Retour à la conversation", use_container_width=True):
                st.session_state.show_quiz = False
                st.session_state.current_quiz = None
                st.rerun()
                
    except json.JSONDecodeError:
        st.error("Erreur de format dans le quiz. Veuillez réessayer.")
        if st.button("Retour", use_container_width=True):
            st.session_state.show_quiz = False
            st.rerun()
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        if st.button("Retour", use_container_width=True):
            st.session_state.show_quiz = False
            st.rerun()

def main():
    st.set_page_config(page_title="Assistant Économique", page_icon="📚", layout="wide")

    # Sidebar
    with st.sidebar:
        st.title("Gestion des Documents")

        if st.button("Initialiser/Recharger le Corpus", use_container_width=True):
            with st.spinner("Initialisation..."):
                try:
                    collection = st.session_state.tutor.initialize_corpus()
                    st.success("✅ Corpus initialisé!")
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")

        st.header("Ajouter des Documents")
        uploaded_files = st.file_uploader(
            "Télécharger des PDF",
            type=['pdf'],
            accept_multiple_files=True
        )

        if uploaded_files:
            for file in uploaded_files:
                with st.spinner(f"Traitement de {file.name}..."):
                    try:
                        if not os.path.exists(st.session_state.tutor.INITIAL_CORPUS_DIR):
                            os.makedirs(st.session_state.tutor.INITIAL_CORPUS_DIR)
                        file_path = os.path.join(st.session_state.tutor.INITIAL_CORPUS_DIR, file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.getvalue())
                        st.session_state.tutor.add_document_to_corpus(file_path)
                        st.success(f"✅ {file.name} ajouté")
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")

        st.header("Langue / Language")
        language = st.selectbox(
            "",
            options=["Français", "English"],
            index=0 if st.session_state.language == "fr" else 1
        )
        st.session_state.language = "fr" if language == "Français" else "en"

    # Main content area
    if not st.session_state.show_quiz:
        st.title("📚 Assistant Économique")
        st.markdown("""
        Je suis votre assistant en économie. Je peux :
        - Expliquer des concepts si vous me demandez des explications
        - Vous guider par des questions pour approfondir votre réflexion
        - Créer des quiz interactifs pour tester vos connaissances
        """)

        # Chat container
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Posez votre question..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Réflexion en cours..."):
                        response = st.session_state.tutor.handle_question(
                            prompt, 
                            st.session_state.language
                        )
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

        # Quiz and Clear buttons with consistent styling
        button_col1, button_col2, button_col3 = st.columns([1.2, 1.2, 3.6])
        with button_col1:
            if st.button("Créer un Quiz", key="create_quiz", use_container_width=True, type="primary"):
                st.session_state.show_quiz = True
                st.rerun()
            
        with button_col2:
            if st.button("Effacer la conversation", key="clear_chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    else:  # Quiz Interface
        st.title("📝 Générateur de Quiz")
        
        topic = st.text_input("Sujet du quiz", placeholder="ex: inflation, croissance économique...")
        
        quiz_col1, quiz_col2, quiz_col3 = st.columns([1.2, 1.2, 3.6])
        with quiz_col1:
            if st.button("Générer", key="generate_quiz", use_container_width=True, type="primary"):
                if topic:
                    with st.spinner("Création du quiz..."):
                        quiz = st.session_state.tutor.generate_quiz(
                            conversation_history=st.session_state.messages,
                            topic=topic,
                            language=st.session_state.language
                        )
                        try:
                            test_parse = json.loads(quiz)
                            if "questions" not in test_parse:
                                st.error("Erreur lors de la génération du quiz")
                                return
                            st.session_state.current_quiz = quiz
                            st.session_state.quiz_answers = {}
                        except json.JSONDecodeError:
                            st.error("Erreur lors de la génération du quiz")
                            return
                else:
                    st.warning("Veuillez entrer un sujet")
        
        with quiz_col2:
            if st.button("Retour", key="back_to_chat", use_container_width=True):
                st.session_state.show_quiz = False
                st.session_state.current_quiz = None
                st.rerun()
        
        if st.session_state.current_quiz:
            display_interactive_quiz()

if __name__ == "__main__":
    main()