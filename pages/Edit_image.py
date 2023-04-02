import streamlit as st


def hide_header():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

def show_sidebar():
    with st.sidebar:
        #st.image('icon.ico')
        st.header("Welcome to the Image Analysis tool!")


if __name__ == "__main__":
    st.set_page_config(page_title="Image Analysis", page_icon="icon.ico", layout="wide")
    hide_header()
    show_sidebar()
