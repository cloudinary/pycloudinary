Cloudinary
==========

Cloudinary is a cloud service that offers a solution to a web application's entire image management pipeline. 

Easily upload images to the cloud. Automatically perform smart image resizing, cropping and conversion without installing any complex software. Integrate Facebook or Twitter profile image extraction in a snap, in any dimension and style to match your website’s graphics requirements. Images are seamlessly delivered through a fast CDN, and much much more. 

Cloudinary offers comprehensive APIs and administration capabilities and is easy to integrate with any web application, existing or new.

Cloudinary provides URL and HTTP based APIs that can be easily integrated with any Web development framework. 

For Python, Cloudinary provides an egg for simplifying the integration even further.

## Setup ######################################################################

You can install Cloudinary's module using either `easy_install` or `pip` package management tools. For example:

        $ pip install cloudinary

## Try it right away

Sign up for a [free account](https://cloudinary.com/users/register/free) so you can try out image transformations and seamless image delivery through CDN.

*Note: Replace `demo` in all the following examples with your Cloudinary's `cloud name`.*  

Accessing an uploaded image with the `sample` public ID through a CDN:

    http://res.cloudinary.com/demo/image/upload/sample.jpg

![Sample](https://d3jpl91pxevbkh.cloudfront.net/demo/image/upload/w_0.4/sample.jpg "Sample")

Generating a 150x100 version of the `sample` image and downloading it through a CDN:

    http://res.cloudinary.com/demo/image/upload/w_150,h_100,c_fill/sample.jpg

![Sample 150x100](https://d3jpl91pxevbkh.cloudfront.net/demo/image/upload/w_150,h_100,c_fill/sample.jpg "Sample 150x100")

Converting to a 150x100 PNG with rounded corners of 20 pixels: 

    http://res.cloudinary.com/demo/image/upload/w_150,h_100,c_fill,r_20/sample.png

![Sample 150x150 Rounded PNG](https://d3jpl91pxevbkh.cloudfront.net/demo/image/upload/w_150,h_100,c_fill,r_20/sample.png "Sample 150x150 Rounded PNG")

For plenty more transformation options, see our [image transformations documentation](http://cloudinary.com/documentation/image_transformations).

Generating a 120x90 thumbnail based on automatic face detection of the Facebook profile picture of Bill Clinton:
 
    http://res.cloudinary.com/demo/image/facebook/c_thumb,g_face,h_90,w_120/billclinton.jpg
    
![Facebook 90x120](https://d3jpl91pxevbkh.cloudfront.net/demo/image/facebook/c_thumb,g_face,h_90,w_120/billclinton.jpg "Facebook 90x200")

For more details, see our documentation for embedding [Facebook](http://cloudinary.com/documentation/facebook_profile_pictures) and [Twitter](http://cloudinary.com/documentation/twitter_profile_pictures) profile pictures. 


## Usage

### Configuration

Each request for building a URL of a remote cloud resource must have the `cloud_name` parameter set. 
Each request to our secure APIs (e.g., image uploads, eager sprite generation) must have the `api_key` and `api_secret` parameters set. See [API, URLs and access identifiers](http://cloudinary.com/documentation/api_and_access_identifiers) for more details.

Setting the `cloud_name`, `api_key` and `api_secret` parameters can be done either directly in each call to a Cloudinary method, by calling the cloudinary.config(), by using environment variables, or using the CLOUDINARY django settings.

You can [download your customized cloudinary python configuration](https://cloudinary.com/console/cloudinary_python.txt) using our Management Console.


### Embedding and transforming images

Any image uploaded to Cloudinary can be transformed and embedded using powerful view helper methods:

The following example generates the url for accessing an uploaded `sample` image while transforming it to fill a 100x150 rectangle:

    cloudinary.utils.cloudinary_url("sample.jpg", width = 100, height = 150, crop = "fill")

Another example, emedding a smaller version of an uploaded image while generating a 90x90 face detection based thumbnail: 

    cloudinary.utils.cloudinary_url("woman.jpg", width = 90, height = 90, 
                 crop = "thumb", gravity = "face")

You can provide either a Facebook name or a numeric ID of a Facebook profile or a fan page.  
             
Embedding a Facebook profile to match your graphic design is very simple:

    cloudinary.utils.cloudinary_url("billclinton.jpg", width = 90, height = 130, type = "facebook",
                               crop => "fill", gravity => "north_west")
                           
Same goes for Twitter:

    cloudinary.utils.cloudinary_url("billclinton.jpg", type = "twitter_name")

### Upload

Assuming you have your Cloudinary configuration parameters defined (`cloud_name`, `api_key`, `api_secret`), uploading to Cloudinary is very simple.
    
The following example uploads a local JPG to the cloud: 
    
    cloudinary.uploader.upload("my_picture.jpg")
        
The uploaded image is assigned a randomly generated public ID. The image is immediately available for download through a CDN:

    cloudinary.utils.cloudinary_url("abcfrmo8zul1mafopawefg.jpg")
        
    http://res.cloudinary.com/demo/image/upload/abcfrmo8zul1mafopawefg.jpg

You can also specify your own public ID:    
    
    cloudinary.uploader.upload("http://www.example.com/image.jpg", public_id = 'sample_remote')

    cloudinary.utils.cloudinary_url("sample_remote.jpg")

    http://res.cloudinary.com/demo/image/upload/sample_remote.jpg
        
## Django 

### cloudinary.CloudinaryImage

Represents an image stored in Cloudinary.

Usage:
    img = cloudinary.CloudinaryImage("sample", format="png")
    
    img.url(width=100, height=100, crop="fill") 
    # http://res.cloudinary.com/cloud_name/image/upload/c_fill,h_100,w_100/sample.png 
    
    img.image(width=100, height=100, crop="fill") 
    # <img src="http://res.cloudinary.com/cloud_name/image/upload/c_fill,h_100,w_100/sample.png" width="100" height="100"/>

### cloudinary.models.CloudinaryField

Allows you to store references to Cloudinary stored images in your model. `CloudinaryField` inherits from `ImageFileField` so it should be a drop-in replacement if you already use an `ImageFileField`. (You'll still have to upload existing images to Cloudinary.)

Field instances have a `url_with_options` method which can be passed the same options as `cloudinary_url`.

Usage:

    class Poll(models.Model):
      # ...
      image = cloudinary.models.CloudinaryField()

### cloudinary.forms.CloudinaryField

Form field that allows you to validate and convert to CloudinaryImage a signed Cloudinary image reference (see [here](http://github.com/cloudinary/cloudinary_js))


### cloudinary.storage.CloudinaryStorage

If you want to store images in Cloudinary without using a `CloudinaryField`, you can use the storage backend for convenient image access.

### cloudinary template tags

Initialization:

    {% load cloudinary %}

Image tags can be generated from public_id or from CloudinaryImage object using:

    {% cloudinary image width=100, height=100, crop="fill" %}   
    # <img src="http://res.cloudinary.com/cloud_name/image/upload/c_fill,h_100,w_100/sample.png" width="100" height="100" crop="scale"/>

The following tag generates an html form that can be used to upload the file directly to Cloudinary. The result is a redirect to the supplied callback_url.

    {% cloudinary_direct_upload callback_url %}

Optional parameters:

    public_id - The name of the uploaded file in Cloudinary
  
## Additional resources ##########################################################

Additional resources are available at:

* [Website](http://cloudinary.com)
* [Documentation](http://cloudinary.com/documentation)
* [Image transformations documentation](http://cloudinary.com/documentation/image_transformations)
* [Upload API documentation](http://cloudinary.com/documentation/upload_images)

## Support

You can [open an issue through GitHub](https://github.com/cloudinary/cloudinary/issues).

Contact us at [info@cloudinary.com](mailto:info@cloudinary.com)

Or via Twitter: [@cloudinary](https://twitter.com/#!/cloudinary)

## License #######################################################################

Released under the MIT license. 
