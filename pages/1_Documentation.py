import streamlit as st

def run():
    st.title("How to Use FactChecker_ID 📚")
    st.write("""
    FactChecker_ID: Empowering Fact-Checking Across Eight Languages.
    
    ### Features
    1. Multilingual Support: Verify text in eight languages, including Indonesian, English, Arabic, French, Spanish, Chinese, Japanese, and Russian.
    2. Automatic Claim Extraction: Our algorithm automatically extracts claims from the input text, making it easy to identify and verify specific statements.
    3. Real-Time Fact Verification: Get instant results and verify facts in real-time, ensuring that your information is up-to-date and accurate.
    4. Credibility Scoring: Our credibility scoring system provides a clear indication of the reliability and trustworthiness of the verified information.
    5. Typos Correction: Our tool also corrects typos and grammatical errors, ensuring that your text is accurate and error-free.
       
    ### Usage Guide
    1. Select Your Preferred Language: Choose from eight languages, including Indonesian, English, Arabic, French, Spanish, Chinese, Japanese, and Russian.
    2. Enter or Paste Your Text: Input the text you'd like to verify, or paste it from another source.
    3. Click "Check Facts": Our algorithm will quickly process your text and provide highlighted results.
    4. Review the Highlighted Results: Our tool will highlight the verified information, allowing you to easily review and understand the credibility of the claims.
    
    """)

if __name__ == "__main__":
    run()