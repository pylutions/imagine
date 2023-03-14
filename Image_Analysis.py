import streamlit as st
import requests
from PIL import Image
from sklearn.cluster import KMeans


def hide_header():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


def show_sidebar():
    with st.sidebar:
        #st.image('icon.ico')
        st.header("Welcome to the Image Analysis tool!")
        st.write("Upload an image or provide a link to analyze an image.")
        st.write('')
        st.write("Your data (inputs and outputs) will not be saved and is yours only.")

def process_file(image_file):
    try:
        img = Image.open(image_file)
        process_image(img)
    except Exception as e:
        st.write(e)

def process_url(image_url):
    try:
        img = Image.open(requests.get(image_url, stream=True).raw)
        process_image(img)

    except Exception as e:
        st.write(e)


def extract_colors(img):
    colors = img.getcolors(img.size[0] * img.size[1])
    rgb_colors = [[color[1][i] for i in range(3)] for color in colors]
    kmeans = KMeans(n_clusters=5, random_state=0).fit(rgb_colors)
    colors = kmeans.cluster_centers_
    return  colors



def process_image(img):
    try:
        st.write('---')
        st.image(img)
        colors = extract_colors(img)
        col1, col2, col3 = st.columns(3)
        col1.header('Color')
        col2.header('RGB')
        col3.header('Hex')
        for color in colors:
            R = int(color[0].round())
            G = int(color[1].round())
            B = int(color[2].round())
            hex = '#%02x%02x%02x' % (R, G, B)
            col1, col2, col3 = st.columns(3)
            col1.markdown(
                f'<div style="background-color: rgba({R}, {G}, {B},1); width:100%; height:50px;"></div>',
                unsafe_allow_html=True)
            col2.write(f'{R}, {G}, {B}')
            col3.write(hex)
        col1, col2, col3 = st.columns(3)
        col1.header('Change color')
        col2.header('RGB')
        col3.header('Hex')
        for color in colors:
            R = int(color[0].round())
            G = int(color[1].round())
            B = int(color[2].round())
            hex = '#%02x%02x%02x' % (R, G, B)
            col1, col2, col3 = st.columns(3)
            col1.color_picker(label='cp', value=hex, label_visibility='collapsed')
            col2.write(f'{R}, {G}, {B}')
            col3.write(hex)
    except Exception as e:
        st.write(e)

if __name__ == "__main__":
    st.set_page_config(page_title="Image Analysis", page_icon="icon.ico", layout="wide")
    hide_header()
    show_sidebar()

    st.title("Image Analysis")

    col1, col2 = st.columns(2)
    with col1:
        image_file = st.file_uploader('Upload an image', type=['png', 'jpg'], key='uploader')


    with col2:
        image_url = st.text_input('Enter image URL', key='input')


    if image_file is not None:
        process_file(image_file)

    if image_url:
        process_url(image_url)


