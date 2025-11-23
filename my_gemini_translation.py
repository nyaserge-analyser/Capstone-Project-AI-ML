# import necessary libs (libraries) into project
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import PyPDF2
import pandas as pd
import os
import tempfile
import io
import PyPDF2 # Or another PDF library like pdfplumber
#import gemini_translation

#  Our Streamlit App Configuration 
st.set_page_config(page_title="Simple Web Multilanguage Translation and Text-to-Speech Application by using Streamlit ", layout="wide")
st.title("Multilanguage Translation And Text-to-Speech Application by using GEMINI(API)")


# Step2: Configure the GEMINI API
import getpass
APIKEY = getpass.getpass()        # to get the apikey at runtime without showing to end user.(*******)
genai.configure(api_key=APIKEY)

# Step 3: Configure our LLM Model
model = genai.GenerativeModel("gemini-flash-latest")
print(genai.list_models())


# FUNCTION: Translate text using Gemini

def translate_text_gemini(text, target_language):
    try:
        prompt = f"Translate the following text into {target_language}, provide only the translated text \n\n {text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as err:
        return f"Error occurred: {err}"
    
# FUNCTION : convert text to speech
def text_to_speech(text, language_code):
    try:
        tts = gTTS(text = text, lang = language_code)
        temp_file = tempfile.NamedTemporaryFile(delete= False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as err:
        return f"Error occurred: {err}"
    
# File Reader and Uploader section 
# File Uploader
st.subheader("Files Reader and Extractor")
uploaded_file = st.file_uploader("Upload a text, PDF, CSV, or Excel file", type=["txt", "pdf", "csv", "xls", "xlsx"])

# File Processing and Text Extraction 
extracted_text = ""
if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    st.write(f"Processing file: {uploaded_file.name}")

    if file_extension == "txt":
        try:
            # Read as string directly
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            extracted_text = stringio.read()
            st.text_area("Extracted Text", extracted_text)
        except Exception as e:
            st.error(f"Error reading text file: {e}")

    elif file_extension == "csv":
        try:
            # Read directly into a pandas DataFrame
            dataframe = pd.read_csv(uploaded_file)
            st.dataframe(dataframe)
            # Convert DataFrame to a string for translation
            extracted_text = dataframe.to_string()
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

    elif file_extension == "xlsx":
        try:
            # Read directly into a pandas DataFrame
            dataframe = pd.read_excel(uploaded_file)
            st.dataframe(dataframe)
            # Convert DataFrame to a string for translation
            extracted_text = dataframe.to_string()
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")

    elif file_extension == "pdf":
        try:
            # Use PyPDF2 to read PDF
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                pdf_text += page.extract_text()
            extracted_text = pdf_text
            st.text_area("Extracted Text", extracted_text)
        except Exception as e:
            st.error(f"Error reading PDF file. Make sure the PDF is not image-based. {e}")



#  STREAMLIT APP UI

st.subheader("Multilanguage Translator and text-to-speech convertor")
text_input = st.text_area("Enter the text here")

# Language selection
languages = {
    "English": "en",
    "French": "fr",
    "Latin": "la",
    "German": "de",
    "Spanish": "es",
    "Italian": "it",
    "Japanees": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "sh-cn",
    "chinese": "zh",
    "Russian": "ru",
    "Arabic": "ar",
    "Hindi": "hi",
    "Tamil": "ta"
}

selected_languare = st.selectbox("Select the language", list(languages.keys()))

if st.button("Translate and Convert"): 

    if text_input.strip() == "":
        st.error("Please provide the text to translate")
    else:
        translated_text = translate_text_gemini(text_input, selected_languare)
        st.subheader("Translated Text:")
        st.write(translated_text)

        # Convert text to speech:
        audio_file = text_to_speech(translated_text, languages[selected_languare])
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            with open(audio_file, "rb") as file:
                st.download_button("Downloaded audio", data=file, file_name="translated_audio.mp3")
        else:
            st.error("Failed to generate audio")