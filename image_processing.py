import os
from google.cloud import vision
from google.oauth2 import service_account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Google Cloud Vision client
CREDENTIALS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

try:
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)
except Exception as e:
    raise Exception(f"Error initializing Google Cloud Vision client: {e}")

def extract_text_from_image(image_bytes):
    """Extracts text from an uploaded image using Google Cloud Vision API."""
    try:
        image = vision.Image(content=image_bytes)
        response = vision_client.text_detection(image=image)

        if response.error.message:
            raise Exception(f"Google Cloud Vision API Error: {response.error.message}")

        texts = response.text_annotations
        return texts[0].description if texts else "No text detected in the image."
    
    except Exception as e:
        return f"Error processing image: {e}"