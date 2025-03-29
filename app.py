import streamlit as st
from modules.file_parser import extract_text
from modules.content_splitter import propose_article_splits
from modules.article_writer import generate_long_article
from modules.wordpress_exporter import publish_to_wordpress

st.set_page_config(page_title="Redaktor GoldBot", layout="wide")

st.title("🧠 Redaktor GoldBot – generator artykułów do WordPressa (Knawall)")
st.markdown("Stwórz profesjonalne artykuły z dokumentów źródłowych i wyślij je prosto do WordPressa jako wpisy bazy wiedzy.")

uploaded_file = st.file_uploader("Wgraj plik źródłowy (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])

if uploaded_file:
    with st.spinner("📄 Odczytywanie treści..."):
        with open("temp_input", "wb") as f:
            f.write(uploaded_file.read())
        raw_text = extract_text("temp_input")

    st.text_area("📃 Podgląd treści", raw_text[:3000], height=300)

    if st.button("🔍 Zaproponuj podział na artykuły"):
        with st.spinner("🧩 Analiza treści..."):
            propozycje = propose_article_splits(raw_text)
        st.markdown("### ✍️ Propozycje artykułów:")
        st.markdown(propozycje)
        st.session_state["propozycje"] = propozycje

if "propozycje" in st.session_state:
    st.markdown("---")
    st.header("🧩 Wybierz temat do opracowania")
    tytul = st.text_input("Tytuł artykułu (SEO)")
    zakres = st.text_area("Zakres treści", height=150)
    czesci = st.slider("Ile części ma mieć artykuł?", 1, 5, 1)

    if st.button("🛠️ Wygeneruj artykuł"):
        with st.spinner("✏️ Generowanie treści..."):
            wygenerowany = generate_long_article(tytul, zakres, max_parts=czesci)
        st.session_state["wygenerowany"] = wygenerowany
        st.success("✅ Artykuł wygenerowany!")

if "wygenerowany" in st.session_state:
    st.markdown("---")
    st.header("📤 Podgląd artykułu i eksport do WordPressa")
    st.markdown(st.session_state["wygenerowany"], unsafe_allow_html=True)

    slug = st.text_input("Slug (adres URL wpisu)", value=tytul.lower().replace(" ", "-"))
    status = st.selectbox("Status wpisu", ["draft", "publish"])
    tags_input = st.text_input("ID tagów WordPress (oddzielone przecinkami)", value="")
    cats_input = st.text_input("ID kategorii WordPress (oddzielone przecinkami)", value="")

    if st.button("🚀 Opublikuj do WordPressa"):
        with st.spinner("📡 Wysyłanie do WordPressa..."):
            wynik = publish_to_wordpress(
                title=tytul,
                content_html=st.session_state["wygenerowany"],
                slug=slug,
                tags=[int(t.strip()) for t in tags_input.split(",") if t.strip().isdigit()],
                categories=[int(c.strip()) for c in cats_input.split(",") if c.strip().isdigit()],
                status=status
            )
        st.success(wynik)
