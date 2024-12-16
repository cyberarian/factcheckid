import streamlit as st
import webbrowser

def run():
    st.title("GitHub Repository 💻")
    st.write("Visit our GitHub repository to contribute or report issues.")
    
    # Replace with your actual GitHub URL
    github_url = "https://github.com/cyberarian/factcheckid"
    
    if st.button("Open GitHub Repository"):
        st.markdown(f'<a href="{github_url}" target="_blank">Visit GitHub Repository</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    run()