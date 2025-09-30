import streamlit as st
import pytesseract
import cv2
import numpy as np
from PIL import Image
from gtts import gTTS
import base64
import tempfile

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\mahar\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

st.set_page_config(page_title="HEARABLE", layout="centered")
st.title("HEARABLE 👂🏻")

language_option = st.selectbox(
    "Select Language:",
    options=["English", "Hindi", "Marathi"]
)

tesseract_language = {
    "English": "eng",
    "Hindi": "hin",
    "Marathi": "mar"
}

gtts_language = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr"
}

capture_button = st.camera_input("Capture Image")

def convert_image_to_text(image_np, tess_lang_code):
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pil_img = Image.fromarray(thresh)
    text = pytesseract.image_to_string(pil_img, lang=tess_lang_code, config="--psm 6")
    return text.strip()

def text_to_speech(text, tts_lang_code):
    try:
        tts = gTTS(text=text, lang=tts_lang_code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            tts.save(temp_audio.name)
            return temp_audio.name
    except Exception as e:
        st.error(f"Error during text-to-speech: {e}")
        return None


def play_audio(file_path):
    with open(file_path, "rb") as f:
        audio_data = f.read()
        b64 = base64.b64encode(audio_data).decode()
        audio_html = f"""
        <audio autoplay controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

if capture_button:
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Unable to access the camera.")
        else:
            ret, frame = cap.read()
            cap.release()

            if ret:
                st.image(frame, caption="Captured Image", channels="BGR", use_container_width=True)

                with st.spinner("Performing OCR..."):
                    tess_lang = tesseract_language[language_option]
                    extracted_text = convert_image_to_text(frame, tess_lang)

                if extracted_text:
                    st.subheader("Extracted Text:")
                    st.success(extracted_text)

                    with st.spinner(f"Converting to {language_option} speech..."):
                        tts_lang = gtts_language[language_option]
                        audio_path = text_to_speech(extracted_text, tts_lang)
                        if audio_path:
                            play_audio(audio_path)
                else:
                    st.warning("No text detected. Try again with a clearer image.")
            else:
                st.error("Failed to capture image from webcam.")
    except Exception as e:
        st.error(f"Camera capture failed: {e}")
