import streamlit as st
import wikipedia
from groq import Groq
import json
from typing import List, Dict
import re

# Initialize Groq client with API key from environment or Streamlit secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Groq API key not found. Please set GROQ_API_KEY in Streamlit secrets.")
    st.stop()

# Set Wikipedia language to Indonesian
wikipedia.set_lang("id")

def extract_keywords(text: str) -> List[str]:
    """Extract key entities and potential Wikipedia search terms."""
    try:
        prompt = f"""Extract key entities and search terms from the following text:

Guidelines:
1. Focus on proper nouns, specific names, locations, organizations
2. Extract terms most likely to match Wikipedia page titles
3. Prioritize complete, precise terms
4. Avoid generic or common words
5. Consider context and significance

Text: {text}

Return JSON format:
{{
    "keywords": [
        "Exact search term 1",
        "Exact search term 2",
        ...
    ]
}}"""
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        keywords_data = json.loads(response.choices[0].message.content)
        return keywords_data.get('keywords', [])
    except Exception as e:
        st.error(f"Error extracting keywords: {e}")
        # Fallback to basic extraction
        return re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)[:5]

def find_best_wikipedia_page(keywords: List[str]) -> Dict:
    """Find the most relevant Wikipedia page based on keywords."""
    for keyword in keywords:
        try:
            # Try exact page match first
            try:
                page = wikipedia.page(keyword, auto_suggest=False)
                return {
                    'title': page.title,
                    'content': page.content[:5000],
                    'url': page.url,
                    'summary': page.summary
                }
            except wikipedia.exceptions.DisambiguationError as e:
                # If disambiguation, try the first option
                if e.options:
                    try:
                        page = wikipedia.page(e.options[0], auto_suggest=False)
                        return {
                            'title': page.title,
                            'content': page.content[:5000],
                            'url': page.url,
                            'summary': page.summary
                        }
                    except:
                        continue
            except wikipedia.exceptions.PageError:
                # Page not found, continue to next keyword
                continue
        except Exception as e:
            st.warning(f"Could not find Wikipedia page for '{keyword}': {e}")
    
    return None

def extract_claims(text: str) -> List[Dict]:
    """Extract factual claims from the input text."""
    try:
        prompt = f"""Extract specific, verifiable factual claims from the following text:

Rules:
1. Extract claims that are:
   - Objectively verifiable
   - Specific and precise
   - Not subjective opinions
   - Related to names, events, locations, or statistical facts

2. Format each claim with a clear topic and statement

Text: {text}

Return JSON in this format:
{{
    "claims": [
        {{
            "claim": "Exact verifiable statement",
            "topic": "Main subject of the claim"
        }}
    ]
}}"""
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error extracting claims: {e}")
        return {"claims": []}

def verify_claim(claim: str, wiki_content: Dict) -> Dict:
    """Verify a single claim against Wikipedia content."""
    if not wiki_content:
        return {
            "status": "error",
            "justification": "No Wikipedia reference found",
            "source": "N/A"
        }

    try:
        prompt = f"""Verify the following claim against the Wikipedia content:

Claim: "{claim}"

Wikipedia Article: {wiki_content['title']}
Wikipedia Summary: {wiki_content['summary']}
Wikipedia Content: {wiki_content['content']}

Determine if the claim is:
- Accurate: Fully supported by Wikipedia
- Inaccurate: Contradicted by Wikipedia
- Subjective: Cannot be definitively verified

Respond in JSON format:
{{
    "status": "accurate/inaccurate/subjective",
    "justification": "Detailed explanation with specific references",
    "relevant_wiki_quote": "Relevant quote from Wikipedia",
    "source_url": "{wiki_content['url']}"
}}"""

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Verification error: {e}")
        return {
            "status": "error",
            "justification": "Processing verification failed",
            "source_url": wiki_content['url']
        }

