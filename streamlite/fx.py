import streamlit as st
import pytesseract
import easyocr
from PIL import Image
import numpy as np
from transformers import pipeline
import requests

# Set page config
st.set_page_config(
    page_title="Health Analysis App",
    page_icon="🏥",
    layout="wide"
)

# Cache resources for better performance
@st.cache_resource
def load_easyocr():
    return easyocr.Reader(['en'])

@st.cache_resource
def load_nlp_pipeline():
    return pipeline("summarization", model="facebook/bart-large-cnn")

# Sidebar navigation
def sidebar():
    st.sidebar.title("Navigation")
    return st.sidebar.radio(
        "Go to",
        ["Food Label Analysis", "Prescription Analysis", "Diet Planning"]
    )

# Extract text using EasyOCR
def extract_text(image):
    reader = load_easyocr()
    results = reader.readtext(np.array(image))
    return "\n".join([result[1] for result in results])

# Food Label Analysis
def food_label_analysis():
    st.header("Food Label Analysis 🏷️")
    uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Label", use_column_width=True)
        with st.spinner("Extracting text..."):
            text = extract_text(image)
            st.text_area("Extracted Text:", text, height=200)

# Prescription Analysis
def prescription_analysis():
    st.header("Prescription Analysis 📝")
    uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Prescription", use_column_width=True)
        with st.spinner("Analyzing prescription..."):
            text = extract_text(image)
            summarizer = load_nlp_pipeline()
            summary = summarizer(text, max_length=130, min_length=30)[0]['summary_text'] if len(text) > 100 else text
            st.subheader("Simplified Interpretation")
            st.write(summary)
            st.text_area("Extracted Text:", text, height=200)

# Calculate BMI
def calculate_bmi(weight, height):
    return round(weight / ((height / 100) ** 2), 2)

# Fetch food nutrition data using the API key
def get_food_nutrition(food_query):
    api_key = "ha6WbCNn0HkQonQpJHHh6CWRLRLSpdUgXg84trte"
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_query}&api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        foods = response.json().get("foods", [])
        if foods:
            # Return the first result instead of a random one
            return foods[0]
    return None

# Diet Planning
def diet_planning():
    st.header("Diet Planning 🥗")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 1, 120, 25)
        weight = st.number_input("Weight (kg)", 1.0, 300.0, 70.0)
        height = st.number_input("Height (cm)", 1.0, 300.0, 170.0)
        bmi = calculate_bmi(weight, height)
        st.subheader("Your Health Analysis")
        st.write(f"**BMI:** {bmi}")
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity_level = st.select_slider("Activity Level", ["Sedentary", "Light", "Moderate", "Active", "Very Active"])
        diseases = ["None", "Diabetes", "Hypertension", "Heart Disease", "Obesity", "Asthma", "Anemia", "Cancer", "Chronic Kidney Disease", "Stroke", "COVID-19", "Influenza", "Tuberculosis", "Dengue", "HIV/AIDS", "Malaria", "Hepatitis", "Pneumonia", "Arthritis", "Liver Disease", "Epilepsy", "Depression", "Thyroid Disorder"]
        health_condition = st.multiselect("Health Conditions", diseases)
    if st.button("Generate Diet Plan"):
        with st.spinner("Generating your personalized diet plan..."):
            # Calculate Basal Metabolic Rate (BMR) based on gender, age, weight, and height
            if gender == "Male":
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            elif gender == "Female":
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            else:
                bmr = 500 + (10 * weight) + (6.25 * height) - (5 * age)  # Default calculation for "Other"

            # Adjust BMR based on activity level
            activity_multipliers = {
                "Sedentary": 1.2,
                "Light": 1.375,
                "Moderate": 1.55,
                "Active": 1.725,
                "Very Active": 1.9
            }
            daily_calories = bmr * activity_multipliers.get(activity_level, 1.2)

            # Determine the food query based on health conditions
            if "Diabetes" in health_condition:
                food_query = "low glycemic index foods"
            elif "Hypertension" in health_condition:
                food_query = "potassium-rich foods"
            elif "Obesity" in health_condition:
                food_query = "low calorie high protein foods"
            elif "Heart Disease" in health_condition:
                food_query = "heart-healthy foods"
            elif "Asthma" in health_condition:
                food_query = "anti-inflammatory foods"
            elif "Anemia" in health_condition:
                food_query = "iron-rich foods"
            elif "Cancer" in health_condition:
                food_query = "antioxidant-rich foods"
            elif "Chronic Kidney Disease" in health_condition:
                food_query = "low sodium low potassium foods"
            elif "Stroke" in health_condition:
                food_query = "low sodium high fiber foods"
            elif "COVID-19" in health_condition or "Influenza" in health_condition:
                food_query = "immune-boosting foods"
            elif "Tuberculosis" in health_condition:
                food_query = "high calorie high protein foods"
            elif "Dengue" in health_condition:
                food_query = "hydration-rich foods"
            elif "HIV/AIDS" in health_condition:
                food_query = "high calorie high protein foods"
            elif "Malaria" in health_condition:
                food_query = "hydration-rich foods"
            elif "Hepatitis" in health_condition:
                food_query = "liver-friendly foods"
            elif "Pneumonia" in health_condition:
                food_query = "immune-boosting foods"
            elif "Arthritis" in health_condition:
                food_query = "anti-inflammatory foods"
            elif "Liver Disease" in health_condition:
                food_query = "liver-friendly foods"
            elif "Epilepsy" in health_condition:
                food_query = "ketogenic diet foods"
            elif "Depression" in health_condition:
                food_query = "mood-boosting foods"
            elif "Thyroid Disorder" in health_condition:
                food_query = "iodine-rich foods"
            else:
                food_query = "balanced diet"

            # Fetch food nutrition data using the API key
            nutrition_data = get_food_nutrition(food_query)
            if nutrition_data:
                st.write(f"**Food Recommendation:** {nutrition_data.get('description', 'N/A')}")
                nutrients = {n["nutrientName"].lower(): n for n in nutrition_data.get("foodNutrients", [])}
                st.markdown("**Nutritional Breakdown:**")
                st.write(f"- **Calories:** {nutrients.get('energy', {}).get('value', 'N/A')} kcal")
                st.write(f"- **Protein:** {nutrients.get('protein', {}).get('value', 'N/A')} g")
                st.write(f"- **Carbohydrates:** {nutrients.get('carbohydrate, by difference', {}).get('value', 'N/A')} g")
                st.write(f"- **Fat:** {nutrients.get('total lipid (fat)', {}).get('value', 'N/A')} g")
                
                # Provide personalized calorie intake recommendation
                st.subheader("Daily Calorie Intake Recommendation")
                st.write(f"Based on your age, weight, height, gender, and activity level, your estimated daily calorie intake is **{daily_calories:.0f} kcal**.")
            else:
                st.write("No nutritional data available.")

# Main app
def main():
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    page = sidebar()
    if page == "Food Label Analysis":
        food_label_analysis()
    elif page == "Prescription Analysis":
        prescription_analysis()
    else:
        diet_planning()

if __name__ == "__main__":
    main()