import streamlit as st
from groq import Groq
import base64
import json

# Initialize Groq client (similar to your existing code)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Groq API key not found. Please set GROQ_API_KEY in Streamlit secrets.")
    st.stop()

def analyze_image_with_vision(image_file):
    # Image analysis implementation here
    base64_image = base64.b64encode(image_file.getvalue()).decode('utf-8')
    
    # Your Groq API call for vision analysis
    try:
        response = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image for journalistic verification"},
                        {"type": "image", "image": base64_image}
                    ]
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Image analysis failed: {e}")
        return None

def run():
    st.title("Image Verification")
    
    uploaded_file = st.file_uploader(
        "Upload Image for Verification", 
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Max 10MB, support journalistic image verification"
    )
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image")
        
        if st.button("Verify Image"):
            with st.spinner("Analyzing image..."):
                analysis_result = analyze_image_with_vision(uploaded_file)
                
                if analysis_result:
                    # Display analysis results
                    st.json(analysis_result)

if __name__ == "__main__":
    run()