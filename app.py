import os
import time
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS  # type: ignore[import-untyped]
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Ensure API key is available
if not GOOGLE_API_KEY:
    st.error("🚨 GOOGLE_API_KEY is missing! Please check your .env file.")
    st.stop()

# Initialize session state for caching and rate limiting
if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}
if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0

# Rate limiting: minimum 2 seconds between requests
RATE_LIMIT_SECONDS = 2

# Initialize LLM model (ensure model name is valid)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)  # Ensure to set the API key in the environment or configuration
prompt_template = PromptTemplate(
    input_variables=["text"],
    template="""
You are an English language translation expert. Your goal is to provide accurate, context-sensitive Urdu translation of English words and sentences while helping learners understand and apply the content effectively. Follow these detailed steps for translation:

### 1. *Translation*:
   - Translate the following text into Urdu:
     "{text}"
   - Ensure the translation is:
     - *Accurate*: Retain the original meaning and context of the text.
     - *Culturally Appropriate*: Use expressions and terms that align with Urdu language norms and cultural sensibilities.
     - *Intention*: Adjust the tone to match the intent of the original text (e.g., conversational, formal, poetic, etc.).

### 2. *Pronunciation Guide*:
   - Provide pronunciation of the input word to help learners unfamiliar with English.

### 3. *Definition*:
   If the input is in the form of text, provide:
   - A clear and simple definition with *Urdu meanings*.
   - Two or Three relevant synonyms and antonyms of the words in English with *Urdu meanings*.
   - An example sentence to demonstrate proper usage in context.
   - Translation in Roman Urdu to help learners unfamiliar with the Urdu script.

### 4. *Vocabulary Analysis*:
   - Analyze the *input word* and provide:
     - Details on usage, formality, and difficulty level (beginner, intermediate, advanced).

### 5. *Grammar and Structure*:
   - Identify notable grammatical structures in the text (e.g., verb tenses, clauses, sentence types) and explain how they are represented in Urdu.

### 6. *Corrections*:
    - Check for any grammar, spelling, or sentence structure errors in the input and suggest improvements.

### Response Formatting:
   - Organize your response into clear sections with headings (e.g., Translation, Pronunciation, Vocabulary, etc.).
   - Use simple and concise language to ensure clarity.
   - Adopt an encouraging tone to motivate learners in their English language journey.
"""
)

# Create LangChain
translation_chain = LLMChain(llm=llm, prompt=prompt_template)

def process_text_with_model(text):
    """Process input text and return AI-generated response."""
    response = translation_chain.run(text=text)
    return response  # Returning plain text instead of JSON

def text_to_speech(text, speed="normal"):
    """Convert text to speech using gTTS and return the audio file path."""
    try:
        clean_text = " ".join(text.split())  # Remove extra spaces
        clean_text = clean_text.replace("*", "").replace("#", "")  # Remove markdown symbols
        
        slow = True if speed == "slow" else False
        tts = gTTS(text=clean_text, lang='en', slow=slow)
        audio_path = "pronunciation.mp3"
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"Failed to generate audio: {e}")
        return None

def extract_section(response, section_title):
    """Extract a specific section from the response based on the section title."""
    sections = response.split("###")
    for section in sections:
        if section_title in section:
            return section.strip()
    return "Section not found."

# ─────────────────────────────
# 🎨 Streamlit UI Design
st.set_page_config(page_title="📚 AI-Powered English Learning Assistant", page_icon="📚", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stTextInput input {
        padding: 10px;
        font-size: 16px;
    }
    .stRadio div {
        flex-direction: row;
        gap: 10px;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #4CAF50;
    }
    .stSpinner div {
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Main title and description
st.title("📚 AI-Powered English Learning Assistant")
st.write("""
Welcome to the AI-powered English Learning Assistant! This tool helps you learn English by providing translations, pronunciation guides, definitions, grammar analysis, and more. Enter a word or sentence below to get started.
""")

# Sidebar for function selection
st.sidebar.header("Select a Function")
options = ["Translation", "Pronunciation Guide", "Definition", "Grammar and Structure", "Vocabulary Analysis", "Corrections"]
selected_option = st.sidebar.radio("Choose one:", options)

# User input field
user_input = st.text_input("✍️ Enter a word or sentence:", placeholder="Type here...")

# Process input and display results
if user_input:
    if user_input.lower() == "end":
        st.success("✅ Session Ended! Goodbye! 👋")
    else:
        with st.spinner("Processing your request..."):  # Add a loading spinner
            result = process_text_with_model(user_input)
        
        if selected_option == "Translation":
            st.markdown("### 🔍 Translation to Urdu:")
            translation_section = extract_section(result, "Translation")
            st.info(translation_section)
        elif selected_option == "Pronunciation Guide":
            st.markdown("### 🔊 Pronunciation Guide:")
            pronunciation_section = extract_section(result, "Pronunciation Guide")
            st.info(pronunciation_section)
            
            # Add speed control for pronunciation
            st.markdown("#### ⚙️ Pronunciation Speed")
            speed = st.radio("Select speed:", ["Normal", "Slow"], index=0)
            
            # Add voice functionality
            st.markdown("#### 🎤 Listen to the Pronunciation:")
            audio_file = text_to_speech(pronunciation_section, speed.lower())
            if audio_file:
                st.audio(audio_file, format='audio/mp3')
        elif selected_option == "Definition":
            st.markdown("### 📚 Definition:")
            definition_section = extract_section(result, "Definition")
            st.info(definition_section)
        elif selected_option == "Vocabulary Analysis":
            st.markdown("### 🧠 Vocabulary and Phrase Analysis:")
            vocabulary_section = extract_section(result, "Vocabulary Analysis")
            st.info(vocabulary_section)
        elif selected_option == "Grammar and Structure":
            st.markdown("### 📏 Grammar and Structure:")
            grammar_section = extract_section(result, "Grammar and Structure")
            st.info(grammar_section)
        elif selected_option == "Corrections":
            st.markdown("### ✍️ Corrections:")
            corrections_section = extract_section(result, "Corrections")
            st.info(corrections_section)

# Completion message
st.success("✅ AI English Assistant Ready!")
