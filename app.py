import os, imghdr
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_bootstrap import Bootstrap
from wtforms import Form, FileField
from wtforms.validators import DataRequired
from random import randint
from functions import google_vision, nutrionix_requests
from keys import flask_secret_key

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = flask_secret_key

class UploadForm(Form):
    image_file = FileField('')

@app.route('/index/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        imageuploadform = UploadForm(request.form)
        nutrients_percentage = []
        default_img = '/static/uploads/default_340x340.jpg'

        # POST-request
        if request.method == 'POST':
            if request.files['image_file'].filename == '':
                flash('Looks like you didn\'t select any file to upload. Please choose one',
                      'alert alert-warning alert-dismissible fade show')
                return render_template('index.html', imageuploadform=imageuploadform, image=default_img, nutrients_percentage=nutrients_percentage)
            if request.files['image_file'].filename[-4:].lower() != '.jpg':
                flash('Invalid file extension. Only .jpg/.jpeg images allowed at the moment',
                      'alert alert-warning alert-dismissible fade show')
                return render_template('index.html', imageuploadform=imageuploadform, image=default_img, nutrients_percentage=nutrients_percentage)
            if imghdr.what(request.files['image_file']) != 'jpeg':
                flash(
                    'Invalid image format. Are you sure that\'s really a .jpeg image (only .jpg/.jpeg images allowed at the moment)? Please choose a different one',
                    'alert alert-warning alert-dismissible fade show')
                return render_template('index.html', imageuploadform=imageuploadform, image=default_img, nutrients_percentage=nutrients_percentage)

            path = 'uploads/' + request.files['image_file'].filename
            request.files['image_file'].save(os.path.join(app.static_folder, path))
            # avoid image caching
            image_b4_anticaching = 'static/uploads/' + request.files['image_file'].filename
            image = image_b4_anticaching + '?' + str(randint(1, 10000))

            #nutrients_percentage = nutrionix_requests(google_vision(image_b4_anticaching))
            labels = google_vision(image_b4_anticaching) # temp
            nutrients_percentage = labels # temp

            flash(nutrients_percentage, 'alert alert-success alert-dismissible fade show')
            #flash('Image successfully uploaded', 'alert alert-success alert-dismissible fade show')
            return render_template('index.html', imageuploadform=imageuploadform, image=image, nutrients_percentage=nutrients_percentage)

        # GET request
        image = default_img
        return render_template('index.html', imageuploadform=imageuploadform, image=default_img, nutrients_percentage=nutrients_percentage)

    except Exception as e:
        # 2be removed in final version
        flash(e, 'alert alert-danger')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

# Run Flask server (host='0.0.0.0' - for Vagrant)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
# hello