import os
import json
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

# Load environment variables from the .env file
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Error handling for API Key
if not GOOGLE_API_KEY:
    st.error("🚨 GOOGLE_API_KEY is missing! Please check your .env file.")

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.7)

# Define a PromptTemplate to generate responses
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

# Create LangChains for each task
translation_chain = LLMChain(llm=llm, prompt=translation_prompt, verbose=True)
pronunciation_chain = LLMChain(llm=llm, prompt=pronunciation_prompt, verbose=True)
vocab_grammar_chain = LLMChain(llm=llm, prompt=vocab_grammar_prompt, verbose=True)

# Create LangChain
translation_chain = LLMChain(llm=llm, prompt=prompt_template)

def process_text_with_model(text):
    """Process the input text and return a structured response."""
    response = translation_chain.run(text=text)
    
    # Ensure response is valid JSON
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        clean_json = response[json_start:json_end]
        response_json = json.loads(clean_json)  # Convert to JSON
        return response_json
    except json.JSONDecodeError:
        return {"error": "AI model returned an invalid JSON format. Please try again."}

# Streamlit UI
st.title("📚 English Language Assistant")
st.write("Select one function at a time from the sidebar.")

# Sidebar for Function Selection
st.sidebar.header("Select a Function")
options = [
    "Translation", "Pronunciation Guide", "Definition", 
    "Vocabulary Analysis", "Grammar Explanation", "Corrections"
]
selected_option = st.sidebar.radio("Choose one:", options)

# User Input Field
user_input = st.text_input("✍️ Enter a word or sentence:")

if user_input:
    if user_input.lower() == "end":
        st.success("✅ Session Ended! Goodbye! 👋")
    else:
        result = process_text_with_model(user_input)
        
        if "error" in result:
            st.error(result["error"])
        else:
            if selected_option == "Translation":
                st.markdown("### 🔍 Translation to Urdu:")
                st.info(result.get("translation", "No translation available."))
            elif selected_option == "Pronunciation Guide":
                st.markdown("### 🔊 Pronunciation Guide:")
                st.info(result.get("pronunciation", "No pronunciation available."))
            elif selected_option == "Definition":
                st.markdown("### 📚 Definition:")
                st.info(result.get("definition", "No definition available."))
            elif selected_option == "Vocabulary Analysis":
                st.markdown("### 🧠 Vocabulary and Phrase Analysis:")
                st.info(result.get("vocabulary", "No vocabulary analysis available."))
            elif selected_option == "Grammar Explanation":
                st.markdown("### 📏 Grammar and Structure:")
                st.info(result.get("grammar", "No grammar explanation available."))
            elif selected_option == "Corrections":
                st.markdown("### ✍️ Corrections:")
                st.info(result.get("corrections", "No corrections available."))
