import streamlit as st

from PIL import Image

def run():
    st.title("Vessel Segmentation")

    if "segmentations" not in st.session_state:
        st.session_state.segmentations = {}

    selected_image_key = st.session_state.get("image_select")
    st.write(selected_image_key)
    
    st.write('Do you want to use the cornea segmentation or do you have already a mask ')

    selected_option = st.radio(
    "Select an option:",
    ["Segmentation", "Mask"],
    horizontal=True )

    st.write(f"Selected: {selected_option}")

    if selected_option == 'Mask':
        uploaded_Mask = st.file_uploader("Upload images", accept_multiple_files=False, type=["jpg", "jpeg", "png","tiff"])
        if uploaded_Mask:
            st.write(f"Filename: {uploaded_Mask.name}")
            img = Image.open(uploaded_Mask[0])
            st.session_state.segmentations[selected_image_key + "_mask"] = img
        
    if selected_image_key:
        
        if selected_image_key:
            key = selected_image_key + "_cornea"
            
            if key in st.session_state.segmentations:
                st.write('Cornea Segmentation Done')

            else : 
                st.write('Missing Cornea Selection')
