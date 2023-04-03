import streamlit as st
import numpy as np
import requests
import base64
from io import BytesIO
from PIL import Image
from PIL.ExifTags import TAGS
from sklearn.cluster import KMeans
from streamlit_image_coordinates import streamlit_image_coordinates


def hide_header():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


def show_sidebar():
    with st.sidebar:
        st.header("Welcome to the Image Analysis tool!")
        st.write("Upload an image or provide a link to analyze an image.")
        st.write('')
        st.write("Your data (inputs and outputs) will not be saved.")



def process_file(image_file):
    try:
        img = Image.open(image_file)
        process_image(img)
    except Exception as e:
        st.write(e)


@st.cache_resource
def request_image(image_url):
    if image_url.startswith('data:image/jpeg;base64'):
        url = image_url.split(',')[1]
        image_data = base64.b64decode(url)
        img = Image.open(BytesIO(image_data))
    else:
        img = Image.open(requests.get(image_url, stream=True).raw)
    return img


def process_url(image_url):
    try:
        img = request_image(image_url)
        process_image(img)

    except Exception as e:
        st.write(e)


def get_clusters(colors):
    kmeans = KMeans(n_clusters=5, random_state=0).fit(colors)
    clusters = kmeans.cluster_centers_
    st.session_state['clusters'] = np.rint(clusters).astype(np.int32)
    #return colors



def extract_colors(img):
    colors = img.getcolors(img.size[0] * img.size[1])
    rgb_colors = [[color[1][i] for i in range(3)] for color in colors]
    st.session_state['rgb_colors'] = rgb_colors
    #return rgb_colors



def get_metadata(image):
    st.session_state['meta'] = {
        "Filename": image.filename,
        "Image Size": image.size,
        "Image Height": image.height,
        "Image Width": image.width,
        "Image Format": image.format,
        "Image Mode": image.mode,
        "Image is Animated": getattr(image, "is_animated", False),
        "Frames in Image": getattr(image, "n_frames", 1)
    }
    exifdata = image.getexif()
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes
        if isinstance(data, bytes):
            data = data.decode()
        st.session_state['meta'][tag] = data


def add_picked_color(selected_color):
    st.session_state['picked_colors'].append(selected_color)


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))


def display_colors(colors):
    rerun = False
    ret_colors = []
    for color in colors:
        R, G, B = color
        hex_color = '#%02x%02x%02x' % (R, G, B)
        cp, div, rgb, hxc = st.columns(4)
        new_color = cp.color_picker(label='cp', value=hex_color, label_visibility='collapsed')
        if new_color != hex_color:
            rerun = True
            color = np.array(hex_to_rgb(new_color))
        div.markdown(
                f'<div style="background-color: rgba({R}, {G}, {B},1); width:100%; height:50px;"></div>',
                unsafe_allow_html=True)
        rgb.write(f'{R}, {G}, {B}')
        hxc.code(hex_color, language=None)
        ret_colors.append(color)
    return ret_colors, rerun


def process_image(img):
    st.session_state['image'] = img

    if 'previous_image' in st.session_state:
        if st.session_state['image'] != st.session_state['previous_image']:
            del st.session_state['rgb_colors']
            del st.session_state['clusters']

    st.session_state['previous_image'] = st.session_state['image']
    try:
        st.write('---')
        get_metadata(img)
        with st.expander('Meta data'):
            st.write(st.session_state['meta'])

        st.session_state['last_coordinates'] = streamlit_image_coordinates(img)

        if 'rgb_colors' not in st.session_state:
            extract_colors(img)
        colors = st.session_state.rgb_colors
        if st.session_state['last_coordinates']:
            if not st.session_state['last_coordinates'] == st.session_state['last_added']:
                st.session_state['last_added'] = st.session_state['last_coordinates']
                add_picked_color(img.getpixel((st.session_state['last_coordinates']['x'], st.session_state['last_coordinates']['y'])))

        if st.session_state['picked_colors']:
            st.header('Picked colors')
            st.session_state['picked_colors'], rerun = display_colors(st.session_state['picked_colors'])
            if rerun:
                st.experimental_rerun()
        if 'clusters' not in st.session_state:
            get_clusters(colors)

        st.header('Dominant colors')
        st.session_state['clusters'], rerun = display_colors(st.session_state['clusters'])

        st.session_state['image_loaded'] = True

        if rerun:
            st.experimental_rerun()

    except Exception as e:
        st.write(e)


def get_query():
    st.session_state.query_params = st.experimental_get_query_params()
    if 'url' in st.session_state.query_params:
        # /?url=
        st.session_state['image_url'] = st.session_state.query_params['url'][0]
        return True
    else:
        return False


if __name__ == "__main__":
    st.set_page_config(page_title="Image Analysis", page_icon="icon.ico", layout="wide")
    hide_header()
    show_sidebar()
    if 'picked_colors' not in st.session_state:
        st.session_state['picked_colors'] = []
        st.session_state['last_added'] = ''
        st.session_state['image_loaded'] = False


    st.title("Image Analysis")

    if not get_query() and not st.session_state['image_loaded']:
        col1, col2 = st.columns(2)
        with col1:
            st.session_state['image_file'] = st.file_uploader('Upload an image', type=['png', 'jpg'], key='uploader')

        with col2:
            st.session_state['image_url'] = st.text_input('Enter image URL', key='input')


    if 'image_file' in st.session_state:
        if st.session_state['image_file']:
            process_file(st.session_state['image_file'])


    if 'image_url' in st.session_state:
        if st.session_state['image_url']:
            process_url(st.session_state['image_url'])


