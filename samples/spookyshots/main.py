import streamlit as st
from streamlit_option_menu import option_menu
import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os
import time

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Spooky Pet Background Generator", "Spooky Cat Face Transformer"],
        icons=["house", "image", "skull"],
        menu_icon="cast",
        default_index=0,
    )

if selected == "Home":
    st.title("Welcome to the Spooky Pet Image App! ~Powered by Cloudinary")
    
    st.write(""" 
    **Spooky Pet Image App** is a fun and creative platform that transforms ordinary pet images into spooky, Halloween-themed masterpieces. 
    Whether you're looking to give your cat a spooky makeover or place your pet in a chilling Halloween setting, this app has you covered!

    ### Features:
    - **Spooky Pet Background Generator**: Upload an image of any pet, and the app will replace the background with a dark, foggy Halloween scene featuring eerie trees, glowing pumpkins, a haunted house, and more.
    - **Spooky Cat Face Transformer**: Specifically designed for cats, this feature transforms your cat into a demonic version with glowing red eyes, sharp fangs, bat wings, and dark mist under a blood moon. You can also modify the transformation prompt for a more personalized spooky effect.
    
    This app leverages Cloudinary's powerful Generative AI features to make your pets look extra spooky this Halloween. Try it out, and share the spooky transformations with your friends!
    """)

if selected == "Spooky Pet Background Generator":
    st.title("Spooky Halloween Pet Image Transformer")

    upload_option = st.radio("Select image source:", ("Upload a file", "Enter an image URL"))

    if upload_option == "Upload a file":
        uploaded_file = st.file_uploader("Upload an image (jpg, jpeg, png)", type=["jpg", "jpeg", "png"])
    else:
        image_url = st.text_input("Enter the direct URL of the image (jpg, jpeg, png)")

    default_prompt = "A dark foggy Halloween night with a full moon in the sky surrounded by twisted trees Scattered glowing pumpkins with carved faces placed around an old broken fence in the background a shadowy haunted house with dimly lit windows"

    modify_prompt = st.checkbox("Do you want to modify the generative Halloween background prompt?", value=False)

    custom_prompt = st.text_input(
        "Optional: Modify the generative Halloween background prompt",
        value=default_prompt,
        disabled=not modify_prompt
    )

    if st.button("Submit"):
        if upload_option == "Upload a file" and uploaded_file:
            if uploaded_file.size > MAX_FILE_SIZE_BYTES:
                st.warning(f"File size exceeds the 5 MB limit. Please upload a smaller file.")
            else:
                with st.spinner("Generating image... Please have patience while the image is being processed by Cloudinary."):
                    upload_result = cloudinary.uploader.upload(
                        uploaded_file, 
                        public_id=f"user_uploaded_{uploaded_file.name[:6]}", 
                        unique_filename=True, 
                        overwrite=False
                    )
                    public_id = upload_result['public_id']
                    halloween_bg_image_url = CloudinaryImage(public_id).image(
                        effect=f"gen_background_replace:prompt_{custom_prompt}"
                    )

                    start_index = halloween_bg_image_url.find('src="') + len('src="')
                    end_index = halloween_bg_image_url.find('"', start_index)
                    generated_image_url = halloween_bg_image_url[start_index:end_index] if start_index != -1 and end_index != -1 else None

                    if generated_image_url:
                        st.image(generated_image_url)
                    else:
                        st.write("Failed to apply the background. Please try again.")
        
        elif upload_option == "Enter an image URL" and image_url:
            with st.spinner("Generating image... Please have patience while the image is being processed by Cloudinary."):
                unique_id = f"user_uploaded_url_{int(time.time())}"
                upload_result = cloudinary.uploader.upload(
                    image_url,
                    public_id=unique_id,
                    unique_filename=True,
                    overwrite=False
                )
                public_id = upload_result['public_id']
                halloween_bg_image_url = CloudinaryImage(public_id).image(
                    effect=f"gen_background_replace:prompt_{custom_prompt}"
                )

                start_index = halloween_bg_image_url.find('src="') + len('src="')
                end_index = halloween_bg_image_url.find('"', start_index)
                generated_image_url = halloween_bg_image_url[start_index:end_index] if start_index != -1 and end_index != -1 else None

                if generated_image_url:
                    st.image(generated_image_url)
                else:
                    st.write("Failed to apply the background. Please try again.")
        else:
            st.write("Please upload an image or provide a URL to proceed.")
            
if selected == "Spooky Cat Face Transformer":
    st.title("Spooky Cat Face Transformer")

    upload_option = st.radio("Select image source:", ("Upload a file", "Enter an image URL"))

    if upload_option == "Upload a file":
        uploaded_cat_pic = st.file_uploader("Upload a cat image to give it a spooky transformation! (jpg, jpeg, png)", type=["jpg", "jpeg", "png"])
    else:
        cat_image_url = st.text_input("Enter the direct URL of the cat image (jpg, jpeg, png)")

    default_cat_prompt = "A demonic cat with glowing red eyes sharp fangs and dark mist swirling around it under a blood moon"

    modify_cat_prompt = st.checkbox("Do you want to modify the spooky cat transformation prompt?", value=False)

    custom_cat_prompt = st.text_input(
        "Optional: Modify the spooky cat transformation prompt",
        value=default_cat_prompt,
        disabled=not modify_cat_prompt
    )

    if st.button("Transform to Spooky"):
        if upload_option == "Upload a file" and uploaded_cat_pic:
            if uploaded_cat_pic.size > MAX_FILE_SIZE_BYTES:
                st.warning(f"File size exceeds the 5 MB limit. Please upload a smaller file.")
            else:
                with st.spinner("Generating your cat's spooky transformation... Please wait while Cloudinary processes the image."):
                    upload_result = cloudinary.uploader.upload(
                        uploaded_cat_pic, 
                        public_id=f"user_spooky_cat_{uploaded_cat_pic.name[:6]}", 
                        unique_filename=True, 
                        overwrite=False
                    )
                    public_id = upload_result['public_id']
                    spooky_image_url = CloudinaryImage(public_id).image(
                        effect=f"gen_replace:from_cat;to_{custom_cat_prompt}"
                    )

                    start_index = spooky_image_url.find('src="') + len('src="')
                    end_index = spooky_image_url.find('"', start_index)
                    generated_image_url = spooky_image_url[start_index:end_index] if start_index != -1 and end_index != -1 else None

                    if generated_image_url:
                        st.image(generated_image_url)
                    else:
                        st.write("Failed to generate the spooky transformation. Please try again.")

        elif upload_option == "Enter an image URL" and cat_image_url:
            with st.spinner("Generating your cat's spooky transformation... Please wait while Cloudinary processes the image."):
                unique_id = f"user_uploaded_url_{int(time.time())}"
                upload_result = cloudinary.uploader.upload(
                    cat_image_url,
                    public_id=unique_id,
                    unique_filename=True,
                    overwrite=False
                )
                public_id = upload_result['public_id']
                spooky_image_url = CloudinaryImage(public_id).image(
                    effect=f"gen_replace:from_cat;to_{custom_cat_prompt}"
                )

                start_index = spooky_image_url.find('src="') + len('src="')
                end_index = spooky_image_url.find('"', start_index)
                generated_image_url = spooky_image_url[start_index:end_index] if start_index != -1 and end_index != -1 else None

                if generated_image_url:
                    st.image(generated_image_url)
                else:
                    st.write("Failed to generate the spooky transformation. Please try again.")
        else:
            st.write("Please upload an image or provide a URL to proceed.")
