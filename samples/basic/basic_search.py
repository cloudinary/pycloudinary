import cloudinary



CLOUD_NAME = 'YOUR NAME'
API_KEY = 'YOUR API KEY'
API_SECRET = 'YOUR API SECRET'

cloudinary.config(
    cloud_name = CLOUD_NAME,
    api_key = API_KEY,
    api_secret = API_SECRET
)


# Function to search for an image in your account
def search():
    file_name = input("Enter file name: ")

    image = cloudinary.search().expression(public_id).execute() # IMAGE IS A JSON OBJECT. 


search()
