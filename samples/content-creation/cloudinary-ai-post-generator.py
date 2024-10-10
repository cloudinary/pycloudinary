#!/usr/bin/env python
import os
import sys

from cloudinary.api import delete_resources_by_tag, resources_by_tag
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Config
os.chdir(os.path.join(os.path.dirname(sys.argv[0]), '.'))
if os.path.exists('settings.py'):
    exec(open('settings.py').read())

DEFAULT_TAG = "python_sample_basic"


def dump_response(response):
    """Function to print and handle upload response"""
    print("Upload response:")
    for key in sorted(response.keys()):
        print("  %s: %s" % (key, response[key]))


def upload_file(file_path, public_id=None, mood=None, theme=None):
    """Upload a file to Cloudinary with options for custom public ID and transformations"""
    print(f"--- Uploading {file_path}")
    
    # Define transformations based on mood
    transformations = []
    
    if mood == "happy":
        transformations.append({"effect": "brightness:30"})  # Increase brightness
    elif mood == "sad":
        transformations.append({"effect": "grayscale"})  # Convert to grayscale

    # Add text overlay based on theme
    if theme:
        transformations.append({
            "overlay": {
                "font_family": "Arial",
                "font_size": 20,
                "text": f"{theme.capitalize()} - {mood.capitalize()}",
                "text_color": "white"
            },
            "gravity": "north",
            "y": 10
        })

    # Upload with transformations
    response = upload(
        file_path,
        public_id=public_id,
        transformation=transformations,
        tags=DEFAULT_TAG
    )

    dump_response(response)

    url, options = cloudinary_url(
        response['public_id'],
        format=response['format'],
        width=200,
        height=150,
        crop="fill"
    )
    print("Image URL: " + url)
    return url


@app.route('/generate_post', methods=['POST'])
def generate_post():
    """API endpoint to handle post generation and image upload"""
    try:
        # Get image file from request
        image = request.files.get('image')
        
        if not image:
            return jsonify({"error": "No image file provided"}), 400
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save image locally
        file_path = os.path.join(uploads_dir, image.filename)
        image.save(file_path)
        
        # Upload file to Cloudinary
        public_id = request.form.get('public_id', None)
        mood = request.form.get('mood', None)
        theme = request.form.get('theme', None)
        image_url = upload_file(file_path, public_id=public_id, mood=mood, theme=theme)
        
        # Clean up the local file after upload
        os.remove(file_path)
        
        # Return response
        return jsonify({"status": "success", "image_url": image_url})
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        return jsonify({"error": str(e)}), 500


def cleanup():
    """Cleanup resources by tag"""
    response = resources_by_tag(DEFAULT_TAG)
    resources = response.get('resources', [])
    if not resources:
        print("No images found")
        return
    print(f"Deleting {len(resources)} images...")
    delete_resources_by_tag(DEFAULT_TAG)
    print("Done!")


@app.route('/')
def index():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'upload':
            upload_file("sample.jpg")
        elif sys.argv[1] == 'cleanup':
            cleanup()
    else:
        print("--- Starting Flask server ---")
        app.run(debug=True)