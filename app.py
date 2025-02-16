import streamlit as st
import mysql.connector
import pytesseract
import easyocr
import numpy as np
import os
from groq import Groq
from PIL import Image
import sys
import locale
import requests

# Ensure UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

# Set Groq API Key
GROQ_API_KEY = ""  # Replace with actual API key
client = Groq(api_key=GROQ_API_KEY)

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin@123",
    "database": "plate"
}

# Initialize EasyOCR Reader
reader = easyocr.Reader(["en"])

# Ensure Tesseract is correctly configured (Windows users must set this path)
TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Update if needed
if os.name == "nt":  # Windows
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Initialize Session State
session_vars = ["conversation_history", "extracted_text", "ai_response", "translated_response", "user_health_data"]
for var in session_vars:
    if var not in st.session_state:
        st.session_state[var] = [] if var == "conversation_history" else ""

# Function to Connect to MySQL Database
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Function to Fetch User Health Data Based on ID
def fetch_health_data(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM health_data WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            return user_data
        else:
            return None
    except Exception as e:
        return f"Database Error: {str(e)}"

# Function to Extract Text using Tesseract OCR
def extract_text_tesseract(image):
    try:
        image = np.array(image)
        text = pytesseract.image_to_string(image).strip()
        return text if text else "No text detected."
    except Exception as e:
        return f"Error in Tesseract OCR: {str(e)}"

# Function to Analyze Health Data & Extracted Text using Groq AI
def analyze_text_with_groq(text, health_data):
    if not GROQ_API_KEY:
        return "Error: Groq API key is not set."

    health_context = f"""
    User's Health Data:
    - Name: {health_data['name']}
    - Current Health: {health_data['current_health']}
    - Past Health: {health_data['past_health']}
    
    Now analyze the following extracted text:
    {text}
    Based on the user's past and present health data, give recommendations.
    """

    try:
        st.session_state.conversation_history.append({"role": "user", "content": health_context})

        chat_completion = client.chat.completions.create(
            messages=st.session_state.conversation_history,
            model="mixtral-8x7b-32768",
            stream=False,
        )

        response = chat_completion.choices[0].message.content if chat_completion.choices else "Error: No response from AI."
        
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
        st.session_state.ai_response = response
        return response
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

# Function to Translate Text to Hindi using Groq AI
def translate_text_to_hindi(text):
    try:
        translation_prompt = f"Translate the following text into Hindi:\n\n{text}"
        st.session_state.conversation_history.append({"role": "user", "content": translation_prompt})

        chat_completion = client.chat.completions.create(
            messages=st.session_state.conversation_history,
            model="mixtral-8x7b-32768",
            stream=False,
        )

        translated_text = chat_completion.choices[0].message.content if chat_completion.choices else "Error: No response from AI."
        
        st.session_state.conversation_history.append({"role": "assistant", "content": translated_text})
        st.session_state.translated_response = translated_text
        return translated_text
    except Exception as e:
        return f"Translation Error: {str(e)}"

def fetch_health_data(user_id):
    try:
        api_url = f"http://localhost:5000/get/{user_id}"  # API Endpoint
        response = requests.get(api_url)

        if response.status_code == 200:
            health_data = response.json()  # Convert JSON response to Python dictionary
            return health_data
        else:
            return f"API Error: {response.status_code} - {response.text}"  # Handle API failure

    except Exception as e:
        return f"Request Error: {str(e)}"  # Handle connection errors

# Streamlit UI 

st.title("📸 NutriScan - AI Nutrition Chatbot")
st.write("Enter your user ID to fetch health records and get personalized analysis.")

user_id = st.text_input("Enter User ID to Fetch Health Data:")
if st.button("Fetch Health Data"):
    health_data = fetch_health_data(user_id)

    if isinstance(health_data, dict):  # ✅ Ensure response is a dictionary
        st.session_state.user_health_data = health_data
        st.success("✅ User Health Data Retrieved!")

        # Display structured health data
        st.subheader("📋 User Health Details")
        st.write(f"**👤 Name:** {health_data.get('name', 'N/A')}")
        st.write(f"**🆔 User ID:** {health_data.get('id', 'N/A')}")
        st.write(f"**⚕️ Current Health Condition:** {health_data.get('current_health', 'N/A')}")
        st.write(f"**📜 Past Health History:** {health_data.get('past_health', 'N/A')}")

    else:
        st.error(f"⚠ Error fetching user data: {health_data}") 

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    st.write("🔍 Extracting text from image...")
    extracted_text = extract_text_tesseract(image)
    st.session_state.extracted_text = extracted_text
    st.text_area("Extracted Text", extracted_text, height=150)

    if st.button("Analyze with AI"):
        if st.session_state.user_health_data:
            st.write("🤖 AI is analyzing your health data and nutrition info...")
            analysis = analyze_text_with_groq(extracted_text, st.session_state.user_health_data)
            st.success("✅ AI Analysis Complete!")
        else:
            st.error("⚠ Please fetch user health data first.")

    # Display AI Response
    if st.session_state.ai_response:
        st.text_area("AI Response", st.session_state.ai_response, height=200)

        # Translation Button
        if st.button("Translate to Hindi"):
            translated_analysis = translate_text_to_hindi(st.session_state.ai_response)

    # Display Translated Response
    if st.session_state.translated_response:
        st.text_area("AI Response in Hindi", st.session_state.translated_response, height=200)

# Chatbot Section
st.subheader("💬 Chat with AI")
user_question = st.text_input("Ask a question about your health and nutrition:")

if st.button("Ask AI"):
    if user_question and st.session_state.user_health_data:
        question_with_context = f"""
        User's Health Data:
        - Name: {st.session_state.user_health_data['name']}
        - Current Health: {st.session_state.user_health_data['current_health']}
        - Past Health: {st.session_state.user_health_data['past_health']}
        
        User's Question: {user_question}
        """
        response = analyze_text_with_groq(question_with_context, st.session_state.user_health_data)
        st.session_state.ai_response = response
    else:
        st.error("⚠ Please enter a question and ensure user health data is loaded.")

    # Display Chatbot Response
    if st.session_state.ai_response:
        st.text_area("AI Response", st.session_state.ai_response, height=150)

        # Translation button for chat response
        if st.button("Translate Chat Response to Hindi"):
            translated_chat_response = translate_text_to_hindi(st.session_state.ai_response)

    # Display Translated Chat Response
    if st.session_state.translated_response:
        st.text_area("AI Chat Response in Hindi", st.session_state.translated_response, height=150)
