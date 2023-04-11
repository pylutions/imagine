import streamlit as st
from PIL import Image, ImageEnhance


def hide_header():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

def show_sidebar():
    with st.sidebar:
        #st.image('icon.ico')
        st.header("Welcome to the Image Analysis tool!")
        # Create slider for factor
        st.session_state['factor'] = st.slider('Select a factor value', 1.0, 3.0, step=0.1)


if __name__ == "__main__":
    st.set_page_config(page_title="Image Analysis", page_icon="icon.ico", layout="wide")
    hide_header()
    show_sidebar()
    image = st.session_state['image']
    enhancer = ImageEnhance.Color(image)
    enhanced_image = enhancer.enhance(st.session_state['factor'])
    st.image(enhanced_image)
