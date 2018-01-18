from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_wtf import Form
from wtforms import FileField, StringField, SubmitField, validators
from wtforms.validators import DataRequired, Length, URL
from flask_wtf.csrf import CSRFProtect
from keys import flask_secret_key

import requests
import mimetypes

app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
app.secret_key = flask_secret_key


VALID_IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    "bmp"
]
VALID_IMAGE_MIMETYPES = [
    "image"
]

class ImageUrl(Form):
    image_link = StringField('', [validators.URL('Invalid URL. Please provide a correct one')])
    image_link_submit = SubmitField('Submit')

# Validating the URL’s extension
def valid_url_extension(url, extension_list=VALID_IMAGE_EXTENSIONS):
    '''
    A simple method to make sure the URL the user has supplied has
    an image-like file at the tail of the path
    '''
    return any([url.endswith(e) for e in extension_list])

# Validating the URL mimetype
def valid_url_mimetype(url, mimetype_list=VALID_IMAGE_MIMETYPES):
    # http://stackoverflow.com/a/10543969/396300
    mimetype, encoding = mimetypes.guess_type(url)
    if mimetype:
        return any([mimetype.startswith(m) for m in mimetype_list])
    else:
        return False

# Validating that the image exists on the server
def image_exists(url):
    try:
        r = requests.get(url)
    except:
        return False
    return r.status_code == 200


@app.route('/index/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@csrf.exempt
def index():
    try:
        photourlform = ImageUrl()

        # POST-request
        if request.method == 'POST':
            print('Post')
            flash('Post', 'alert alert-warning alert-dismissible fade show')
            # If 'Submit' button under upload image/provide URL is clicked...
            if photourlform.image_link_submit.data:
                print('Submit button')
                flash('Submit button', 'alert alert-warning alert-dismissible fade show')
                if photourlform.validate():
                    print('WTForms validation: URL Ok')
                    flash('Url Ok', 'alert alert-warning alert-dismissible fade show')

                    url_submitted = photourlform.image_link.data
                    flash(url_submitted, 'alert alert-warning alert-dismissible fade show')
                    print(url_submitted)

                    # Validating the URL’s extension
                    flash('{} {}'.format('Extension: ', valid_url_extension(url_submitted)), 'alert alert-warning alert-dismissible fade show')
                    print('{} {}'.format('Extension: ', valid_url_extension(url_submitted)))

                    # Validating the URL mimetype
                    flash('{} {}'.format('Mimetype: ', valid_url_mimetype(url_submitted)), 'alert alert-warning alert-dismissible fade show')
                    print('{} {}'.format('Mimetype: ', valid_url_mimetype(url_submitted)))

                    # Validating that the image exists on the server
                    flash('{} {}'.format('Image exists on server: ', image_exists(url_submitted)), 'alert alert-warning alert-dismissible fade show')
                    print('{} {}'.format('Image exists on server: ', image_exists(url_submitted)))

            else:
                print('Submit button was not clicked')
                flash('Submit button was not clicked', 'alert alert-warning alert-dismissible fade show')
            return render_template('index1.html', photourlform=photourlform)

        # GET request
        #image = default_img
        return render_template('index1.html', photourlform=photourlform)

    except Exception as e:
        # 2be removed in final version
        flash(e, 'alert alert-danger')
        return redirect(url_for('index'))

# Run Flask server (host='0.0.0.0' - for Vagrant)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
# hello