def main():
    # Streamlit UI Configuration
    st.set_page_config(page_title="Fact Checker ID", page_icon="📋", layout="wide")

    # Custom CSS
    st.markdown("""
    <style>
    .stTextArea textarea {
        background-color: white;
        color: black;
        font-size: 16px;
    }
    .status-accurate { color: green; font-weight: bold; }
    .status-inaccurate { color: red; font-weight: bold; }
    .status-subjective { color: orange; font-weight: bold; }
    .fact-check-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .fact-check-button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Indonesian Fact Checker 🕵️‍♀️")

    # Input and Analysis Columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Text")
        input_text = st.text_area("", height=400, placeholder="Enter text to fact-check...")
        word_count = len(input_text.split())
        st.text(f"Word Count: {word_count}/40,000")

        # Fact Check Button
        fact_check_clicked = st.button("🔍 Check Facts", key="fact_check_button", 
                                       help="Click to verify the claims in the text",
                                       type="primary")

    with col2:
        st.subheader("Fact Check Results")
        
        # Only process when the Fact Check button is clicked
        if fact_check_clicked and input_text:
            # Validate input length
            if word_count > 40000:
                st.error("Text exceeds 40,000 word limit. Please shorten your text.")
                st.stop()

            # Fact Checking Process
            with st.spinner("Analyzing text... This may take a moment"):
                # Extract keywords
                keywords = extract_keywords(input_text)
                st.sidebar.write("Extracted Keywords:", keywords)
                
                # Find best Wikipedia page
                wiki_content = find_best_wikipedia_page(keywords)
                
                if not wiki_content:
                    st.warning("Could not find a relevant Wikipedia page.")
                    st.stop()

                # Extract claims
                claims_data = extract_claims(input_text)
                
                if claims_data and claims_data.get('claims', []):
                    accurate_claims = 0
                    total_claims = len(claims_data['claims'])
                    
                    for claim_info in claims_data['claims']:
                        # Verify the claim against the found Wikipedia page
                        result = verify_claim(claim_info['claim'], wiki_content)
                        
                        # Update accuracy count
                        if result['status'] == 'accurate':
                            accurate_claims += 1
                        
                        # Display result
                        with st.expander(f"Claim: {claim_info['claim'][:100]}...", expanded=True):
                            # Status with color
                            status_class = f"status-{result['status']}"
                            st.markdown(
                                f"**Status:** <span class='{status_class}'>{result['status'].upper()}</span>", 
                                unsafe_allow_html=True
                            )
                            
                            # Justification
                            st.write("**Justification:**", result['justification'])
                            
                            # Wikipedia quote if available
                            if result.get('relevant_wiki_quote'):
                                st.write("**Wikipedia Reference:**")
                                st.markdown(f"> {result['relevant_wiki_quote']}")
                            
                            # Source link
                            if result.get('source_url'):
                                st.write("**Source:**", f"[Wikipedia]({result['source_url']})")
                    
                    # Calculate and display credibility score
                    credibility_score = (accurate_claims / total_claims) * 100 if total_claims > 0 else 0
                    st.write("Text Credibility Score")
                    st.progress(credibility_score/100)
                    st.write(f"{credibility_score:.1f}%")
                    
                    # Display the primary reference Wikipedia page
                    st.sidebar.write("**Primary Reference Page:**")
                    st.sidebar.write(f"Title: {wiki_content['title']}")
                    st.sidebar.write(f"URL: {wiki_content['url']}")
                
                else:
                    st.warning("No verifiable claims found in the text.")
        elif fact_check_clicked and not input_text:
            st.warning("Please enter some text to fact-check.")
        else:
            st.info("Enter text and click 'Check Facts' to start fact-checking.")
# Footer
    st.markdown("---")
    st.markdown("Built with :orange_heart: thanks to Claude.ai, Groq, Github, Streamlit. :scroll: support my works at https://saweria.co/adnuri", help="cyberariani@gmail.com")
if __name__ == "__main__":
    main()