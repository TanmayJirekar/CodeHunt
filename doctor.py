import streamlit as st
from doctr.models import ocr_predictor
import numpy as np
from PIL import Image
from groq import Groq

# Set Groq API Key (Replace this with your actual key)
GROQ_API_KEY = ""
client = Groq(api_key=GROQ_API_KEY)

# Initialize Doctr OCR Model
ocr_model = ocr_predictor(pretrained=True)

# Streamlit UI
st.title("📄 Doctor Prescription Analysis")
st.write("Upload a **JPG or PNG** prescription image to extract medication details.")

# File Upload (Images Only)
uploaded_file = st.file_uploader("Upload Prescription Image", type=["jpg", "png"])

if uploaded_file:
    try:
        # Convert uploaded file to a PIL Image
        image = Image.open(uploaded_file).convert("RGB")

        # Convert PIL image to NumPy array
        image_np = np.array(image)

        # Use Doctr to extract text
        doc = ocr_model([image_np])

        # Extract text properly
        extracted_text = "\n".join(
            [word.value for block in doc.pages[0].blocks for line in block.lines for word in line.words]
        ) if doc.pages else "⚠ No text detected."

        # Display Extracted Text
        st.subheader("📜 Extracted Prescription Text")
        st.text_area("Extracted Text", extracted_text, height=200)

        # Analyze with AI
        if st.button("🔍 Analyze Prescription"):
            st.write("🤖 AI is analyzing your prescription...")

            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": extracted_text}],
                    model="mixtral-8x7b-32768",
                    stream=False,
                )
                ai_response = chat_completion.choices[0].message.content if chat_completion.choices else "⚠ AI could not generate a response."
            except Exception as e:
                ai_response = f"⚠ Error: {str(e)}"

            st.subheader("📝 AI Analysis")
            st.text_area("AI Analysis", ai_response, height=200)

        # Translate to Hindi
        if st.button("🌍 Translate to Hindi"):
            translation_prompt = f"Translate the following prescription into Hindi:\n\n{extracted_text}"

            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": translation_prompt}],
                    model="mixtral-8x7b-32768",
                    stream=False,
                )
                translated_text = chat_completion.choices[0].message.content if chat_completion.choices else "⚠ Translation failed."
            except Exception as e:
                translated_text = f"⚠ Error: {str(e)}"

            st.subheader("🔠 Prescription in Hindi")
            st.text_area("Translated Text", translated_text, height=200)

    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")
