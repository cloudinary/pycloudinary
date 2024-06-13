from cloudinary.uploader import upload


CLOUD_NAME = 'YOUR NAME'
API_KEY = 'YOUR API KEY'
API_SECRET = 'YOUR API SECRET'

cloudinary.config(
    cloud_name = CLOUD_NAME,
    api_key = API_KEY,
    api_secret = API_SECRET
)

# Function to upload an image in your account
def upload_file():
    file_path = input("Enter the file path: ")
    file_name = input("Enter the file name: ")

    image = upload(file_path, file_name, unique_filename=False)

upload_file()
