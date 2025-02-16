import streamlit as st
import cv2
import pytesseract
import easyocr
import numpy as np
import os
from groq import Groq
from PIL import Image
import sys
import locale

# Ensure UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

# Set Groq API Key
GROQ_API_KEY = "your_groq_api_key_here"  # Replace with your actual API key
client = Groq(api_key=GROQ_API_KEY)

# Initialize EasyOCR Reader
reader = easyocr.Reader(["en"])

# Ensure Tesseract is correctly configured (Windows users must set this path)
TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Update if needed
if os.name == "nt":  # Windows
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Store session state variables
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""

if "translated_response" not in st.session_state:
    st.session_state.translated_response = ""

def extract_text_tesseract(image):
    """Extract text using Tesseract OCR."""
    try:
        image = np.array(image)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Error in Tesseract OCR: {str(e)}"

def analyze_text_with_groq(text):
    """Analyze extracted text using Groq AI."""
    if not GROQ_API_KEY:
        return "Error: Groq API key is not set."

    try:
        st.session_state.conversation_history.append({
            "role": "user", 
            "content": f"Analyze the following text for nutritional insights:\n\n{text}"
        })

        chat_completion = client.chat.completions.create(
            messages=st.session_state.conversation_history,
            model="mixtral-8x7b-32768",
            stream=False,
        )

        response = chat_completion.choices[0].message.content if chat_completion.choices else "Error: No response from Groq AI."
        
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
        st.session_state.ai_response = response  # Store response
        return response
    except Exception as e:
        return f"Error connecting to Groq API: {str(e)}"

def translate_text_to_hindi(text):
    """Translate given text to Hindi using Groq AI."""
    try:
        translation_prompt = f"Translate the following text into Hindi:\n\n{text}"
        st.session_state.conversation_history.append({"role": "user", "content": translation_prompt})
        
        chat_completion = client.chat.completions.create(
            messages=st.session_state.conversation_history,
            model="mixtral-8x7b-32768",
            stream=False,
        )
        
        translated_text = chat_completion.choices[0].message.content if chat_completion.choices else "Error: No response from Groq AI."
        
        st.session_state.conversation_history.append({"role": "assistant", "content": translated_text})
        st.session_state.translated_response = translated_text  # Store translated response
        return translated_text
    except Exception as e:
        return f"Translation Error: {str(e)}"

# Streamlit UI
st.title("📸 NutriScan - AI Nutrition Chatbot")
st.write("Upload a food label image to extract nutritional information and analyze it using AI.")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    st.write("🔍 Extracting text from image...")
    extracted_text = extract_text_tesseract(image)
    st.session_state.extracted_text = extracted_text
    st.text_area("Extracted Text", extracted_text, height=150)

    if st.button("Analyze with AI"):
        st.write("🤖 AI is analyzing...")
        analysis = analyze_text_with_groq(extracted_text)
        st.success("✅ AI Analysis Complete!")
        st.session_state.ai_response = analysis  # Store analysis
        st.session_state.translated_response = ""  # Reset translation
       
    # Display AI response
    if st.session_state.ai_response:
        st.text_area("AI Response", st.session_state.ai_response, height=200)

        # Translation button
        if st.button("Translate to Hindi"):
            translated_analysis = translate_text_to_hindi(st.session_state.ai_response)
            st.session_state.translated_response = translated_analysis  # Store translated response

    # Display Translated Response
    if st.session_state.translated_response:
        st.text_area("AI Response in Hindi", st.session_state.translated_response, height=200)

# Chatbot Section
st.subheader("💬 Chat with AI")
user_question = st.text_input("Ask a question about the extracted information:")

if st.button("Ask AI"):
    if user_question:
        question_with_context = f"User question: {user_question}\n\nHere is the nutritional text extracted from the image:\n{st.session_state.extracted_text}"
        response = analyze_text_with_groq(question_with_context)
        st.session_state.ai_response = response  # Store chatbot response
        st.session_state.translated_response = ""  # Reset translation

    # Display Chatbot Response
    if st.session_state.ai_response:
        st.text_area("AI Response", st.session_state.ai_response, height=150)

        # Translation button for chat response
        if st.button("Translate Chat Response to Hindi"):
            translated_chat_response = translate_text_to_hindi(st.session_state.ai_response)
            st.session_state.translated_response = translated_chat_response  # Store translation

    # Display Translated Chat Response
    if st.session_state.translated_response:
        st.text_area("AI Chat Response in Hindi", st.session_state.translated_response, height=150)
