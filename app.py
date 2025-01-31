import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
from gtts import gTTS  # For text-to-speech
import base64

# Load environment variables from the .env file
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Error handling for API Key
if not GOOGLE_API_KEY:
    st.error("🚨 GOOGLE_API_KEY is missing! Please check your .env file.")
    st.stop()

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.7)

# Define the prompt template for translation
translation_prompt = PromptTemplate(
    input_variables=["english_text"],
    template="Translate the following English text into Urdu only: '{english_text}'. Do not provide any additional information, only the translation.",
)

# Define the prompt template for pronunciation
pronunciation_prompt = PromptTemplate(
    input_variables=["english_text"],
    template="Provide the pronunciation of the following English text in English: '{english_text}'. Do not provide any additional information, only the pronunciation.",
)

# Define the prompt template for vocabulary/grammar check
vocab_grammar_prompt = PromptTemplate(
    input_variables=["english_text"],
    template="Analyze the following English text for vocabulary, grammar, synonyms, and antonyms: '{english_text}'. Provide the results in English only. Do not translate anything into Urdu.",
)

# Define the prompt template for synonyms and antonyms
synonyms_antonyms_prompt = PromptTemplate(
    input_variables=["english_text"],
    template="Provide a list of synonyms and antonyms for the following English word or phrase: '{english_text}'. Format the response as: Synonyms: [list] Antonyms: [list].",
)

# Define the prompt template for conversation
conversation_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="You are a friendly and helpful English language assistant. Respond to the following user input in a conversational manner: '{user_input}'.",
)

# Create LangChains for each task
translation_chain = LLMChain(llm=llm, prompt=translation_prompt, verbose=True)
pronunciation_chain = LLMChain(llm=llm, prompt=pronunciation_prompt, verbose=True)
vocab_grammar_chain = LLMChain(llm=llm, prompt=vocab_grammar_prompt, verbose=True)
synonyms_antonyms_chain = LLMChain(llm=llm, prompt=synonyms_antonyms_prompt, verbose=True)
conversation_chain = LLMChain(llm=llm, prompt=conversation_prompt, verbose=True)

def process_text_with_model(text, selected_option):
    """Process the input text and return a response based on the selected option."""
    if selected_option == "Translation":
        response = translation_chain.run(english_text=text)
    elif selected_option == "Pronunciation Guide":
        response = pronunciation_chain.run(english_text=text)
    elif selected_option == "Vocabulary Analysis":
        response = vocab_grammar_chain.run(english_text=text)
    elif selected_option == "Synonyms and Antonyms":
        response = synonyms_antonyms_chain.run(english_text=text)
    elif selected_option == "Conversation":
        response = conversation_chain.run(user_input=text)
    else:
        response = "Function not implemented yet."
    return response

def text_to_speech(text, language='en'):
    """Convert text to speech using gTTS and return the audio file."""
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save("pronunciation.mp3")
    return "pronunciation.mp3"

# Streamlit UI
st.title("📚 English Language Assistant")
st.write("Select one function at a time from the sidebar.")

# Sidebar for Function Selection
st.sidebar.header("Select a Function")
options = [
    "Translation", "Pronunciation Guide", "Vocabulary Analysis",
    "Synonyms and Antonyms", "Conversation"
]
selected_option = st.sidebar.radio("Choose one:", options)

# User Input Field
user_input = st.text_input("✍️ Enter a word or sentence:")

if user_input:
    if user_input.lower() == "end":
        st.success("✅ Session Ended! Goodbye! 👋")
    else:
        result = process_text_with_model(user_input, selected_option)
        
        if selected_option == "Translation":
            st.markdown("### 🔍 Translation to Urdu:")
            st.info(result)
        elif selected_option == "Pronunciation Guide":
            st.markdown("### 🔊 Pronunciation Guide:")
            st.info(result)
            
            # Add voice functionality
            st.markdown("#### 🎤 Listen to the Pronunciation:")
            audio_file = text_to_speech(result)
            st.audio(audio_file, format='audio/mp3')
        elif selected_option == "Vocabulary Analysis":
            st.markdown("### 🧠 Vocabulary and Phrase Analysis:")
            st.info(result)
        elif selected_option == "Synonyms and Antonyms":
            st.markdown("### 🔄 Synonyms and Antonyms:")
            st.info(result)
        elif selected_option == "Conversation":
            st.markdown("### 💬 Conversation:")
            st.info(result)
        else:
            st.warning("This function is not implemented yet.")