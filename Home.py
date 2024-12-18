import streamlit as st
import sys
from pathlib import Path

# Add modules directory to Python path
module_path = Path(__file__).parent / "modules"
sys.path.append(str(module_path))

from modules.fact_checker import fact_checker_main
from modules.image_analyzer import image_analyzer_main

# Must be the first Streamlit command
st.set_page_config(
    page_title="FactChecker_ID", 
    page_icon="📋", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.markdown("<h1 style='text-align: center;'>FactChecker_ID 🕵️‍♀️</h1>", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["📝 Text Fact Checker", "🖼️ Image Analysis"])
    
    with tab1:
        fact_checker_main()
        
    with tab2:
        image_analyzer_main()

    # Footer
    st.markdown("---")
    st.markdown(
        "Built with :orange_heart: thanks to Claude.ai, Groq, Github, Streamlit. "
        ":scroll: support my works at https://saweria.co/adnuri", 
        help="cyberariani@gmail.com"
    )

if __name__ == "__main__":
    main()