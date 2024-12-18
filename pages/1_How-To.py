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
    
    ### Sample Use Cases
    Here are some example texts you can try:
    """)
    
    # Example 1: Historical Facts
    example_1 = st.expander("Example 1: Historical Facts - Jakarta's History (Indonesian)")
    with example_1:
        st.code("""
Jakarta, ibu kota Indonesia, memiliki sejarah yang kaya akan masa lalu sejak tahun 1531 ketika didirikan sebagai Jayakarta. Pada masa kolonial Belanda, kota ini dikenal dengan nama Batavia. 
Nama "Jakarta" pertama kali digunakan pada masa pendudukan Jepang tahun 1942 untuk menyebut wilayah bekas Gemeente Batavia yang diresmikan pemerintah Hindia Belanda pada tahun 1925. Nama "Jakarta" adalah bentuk pendek dari "Jayakarta", yang berasal dari kata-kata Sanskerta "jaya" (kemenangan) dan "krta" (kemakmuran). 
Oleh karena itu, Jayakarta berarti "kota kemenangan dan kemakmuran". Nama itu diberikan oleh Raja Hayam Wuruk setelah menyerang dan berhasil menduduki pelabuhan Sunda Kelapa pada tanggal 22 Agustus 1531 dari Portugis. Penetapan hari jadi Jakarta tanggal 22 Agustus oleh Sudiro, wali kota Jakarta, pada tahun 1956 adalah berdasarkan peristiwa tersebut.
        """)
    
    # Example 2: Current Events
    example_2 = st.expander("Example 2: Current Events - Hypothetical Syrian Conflict (English)")
    with example_2:
        st.code("""
In a sudden and unexpected turn of events, Hayʼat Tahrir al-Sham (HTS)[a], more commonly known as Tahrir al-Sham took control of the capital city of Damascus without facing any resistance on December 4, 2024, marking a significant shift in the country's 23-year civil war. As a result, President Bashar al-Assid was forced to flee to Russia, bringing an end to his family's six-decade-long autocratic rule. 
This development has significant implications for the Middle East, as it removes a key stronghold of Iranian and Russian influence in the region. In response, Russia has granted asylum to President Assad and his family. 
Top rebel commander Abu Mohammed al-Golani greets the crowd at Ummayad Mosque in Damascus, after Syrian rebels announced that they had ousted President Bashar al-Assad on December 8, 2024.
        """)

    # Example 3: Profile
    example_3 = st.expander("Example 3: Profile - Хабиб Нурмагомедов (Russian)")
    with example_3:
        st.code("""
Хабиб Нурмагомедов - российский боец смешанных единоборств, выступавший в UFC. В прошлом он был чемпионом в легком весе и считается одним из величайших бойцов в мире. Он неоднократно становился чемпионом в различных видах единоборств, включая европейские титулы по армейскому рукопашному бою и панкратиону, а также титул чемпиона мира по грэпплингу.
Нурмагомедов имеет впечатляющий послужной список из 59 побед и 0 поражений, что делает его одним из самых успешных бойцов в истории UFC. В 2020 году он был признан лучшим спортсменом года в России, а в 2022 году был введен в Зал славы UFC.
Интересно, что Нурмагомедов имеет двойное гражданство - российский и катарский паспорта.
Переведено с помощью DeepL.com (бесплатная версия)
        """)

if __name__ == "__main__":
    run()