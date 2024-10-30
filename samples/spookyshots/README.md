# Spooky Pet Image App

**Spooky Pet Image App** is a fun platform that transforms ordinary pet images into spooky, Halloween-themed creations. Whether you're looking to give your cat a spooky makeover or place any pet in a chilling Halloween setting, this app has everything you need for a spooky transformation!

## Example Image Generated
### Original
![alexander-london-mJaD10XeD7w-unsplash](https://github.com/user-attachments/assets/98afa889-364a-4337-98ff-347f2a3a94e2)

### Transformed
![user_uploaded_alexander-london-mJaD10XeD7w-unsplash-min](https://github.com/user-attachments/assets/e3e1dde3-4252-499b-80a5-4b67942b2751)


## Installation

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cloudinary/pycloudinary.git
   cd pycloudinary/samples/spookyshots
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Cloudinary credentials**:
   - Inside the root directory of the project, rename `.env.example` to `.env`.
   - Open the `.env` file and fill in your Cloudinary credentials:
     ```
     CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
     CLOUDINARY_API_KEY=your_cloudinary_api_key
     CLOUDINARY_API_SECRET=your_cloudinary_api_secret
     ```

4. **Run the app**:
   ```bash
   streamlit run main.py
   ```

5. **Open the app**:
   After running the command, the app should automatically open in your browser. If not, open the browser and go to:
   ```
   http://localhost:8501
   ```

Enjoy transforming your pets for Halloween!
