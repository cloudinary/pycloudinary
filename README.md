Cloudinary
==========

Cloudinary is a cloud service that offers a solution to a web application's entire image management pipeline. 

Easily upload images to the cloud. Automatically perform smart image resizing, cropping and conversion without installing any complex software. Integrate Facebook or Twitter profile image extraction in a snap, in any dimension and style to match your website’s graphics requirements. Images are seamlessly delivered through a fast CDN, and much much more. 

Cloudinary offers comprehensive APIs and administration capabilities and is easy to integrate with any web application, existing or new.

Cloudinary provides URL and HTTP based APIs that can be easily integrated with any Web development framework. 

For Python, Cloudinary provides an egg for simplifying the integration even further.

## Getting started guide
![](http://res.cloudinary.com/cloudinary/image/upload/see_more_bullet.png)  **Take a look at our [Getting started guide for Python & Django](http://cloudinary.com/documentation/django_integration#getting_started_guide)**.


## Setup ######################################################################

You can install Cloudinary's module using either `easy_install` or `pip` package management tools. For example:

        $ pip install cloudinary

## Try it right away

Sign up for a [free account](https://cloudinary.com/users/register/free) so you can try out image transformations and seamless image delivery through CDN.

*Note: Replace `demo` in all the following examples with your Cloudinary's `cloud name`.*  

Accessing an uploaded image with the `sample` public ID through a CDN:

    http://res.cloudinary.com/demo/image/upload/sample.jpg

![Sample](https://res.cloudinary.com/demo/image/upload/w_0.4/sample.jpg "Sample")

Generating a 150x100 version of the `sample` image and downloading it through a CDN:

    http://res.cloudinary.com/demo/image/upload/w_150,h_100,c_fill/sample.jpg

![Sample 150x100](https://res.cloudinary.com/demo/image/upload/w_150,h_100,c_fill/sample.jpg "Sample 150x100")

Converting to a 150x100 PNG with rounded corners of 20 pixels: 

    http://res.cloudinary.com/demo/image/upload/w_150,h_100,c_fill,r_20/sample.png

![Sample 150x150 Rounded PNG](https://res.cloudinary.com/demo/image/upload/w_150,h_100,c_fill,r_20/sample.png "Sample 150x150 Rounded PNG")

For plenty more transformation options, see our [image transformations documentation](http://cloudinary.com/documentation/image_transformations).

Generating a 120x90 thumbnail based on automatic face detection of the Facebook profile picture of Bill Clinton:
 
    http://res.cloudinary.com/demo/image/facebook/c_thumb,g_face,h_90,w_120/billclinton.jpg
    
![Facebook 90x120](https://res.cloudinary.com/demo/image/facebook/c_thumb,g_face,h_90,w_120/billclinton.jpg "Facebook 90x200")

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

![](http://res.cloudinary.com/cloudinary/image/upload/see_more_bullet.png) **See [our documentation](http://cloudinary.com/documentation/django_image_manipulation) for more information about displaying and transforming images in Python & Django**.                                         

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

![](http://res.cloudinary.com/cloudinary/image/upload/see_more_bullet.png) **See [our documentation](http://cloudinary.com/documentation/django_image_upload) for plenty more options of uploading to the cloud from your Python & Django code or directly from the browser**.


## Django 

### cloudinary.CloudinaryImage

Represents an image stored in Cloudinary.

Usage:
    img = cloudinary.CloudinaryImage("sample", format="png")
    
    img.build_url(width=100, height=100, crop="fill") 
    # http://res.cloudinary.com/cloud_name/image/upload/c_fill,h_100,w_100/sample.png 
 
    # Note: since v1.0.0 this method was change from 'url' to 'build_url' to avoid conflicts with the 'url' property.
    
    img.image(width=100, height=100, crop="fill") 
    # <img src="http://res.cloudinary.com/cloud_name/image/upload/c_fill,h_100,w_100/sample.png" width="100" height="100"/>

### Models
#### cloudinary.models.CloudinaryField

Allows you to store references to Cloudinary stored images in your model. Returns an CloudinaryImage object.

Usage:

    class Poll(models.Model):
      # ...
      image = cloudinary.models.CloudinaryField('image')

### Forms

The CloudinaryField model field has `default_form_class = cloudinary.forms.CloudinaryFileField`. You can create a simple ModelForm that will let you upload an image to through the backend to cloudinary.

    class PollForm(django.forms.ModelForm):
        Meta:
            class = Poll

#### cloudinary.forms.CloudinaryFileField - simple upload

Form field that renders to a simple file input html element and allows you to validate, upload to Cloudinary and convert to CloudinaryImage an uploaded image file

#### cloudinary.forms.CloudinaryJsFileField - direct ajax upload

This form field renders to a special input element that interacts with Cloudinary's jQuery plugin and jQuery-File-Upload.
It allows you to validate and convert to CloudinaryImage a signed Cloudinary image reference resulting from a successful image upload (see [here](http://github.com/cloudinary/cloudinary_js))


### cloudinary template tags

#### Initialization:

    {% load cloudinary %}

Including the required Javascript files:

    {% cloudinary_includes %}

Passing configuration parameters to Cloudinary's jQuery plugin - will create a script tag with configuration initialization: 

    {% cloudinary_js_config %}

#### Embedding images

Image tags can be generated from a public\_id or from a CloudinaryImage object using:

    {% cloudinary image width=100 height=100 crop="fill" %}   
    # <img src="http://res.cloudinary.com/cloud_name/image/upload/c_fill,h_100,w_100/sample.png" width="100" height="100" crop="scale"/>

#### Uploading images

The following tag generates an html form field that can be used to upload the file directly to Cloudinary via ajax
using the jQuery-File-Upload widget. It could be used simply without parameters, anywhere in the DOM:

    {% cloudinary_direct_upload_field request=request %}

Alternatively, if used within an HTML form, after successful upload, the jQuery plugin creates a hidden input field
that could be used to pass the uploaded image's metadata to the backend:

    <form action="{% url "direct_upload_complete" %}" enctype="multipart/form-data">
        {% csrf_token %}
        {% cloudinary_direct_upload_field field='fieldname' request=request %}
    </form>

In both cases, the request object is optional, but is needed for correctly handling older browsers which don't fully support CORS.

The following tag generates an html form that can be used to upload the file directly to Cloudinary. The result is a redirect to the supplied callback_url.

    {% cloudinary_direct_upload callback_url %}

Optional parameters:

    public_id - The name of the uploaded file in Cloudinary

## Code samples

### Basic Python sample

This sample is a synchronous script that shows the upload process from local file, remote URL, with different transformations and options.

The source code and more details are available here:

[https://github.com/cloudinary/pycloudinary/tree/master/samples/basic](https://github.com/cloudinary/pycloudinary/tree/master/samples/basic)


### Photo Album - Django Web application 

A simple web application that allows you to uploads photos, maintain a database with references to them, list them with their metadata, and display them using various cloud-based transformations.

The source code and more details are available here:

[https://github.com/cloudinary/cloudinary-django-sample](https://github.com/cloudinary/cloudinary-django-sample)

  
## Additional resources

Additional resources are available at:

* [Website](http://cloudinary.com)
* [Documentation](http://cloudinary.com/documentation)
* [Knowledge Base](http://support.cloudinary.com/forums) 
* [Documentation for Django integration](http://cloudinary.com/documentation/django_integration)
* [Django image upload documentation](http://cloudinary.com/documentation/django_image_upload)
* [Django image manipulation documentation](http://cloudinary.com/documentation/django_image_manipulation)
* [Image transformations documentation](http://cloudinary.com/documentation/image_transformations)

## Support

You can [open an issue through GitHub](https://github.com/cloudinary/pycloudinary/issues).

Contact us [http://cloudinary.com/contact](http://cloudinary.com/contact)

Stay tuned for updates, tips and tutorials: [Blog](http://cloudinary.com/blog), [Twitter](https://twitter.com/cloudinary), [Facebook](http://www.facebook.com/Cloudinary).

## License #######################################################################

Released under the MIT license. 

Contains MIT licensed code from [poster](https://bitbucket.org/chrisatlee/poster).

