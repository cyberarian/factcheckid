import streamlit as st
import wikipedia
from groq import Groq
import json
from typing import List, Dict
import re
from html import escape

# Initialize Groq client with API key from environment or Streamlit secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Groq API key not found. Please set GROQ_API_KEY in Streamlit secrets.")
    st.stop()

# Default language to Indonesian
wikipedia.set_lang("id")

def switch_wikipedia_language(language: str = "id"):
    """
    Switch Wikipedia language and return current language setting.
    
    Args:
        language (str, optional): Language code to switch to. Defaults to "id".
    
    Returns:
        str: Current language code
    """
    try:
        # Validate language input
        valid_languages = ["id", "en"]  # Add more languages if needed
        if language.lower() not in valid_languages:
            st.warning(f"Invalid language. Defaulting to Indonesian. Choose from {valid_languages}")
            language = "id"
        
        # Explicitly set Wikipedia language
        wikipedia.languages['current'] = language.lower()
        wikipedia.set_lang(language.lower())
        
        # Update session state to track current language
        st.session_state.current_wiki_language = language.lower()
        
        return language.lower()
    except Exception as e:
        st.error(f"Error switching Wikipedia language: {e}")
        return "id"

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
        return re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)[:5]

def find_best_wikipedia_page(keywords: List[str]) -> Dict:
    """Find the most relevant Wikipedia page based on keywords, respecting current language."""
    # Ensure we're using the current session language
    current_language = st.session_state.get('current_wiki_language', 'id')
    
    # Temporarily switch Wikipedia language
    wikipedia.set_lang(current_language)

    for keyword in keywords:
        try:
            try:
                # Use the current language when searching
                page = wikipedia.page(keyword, auto_suggest=False)
                return {
                    'title': page.title,
                    'content': page.content[:5000],
                    'url': page.url,
                    'summary': page.summary
                }
            except wikipedia.exceptions.DisambiguationError as e:
                if e.options:
                    try:
                        # Try the first disambiguation option
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
                continue
        except Exception as e:
            st.warning(f"Could not find Wikipedia page for '{keyword}' in {current_language}: {e}")
    
    return None

def extract_claims(text: str) -> Dict:
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
        
        claims_data = json.loads(response.choices[0].message.content)
        return claims_data
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

def highlight_text(text: str, claims_data: Dict) -> str:
    """Highlight text based on claim verification results."""
    highlighted_text = text
    
    colors = {
        'accurate': '#E8F5E9',    # Light green
        'inaccurate': '#FFEBEE',  # Light red
        'subjective': '#FFF3E0'   # Light orange
    }
    
    if claims_data and 'claims' in claims_data:
        # Sort claims by length (longest first) to avoid nested highlighting
        sorted_claims = sorted(claims_data['claims'], 
                             key=lambda x: len(x.get('claim', '')), 
                             reverse=True)
        
        for claim_info in sorted_claims:
            claim_text = claim_info.get('claim', '')
            if claim_text:
                verification_status = claim_info.get('status', 'subjective')
                color = colors.get(verification_status, colors['subjective'])
                
                # Escape HTML special characters
                escaped_claim = escape(claim_text)
                highlighted_html = f'<span style="background-color: {color};">{escaped_claim}</span>'
                
                # Replace the claim text with highlighted version
                highlighted_text = highlighted_text.replace(claim_text, highlighted_html)
    
    return highlighted_text

