import streamlit as st

def run():
    st.title("About FactChecker_ID 🎯")
    st.write("""
        
Welcome to FactChecker_ID, an open-source tool designed to help users verify information against reliable Wikipedia sources. My goal is to make fact-checking accessible to everyone, supporting multilingual functionality in eight languages, including Indonesian, English, Arabic, French, Spanish, Chinese, Japanese, and Russian.

Inspired by the work of https://parafactai.com/, a pioneering platform in this space, I aim to create a tool that is both accurate and accessible. However, I acknowledge that this app is far from perfection and satisfaction, and I'm committed to continually improving and refining it to meet the evolving needs of users.

Empowered by Meta-Llama-3.3-70b-versatile, I operate through Groq®, a state-of-the-art AI inference technology, delivering efficient processing and faster results.

### About Me

I'm Adnuri Mohamidi, a librarian graduate with a strong interest in data and AI technology, and the creator and maintainer of FactChecker_ID. With a background in the media industry as a Reference Librarian, I've developed a passion for using AI to make a positive impact and promoting fact-based discourse.

As a non-developer with a strong interest in AI, I've built FactChecker_ID using Claude Sonnet, a powerful tool for natural language processing. I believe that by working together, we can make a significant difference in promoting fact-based discourse and reducing the spread of misinformation.

If you're interested in joining this initiative, I invite you to contribute to the project by submitting a pull request or reaching out to me directly. Your expertise and ideas can help us improve and expand the capabilities of FactChecker_ID, making it an even more effective tool for promoting media literacy and combating misinformation.

Together, let's work towards a more informed and responsible online community, leveraging the power of Claude Sonnet and our collective expertise to make a positive impact!

### Open to Work

I'm open to full-time or part-time opportunities, both within and outside of this project. If you're interested in exploring potential collaborations or employment opportunities, please don't hesitate to reach out to me cyberariani@gmail.com.

With a diverse range of experiences across multiple sectors, I've had the privilege of working on projects in law, academia, and the automotive industry. Notably, I've served as a Reference Librarian in the media industry, where I provided research support and information literacy training to journalists and media professionals, honing my skills in information retrieval and dissemination.

As a librarian with a strong interest in data and AI technology, I have had the opportunity to explore and develop skills in various areas. With a solid foundation in online research and information literacy, I am well-versed in leveraging digital tools and resources to uncover insights and drive decision-making. My familiarity with AI concepts, particularly large language models (LLMs), has allowed me to stay up-to-date with the latest advancements in natural language processing and machine learning.

I have had the privilege of working on several AI-powered projects, including:

+ https://asksocrates.streamlit.app/:  an application that enables users to engage in discussions with an AI representation of Socrates, a ancient Greek philosopher famous for the Socratic Method. This application replicates his method, guiding users through philosophical questions while challenging their perspectives.
+ https://poetica.streamlit.app/: an application designed to emulate the style of legendary Indonesian poets such as Sapardi Djoko Damono, Chairil Anwar, Sutardji Calzoum Bachri, WS Rendra, and Widji Thukul. This application also provides features for analyzing poetry (aesthetics, semantic hermeneutics, and literary theory), allowing users to explore the beauty of poetry while encouraging new creative expressions.
+ https://pawangdata.streamlit.app/: a project aimed at helping users manage their data in a simple way.

Through these projects, I have gained valuable experience in leveraging AI to drive innovation and solve real-world problems, despite having a non-computer science background. Specifically, I have:

+ Developed a strong foundation in AI-powered application development using Streamlit and other technologies, allowing me to build and deploy applications that integrate AI-driven insights with user-friendly interfaces.
+ Designed and implemented machine learning models for natural language processing and data analysis, demonstrating my ability to apply AI concepts to practical problems and extract valuable insights from complex data sets.
+ Created user interfaces that effectively communicate complex data insights and AI-driven recommendations, showcasing my ability to translate technical information into actionable recommendations for non-technical stakeholders.

### Disclaimer: Challenges and Problematic Aspects

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