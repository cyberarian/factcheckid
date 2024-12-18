import streamlit as st

def run():
    st.title("Disclaimer 📝")
    st.write("""

## Challenges and Problematic Aspects
      
While Wikipedia is a valuable resource for fact-checking, it is not without its challenges and problematic aspects. Here are a few key considerations:

##### Edit Wars and Vandalism: 
Wikipedia articles can be subject to edit wars and vandalism, which may temporarily distort the information presented. Fact-checkers must be aware of these potential issues and verify information from multiple reliable sources.

##### Incomplete or Missing Information: 
Wikipedia articles may not always have complete or up-to-date information on certain topics. Fact-checkers should use Wikipedia as one of many sources and cross-reference information to ensure accuracy.

##### Biased or Unbalanced Content: 
Some Wikipedia articles may contain biased or unbalanced content, reflecting the perspectives of the editors. Fact-checkers should approach Wikipedia content critically and consider multiple viewpoints when assessing information.

##### Reliability of Sources: 
While Wikipedia strives to cite reliable sources, the reliability of these sources can vary. Fact-checkers should evaluate the credibility of the sources cited in Wikipedia articles and seek additional verification when necessary.

##### Language-Specific Challenges: 
FactChecker_ID is designed to support multiple languages, including Indonesian and English, with Wikipedia serving as the primary source for fact-checking. However, a significant disparity exists between the number of articles available in each language. As of December 11, 2024, Wikipedia Indonesia has approximately 712,688 articles, while Wikipedia English has 6,922,449 articles. 

This disparity can lead to challenges in finding comprehensive information on certain topics, particularly for Indonesian-language fact-checking, where the limited number of articles may hinder the accuracy and reliability of fact-checking results.

By understanding these challenges and problematic aspects, users of FactChecker_ID can make more informed decisions when using Wikipedia as part of their fact-checking process.

We hope FactChecker_ID proves to be a valuable resource in your quest for verified information. Happy fact-checking!
        """)

if __name__ == "__main__":
    run()