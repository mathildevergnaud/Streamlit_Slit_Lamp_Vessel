import streamlit as st

from PIL import Image

def load_model(device):
    net = build_model().to(device)
    net.load_state_dict(torch.load("./utils/cornea/model.pt", map_location=device))
    net.eval()
    return net

def build_model():
    return DynUNet(
        spatial_dims=2,
        in_channels=3,
        out_channels=1,
        kernel_size=[(3, 3)] * 5,
        strides=[(1, 1), (2, 2), (2, 2), (2, 2), (2, 2)],
        upsample_kernel_size=[(2, 2)] * 4,
        norm_name="BATCH",
        dropout=0.2)



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
            img = Image.open(uploaded_Mask)
            st.session_state.segmentations[selected_image_key + "_mask"] = img
            
            st.image(st.session_state.segmentations[selected_image_key + "_mask"], caption="Mask")


    else :
        
        if selected_image_key:
            
            if selected_image_key:
                key = selected_image_key + "_cornea"
                
                if key in st.session_state.segmentations:
                    st.write('Cornea Segmentation Done')
                    st.image(st.session_state.segmentations[selected_image_key + "_cornea"], caption="Cornea")

                
    
                else : 
                    st.write('Please run cornea segmentation before')
