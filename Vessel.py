import streamlit as st

def run():
    st.title("Cornea Segmentation")

    if "segmentations" not in st.session_state:
        st.session_state.segmentations = {}

    key = st.text_input("Image key")

    if key:
        seg_key = key + "_cornea"

        if seg_key in st.session_state.segmentations:
            st.image(st.session_state.segmentations[seg_key])
        else:
            st.info("No cornea result yet.")
