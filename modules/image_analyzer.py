from groq import Groq
import streamlit as st
from PIL import Image
import base64
import io
import json

def encode_image(image_file):
    """Convert uploaded image to base64 string"""
    img = Image.open(image_file)
    buffered = io.BytesIO()
    img.save(buffered, format=img.format)
    return base64.b64encode(buffered.getvalue()).decode()

def analyze_image(image_file):
    """Analyze image using Groq's vision model"""
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
            model="llama-3.2-11b-vision-preview",
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
        st.error(f"Error analyzing image: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }

def image_analyzer_main():
    """Main function for image analysis page"""
    
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
                analysis_result = analyze_image(uploaded_file)
                
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