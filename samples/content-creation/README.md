# Social Media Content Creation API with Cloudinary

This project demonstrates a simple Flask API for social media content creation. The API allows users to upload images, apply transformations suitable for social media (like resizing, cropping, and adjusting image formats), and optionally set custom public IDs. Additionally, the API provides functionality to clean up old uploads by tag.

## Features

- Upload images for social media content creation.
- Apply transformations such as resizing, cropping, and format adjustment for optimal display on platforms like Instagram, Facebook, and Twitter.
- Option to assign custom public IDs for better image management.
- Cleanup of previously uploaded images by tag.

## Prerequisites

Before running this project, ensure you have:

1. [Python 3.x](https://www.python.org/downloads/)
2. A [Cloudinary account](https://cloudinary.com/users/register/free)
3. Cloudinary Python SDK installed via pip.

## Setup Instructions

### 1. Install Dependencies

After cloning or downloading this repository, install the required packages using `pip`:

```bash
pip install flask cloudinary
```

2. Configure Cloudinary

You need to configure the CLOUDINARY_URL environment variable with your Cloudinary credentials. You can find your credentials in the Cloudinary Management Console.
For Linux/MacOS (bash/zsh):
```bash
export CLOUDINARY_URL=cloudinary://<API-Key>:<API-Secret>@<Cloud-name>
```

For Windows (Command Prompt/PowerShell):
```bash
set CLOUDINARY_URL=cloudinary://<API-Key>:<API-Secret>@<Cloud-name>
```

3. Running the Flask App

Start the Flask server by running:

```bash
python app.py
```

The server will be available at http://127.0.0.1:5000/.


Usage
1. Uploading an Image for Social Media

To upload an image with transformations applied (suitable for social media), send a POST request to the /generate_post endpoint with the image file. You can optionally provide a public_id for the image.

    Endpoint: /generate_post
    Method: POST
    Parameters:
        image (required): The image file to upload.
        public_id (optional): Custom public ID for the image.

Image Transformations:

The API will automatically resize the image to a 1:1 aspect ratio (200x200px), perfect for profile pictures, thumbnails, or other social media purposes.
Example with cURL:

```bash
curl -X POST http://localhost:5000/generate_post \
     -F "image=@/path/to/your/social_media_image.jpg" \
     -F "public_id=my_custom_id"
```

Example Response:
```bash
{
  "status": "success",
  "image_url": "http://res.cloudinary.com/<cloud-name>/image/upload/v12345678/my_custom_id.jpg"
}
```
The image is transformed (resized to 200x200, cropped to fill), optimized for social media platforms.


2. Cleaning Up Uploaded Images

To delete all images uploaded with the default tag (set as python_sample_basic), you can run:

```bash
python app.py cleanup
```

This will delete all images tagged under DEFAULT_TAG.
Recommended Image Transformations for Social Media

    Profile Pictures/Thumbnails: Resize to 200x200px with a 1:1 aspect ratio.
    Banners: Crop to 1200x400px for optimal display on platforms like Twitter.
    Story Images: Resize to 1080x1920px (vertical aspect ratio) for Instagram or Snapchat stories.

Example Transformations in the Code:

    Resize and Crop: Automatically applied transformation in the API:

```bash
url, options = cloudinary_url(
    response['public_id'],
    format=response['format'],
    width=200,
    height=200,
    crop="fill"
)
```

This resizes the uploaded image to 200x200 pixels and crops it to fit.
Additional Functionality
Setting Custom Public IDs

You can assign custom public IDs for uploaded images, which is useful for managing content more effectively.
Dynamic Transformations

Feel free to modify the transformations in upload_file() to match specific platform requirements (e.g., square thumbnails, vertical or horizontal banners, etc.).
Environment Variables (Optional)

If you prefer, you can store the CLOUDINARY_URL in a .env file to make environment configuration easier:

```bash 
CLOUDINARY_URL=cloudinary://<API-Key>:<API-Secret>@<Cloud-name>
```
After creating the .env file, load it by running:
```bash
source .env
```
Conclusion

This project is designed to help you quickly set up an image uploading API tailored to social media content creation needs. It handles image transformations, easy uploads, and content management using Cloudinary.

Good luck and happy posting!