def main():
    # Streamlit UI Configuration
    st.set_page_config(page_title="Fact Checker ID", page_icon="📋", layout="wide")

    # Initialize current language in session state if not already set
    if 'current_wiki_language' not in st.session_state:
        st.session_state.current_wiki_language = "id"

    st.title("FactChecker_ID 🕵️‍♀️")

    # Add language switch buttons
    col_lang_switch = st.columns(2)
    with col_lang_switch[0]:
        # Indonesian Language Button
        if st.button("🇮🇩 Indonesian", 
                     type="secondary" if st.session_state.current_wiki_language != "id" else "primary"):
            switch_wikipedia_language("id")
            st.rerun()

    with col_lang_switch[1]:
        # English Language Button
        if st.button("🇬🇧 English", 
                     type="secondary" if st.session_state.current_wiki_language != "en" else "primary"):
            switch_wikipedia_language("en")
            st.rerun()

    st.write(f"Current Wikipedia Language: {st.session_state.current_wiki_language.upper()}")

    # Create two columns for input and results
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Text")
        # Store the input text in session state to persist it
        if 'input_text' not in st.session_state:
            st.session_state.input_text = ""
        
        # Update session state when input changes
        input_text = st.text_area(
            "",
            value=st.session_state.input_text,
            height=400,
            placeholder="Enter text to fact-check...",
            key="input_area"
        )
        st.session_state.input_text = input_text
        
        word_count = len(input_text.split())
        st.text(f"Word Count: {word_count}/40,000")

        fact_check_clicked = st.button(
            "🔍 Check Facts",
            key="fact_check_button",
            help="Click to verify the claims in the text",
            type="primary"
        )

        # After fact checking, show the highlighted text in the input column
        if fact_check_clicked and input_text:
            with st.spinner("Processing text..."):
                keywords = extract_keywords(input_text)
                wiki_content = find_best_wikipedia_page(keywords)
                claims_data = extract_claims(input_text)
                
                if claims_data and claims_data.get('claims', []):
                    # Process claims first
                    for claim_info in claims_data['claims']:
                        result = verify_claim(claim_info['claim'], wiki_content)
                        claim_info['status'] = result['status']
                    
                    # Show highlighted text below the input area
                    st.markdown("### Highlighted Text")
                    highlighted_text = highlight_text(input_text, claims_data)
                    st.markdown(
                        f'<div class="highlighted-text">{highlighted_text}</div>',
                        unsafe_allow_html=True
                    )

    with col2:
        st.subheader("Fact Check Results")
        
        if fact_check_clicked and input_text:
            if word_count > 40000:
                st.error("Text exceeds 40,000 word limit. Please shorten your text.")
                st.stop()

            with st.spinner("Analyzing claims..."):
                if not wiki_content:
                    st.warning("Could not find a relevant Wikipedia page.")
                    st.stop()

                if claims_data and claims_data.get('claims', []):
                    accurate_claims = 0
                    total_claims = len(claims_data['claims'])
                    
                    # Process and display each claim
                    for claim_info in claims_data['claims']:
                        result = verify_claim(claim_info['claim'], wiki_content)
                        
                        if result['status'] == 'accurate':
                            accurate_claims += 1
                        
                        status_class = f"status-{result['status']}"
                        
                        st.markdown(
                            f"""
                            <div class="claim-result" style="background-color: {
                                '#E8F5E9' if result['status'] == 'accurate' else
                                '#FFEBEE' if result['status'] == 'inaccurate' else
                                '#FFF3E0'
                            };">
                                <span class="{status_class}">{result['status'].upper()}</span>
                                <br><br>
                                <strong>Claim:</strong> {claim_info['claim']}
                                <br><br>
                                <strong>Justification:</strong> {result['justification']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        if result.get('relevant_wiki_quote'):
                            st.markdown(
                                f'<div class="wiki-quote">{result["relevant_wiki_quote"]}</div>',
                                unsafe_allow_html=True
                            )
                        
                        if result.get('source_url'):
                            st.write("**Source:**", f"[Wikipedia]({result['source_url']})")
                    
                    # Display credibility score
                    credibility_score = (accurate_claims / total_claims) * 100 if total_claims > 0 else 0
                    st.write("Text Credibility Score")
                    st.progress(credibility_score/100)
                    st.write(f"{credibility_score:.1f}%")
                    
                else:
                    st.warning("No verifiable claims found in the text.")
        elif fact_check_clicked and not input_text:
            st.warning("Please enter some text to fact-check.")
        else:
            st.info("Enter text and click 'Check Facts' to start fact-checking.")

        # Display reference information in sidebar
        if fact_check_clicked and input_text and wiki_content:
            st.sidebar.write("**Extracted Keywords:**")
            st.sidebar.write(keywords)
            st.sidebar.write("**Primary Reference:**")
            st.sidebar.write(f"Title: {wiki_content['title']}")
            st.sidebar.write(f"URL: {wiki_content['url']}")

    # Footer
    st.markdown("---")
    st.markdown("Built with :orange_heart: thanks to Claude.ai, Groq, Github, Streamlit. :scroll: support my works at https://saweria.co/adnuri", help="cyberariani@gmail.com")

if __name__ == "__main__":
    main()