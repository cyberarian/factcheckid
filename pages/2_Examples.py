import streamlit as st

def run():
    st.title("Sample Use Cases 📝")
    st.write("""
      
    Here are some example texts you can try:
    """)

    example_1 = st.expander("Example 1: Historical Facts")
    with example_1:
        st.code("""
        Jakarta, ibu kota Indonesia, memiliki sejarah yang kaya akan masa lalu sejak tahun 1531 ketika didirikan sebagai Jayakarta. Pada masa kolonial Belanda, kota ini dikenal dengan nama Batavia. Nama "Jakarta" pertama kali digunakan pada masa pendudukan Jepang tahun 1942 untuk menyebut wilayah bekas Gemeente Batavia yang diresmikan pemerintah Hindia Belanda pada tahun 1925. Nama "Jakarta" adalah bentuk pendek dari "Jayakarta", yang berasal dari kata-kata Sanskerta "jaya" (kemenangan) dan "krta" (kemakmuran). Oleh karena itu, Jayakarta berarti "kota kemenangan dan kemakmuran". Nama itu diberikan oleh Raja Hayam Wuruk setelah menyerang dan berhasil menduduki pelabuhan Sunda Kelapa pada tanggal 22 Agustus 1531 dari Portugis. Penetapan hari jadi Jakarta tanggal 22 Agustus oleh Sudiro, wali kota Jakarta, pada tahun 1956 adalah berdasarkan peristiwa tersebut.
        """)
        
    example_2 = st.expander("Example 2: Current Events")
    with example_2:
        st.code("""
        On December 5, 2024, the Southern Operations Room, a Syrian opposition group, launched an attack from the east, advancing towards Damascus and pushing the Syrian Arab Army out of several areas on the outskirts. Meanwhile, other opposition forces, including Tahrir al-Sham and the Turkish-backed Syrian National Force, launched offensives in Homs and the capital from the north and southeast, respectively. By December 6, rebel forces had entered the Barzeh neighborhood of Damascus. In response, President Bashar al-Assad reportedly fled Damascus by air and sought asylum in Moscow, effectively marking the end of his regime.
        """)

if __name__ == "__main__":
    run()