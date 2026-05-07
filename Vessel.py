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

def gaussian_2D(center, sig, size_im):
    x, y = np.meshgrid(np.linspace(0, size_im[1], size_im[1]), np.linspace(0, size_im[0], size_im[0]))
    gauss = np.exp((-1*(x-center[0])**2)/((sig**2)/2) + (-1*(y-center[1])**2)/((sig**2)/2))
    return 1-gauss

def powder_trail_filter(img, tresh_high=0.9, tresh_low=0.1):#0.87 #0.25
    img = img/img.max()
    img_tops = (img>tresh_high)*255.0
    img_tops = img_tops.astype(np.uint8)
    img_hills = (img>tresh_low)*255.0
    img_hills = img_hills.astype(np.uint8)
    
    img_ = np.zeros(img.shape)
    ret, markers = cv2.connectedComponents(img_hills)
    for i in range(ret):
        if np.sum(img_tops[markers==i])>0:
            img_[markers==i]=1
    return img_

def func_f(x):
    if x<=0:
        return 0
    else:
        #print(np.exp(-1/x))
        return np.exp(-1/x)

def func_g(x):
	return func_f(x)/(func_f(x)+func_f(1-x))

def trans_func(x, a, b):
	return func_g((x-a)/(b-a))

def flt32_to_unint8(img):
   #print(img.min(),img.max())
    return np.round((((img - img.min())/(img.max()-img.min()) * 255)).astype(np.uint8)) #img.astype(numpy.uint8)#

def cut_im_2(image_in, mask_in, size_im, device = 'cpu'):

    global x_im 
    global y_im
    global bordure

    bordure = 100
        
	cnt, _ = cv2.findContours((mask_in).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contour = max(cnt, key = cv2.contourArea)

	(x,y), radius = cv2.minEnclosingCircle(contour)
	center = (int(x), int(y))
	radius = int(radius)

	g = gaussian_2D(center, radius, mask_in.shape)

	g = ((mask_in*g)/255.0).astype(np.float32)

	im = np.array(im, dtype=np.float32)/255.0

	im = np.concatenate((im, g[:,:,None]), axis=2)

    transform = transforms.Compose([transforms.ToTensor()])
    new_imagette_list=[]

    x_im,y_im,*_  = im.shape 
    i, j = 0,0

    while i + size_im[0] < x_im :
        while j + size_im[1] < y_im:
            new_imagette_list.append(transform(im[i :i+size_im[0], j: j+size_im[1]]).to(device)
)
            j+= size_im[1]-bordure

        new_imagette_list.append(transform(im[i :i+size_im[0], y_im-size_im[1]:y_im]).to(device)
)
        i += size_im[0]-bordure
        j = 0

    while j + size_im[1] < y_im:
        new_imagette_list.append(transform(im[x_im -size_im[0] :x_im, j: j+size_im[1]]).to(device)
)
        j+= size_im[1]-bordure

    new_imagette_list.append(transform(im[x_im -size_im[0] :x_im, y_im-size_im[1]:y_im]).to(device)
)

    return new_imagette_list


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
			key = selected_image_key + "_cornea"
			
			if key in st.session_state.segmentations:
				st.write('Cornea Segmentation Done')
				st.image(st.session_state.segmentations[selected_image_key + "_cornea"], caption="Cornea")
				st.session_state.segmentations[selected_image_key + "_mask"] = st.image(st.session_state.segmentations[selected_image_key + "_cornea"]
	
			else : 
				st.write('Please run cornea segmentation before')


	input = st.st.session_state.images[selected_image_key]
	mask_in = st.session_state.segmentations[selected_image_key + "_mask"]
