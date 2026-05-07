import streamlit as st

def run():
    st.title("Vessel Segmentation")

    if "segmentations" not in st.session_state:
        st.session_state.segmentations = {}

    selected_image_key = st.session_state.get("image_select")
    st.write(selected_image_key)
        
    if selected_image_key:

        if st.session_state.segmentations[selected_image_key + "_cornea"] :
            st.write('Cornea Segmentation Done')


        else : 
            st.write('Missing Cornea Selection')
