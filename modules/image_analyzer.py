import streamlit as st
from groq import Groq
import google.generativeai as genai
from PIL import Image
import base64
import io
import json
import os

def encode_image(image_file):
    """Convert uploaded image to base64 string"""
    img = Image.open(image_file)
    buffered = io.BytesIO()
    img.save(buffered, format=img.format)
    return base64.b64encode(buffered.getvalue()).decode()

def analyze_image_groq(image_file, model_name):
    """Analyze image using Groq's vision models"""
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Encode image to base64
        base64_image = encode_image(image_file)
        
        prompt = """Analyze this image and provide:
        1. A detailed description
        2. Key objects and elements identified
        3. Any text visible in the image
        4. Notable features or patterns
        5. Potential context or setting
        
        Format the response as JSON with these keys:
        - description
        - objects_identified
        - text_content
        - notable_features
        - context
        """
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.2
        )
        
        # Parse the response into JSON
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # If response is not valid JSON, return it as a description
            return {
                "description": response.choices[0].message.content,
                "objects_identified": [],
                "text_content": "",
                "notable_features": [],
                "context": ""
            }
        
    except Exception as e:
        st.error(f"Error analyzing image with Groq: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }

def analyze_image_gemini(image_file):
    """Analyze image using Google Gemini"""
    try:
        # Configure Gemini API
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Create model with generation config
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config,
        )
        
        # Open and convert image
        img = Image.open(image_file)
        
        # Detailed prompt to encourage JSON-like structured response
        prompt = """Analyze this image comprehensively. Your response MUST be a valid JSON object with these EXACT keys:
        {
            "description": "A detailed description of the entire image",
            "objects_identified": ["list", "of", "objects", "in", "the", "image"],
            "text_content": "Any text found in the image",
            "notable_features": ["list", "of", "unique", "or", "striking", "features"],
            "context": "Potential setting or broader context of the image"
        }
        
        Important: Provide a concise, accurate response that fits this exact JSON structure."""
        
        # Send message with image
        response = model.generate_content([prompt, img])
        
        # Try to parse or create a structured response
        try:
            # Direct parsing might fail, so we'll parse more carefully
            parsed_response = json.loads(response.text.split('```json')[-1].split('```')[0].strip())
            return parsed_response
        except Exception:
            # Fallback to creating a structured response
            return {
                "description": response.text,
                "objects_identified": [],
                "text_content": "",
                "notable_features": [],
                "context": ""
            }
    
    except Exception as e:
        st.error(f"Error analyzing image with Gemini: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }

def image_analyzer_main():
    """Main function for image analysis page"""
    
    # Model selection dropdown
    model_options = {
        "Groq Llama 3.2 11B Vision": "llama-3.2-11b-vision-preview",
        "Groq Llama 3.2 90B Vision": "llama-3.2-90b-vision-preview",
        "Google Gemini Flash": "gemini-2.0-flash-exp"
    }
    
    selected_model = st.selectbox(
        "Choose an AI Model", 
        list(model_options.keys())
    )
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload an image for analysis", 
        type=['png', 'jpg', 'jpeg']
    )
    
    if uploaded_file is not None:
        # Create columns for layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
        
        with col2:
            with st.spinner('Analyzing image...'):
                # Choose analysis method based on selected model
                if selected_model.startswith("Groq"):
                    analysis_result = analyze_image_groq(
                        uploaded_file, 
                        model_options[selected_model]
                    )
                else:  # Gemini
                    analysis_result = analyze_image_gemini(uploaded_file)
                
                if 'error' in analysis_result:
                    st.error("Analysis failed. Please try again.")
                else:
                    # Display analysis results in an organized manner
                    st.subheader("📝 Description")
                    st.write(analysis_result.get('description', 'No description available'))
                    
                    st.subheader("🎯 Objects Identified")
                    objects = analysis_result.get('objects_identified', [])
                    if objects:
                        for obj in objects:
                            st.write(f"• {obj}")
                    else:
                        st.write("No objects identified")
                    
                    if analysis_result.get('text_content'):
                        st.subheader("📜 Text Content")
                        st.write(analysis_result['text_content'])
                    
                    st.subheader("✨ Notable Features")
                    features = analysis_result.get('notable_features', [])
                    if features:
                        for feature in features:
                            st.write(f"• {feature}")
                    else:
                        st.write("No notable features identified")
                    
                    st.subheader("🌍 Context")
                    st.write(analysis_result.get('context', 'No context available'))

# Add this if you want to run the app directly
if __name__ == "__main__":
    st.title("Multi-Model Image Analyzer")
    image_analyzer_main()