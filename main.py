# [ Tickets ]
# Chatbot and\or Mobile platforms

# Validate img URL: https://timmyomahony.com/blog/upload-and-validate-image-from-url-in-django/
# Google Vision (GV) API - limit search from 10 to, say, 3-5 terms
# Sort Nutrionix (Nutr) API results by score (https://developer.nutritionix.com/docs/v1_1#/nutritionix_api_v1_1)
# Sexy results presentation (dynamic and/or stylish)
# also started but didn't finish improved Nutr requests
# DONE: Analyse/range/filter GV results using Google Graph (?) - fail, can't be used for food
# DONE: Allow users to edit results of GV results (maybe with search from Nutr DB)
# energy value

import os
import imghdr  # delete after update
import json
import plotly
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_wtf import Form
from wtforms import FileField, StringField, SubmitField, validators
from flask_wtf.csrf import CSRFProtect
from random import randint
from functions import google_vision, nutrionix_requests, valid_url_extension, valid_url_mimetype, image_exists
from parameters import products_n, how_many_terms
from keys import flask_secret_key

app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
app.secret_key = flask_secret_key


class UploadForm(Form):
    image_file = FileField('Upload an image', [
        validators.DataRequired('Looks like you didn\'t select any image to analyse. Please choose one')])
    imagesubmit = SubmitField('Submit')


class ImageUrl(Form):
    image_link = StringField('', [validators.URL('Invalid URL. Please provide a correct one')])
    image_link_submit = SubmitField('Submit')


class CustomLabel(Form):
    customlabel = StringField('', [validators.DataRequired('Please enter some food label'), validators.Length(2, 50,
                                                                                                              'Food label should be a word from 2 to 50 characters long')])
    labelsubmit = SubmitField('Update')


@app.route('/index/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@csrf.exempt
def index():
    try:
        imageuploadform = UploadForm()
        customlabelform = CustomLabel()
        photourlform = ImageUrl()

        nutrionix_data = {}
        nutrients_percentage = []
        labels = ['No labels']
        image = '/static/uploads/default_340x340.jpg'

        # POST-request
        if request.method == 'POST':
            session['products_n'] = products_n

            # So we have 3 forms:
            # Form 1 - imageuploadform [of class UploadForm(Form)] - with a FileField ('Choose file') and a button ('Submit')
            # Form 2 - remoteimgurlform [of class RemoteImgUrl(Form)] - with a StringField where user can enter image URL and with a button ('Submit')
            # Form 3 (appears only after analysis of the 1st image) - customlabelform [of class CustomLabel(Form)] - with a StringField for user's label for image and a button ('Update')

            # If 'Submit' button under upload image is clicked, ...
            if imageuploadform.imagesubmit.data:
                if imageuploadform.validate():
                    session['image'] = ''
                    filename_entered = request.files['image_file'].filename
                    if valid_url_extension(filename_entered) and valid_url_mimetype(filename_entered):
                        # If image passed our ckecks,
                        path = 'uploads/' + request.files['image_file'].filename
                        request.files['image_file'].save(os.path.join(app.static_folder, path))
                        # avoid image caching
                        image_path = 'static/uploads/' + request.files['image_file'].filename
                        image = image_path + '?' + str(randint(1, 10000))
                        session['image'] = image
                    else:
                        flash(
                            'Invalid image extension (not ".jpg", ".jpeg", ".png", ".gif" or "bmp") or invalid image format',
                            'alert alert-warning alert-dismissible fade show')
                        return render_template('index.html', imageuploadform=imageuploadform, photourlform=photourlform,
                                               image=image)
                else:
                    return render_template('index.html', imageuploadform=imageuploadform, photourlform=photourlform,
                                           image=image)

            # If 'Submit' button for provide URL field is clicked, ...
            if photourlform.image_link_submit.data:
                # Let's validate the image URL
                # Formal URL validation using URL validator from wtforms
                if photourlform.validate():
                    # Additional validations - https://timmyomahony.com/blog/upload-and-validate-image-from-url-in-django/
                    # 1. Validating the URL’s extension
                    # 2. Validating the URL mimetype
                    # 3. Validating that the image exists on the server (+ maybe it's <4Mb (Google Vision API's limit)
                    url_entered = photourlform.image_link.data
                    if valid_url_extension(url_entered) and valid_url_mimetype(url_entered) and image_exists(
                            url_entered):
                        image_path = photourlform.image_link.data
                        image = photourlform.image_link.data
                        session['image'] = photourlform.image_link.data
                    else:
                        flash(
                            'Image can\'t be analysed because of invalid file extension (not ".jpg", ".jpeg", ".png", ".gif" or "bmp"), invalid format or image does not exist on server',
                            'alert alert-warning alert-dismissible fade show')
                        return render_template('index.html', imageuploadform=imageuploadform, photourlform=photourlform,
                                               image=image)
                else:
                    print('Invalid image URL')
                    return render_template('index.html', imageuploadform=imageuploadform, photourlform=photourlform,
                                           image=image)

            # So now we have a link to image (uploaded to server or via remote URL) in variable 'image_path')
            # Let's get labels from Google Vision API
            # Errors may be returned at this step
            # labels = google_vision(image_path)[:products_n]

            # If 'Update' button under 'Incorrect labels? Please provide a better variant:' field is clicked
            if customlabelform.labelsubmit.data:
                invalidlabel = False
                if customlabelform.validate():
                    labels = [customlabelform.customlabel.data]
                    image = session['image']
                    session['products_n'] = 1
                else:
                    # If the field with custom label doesn't validate, return form with
                    # uploaded image but without any calculations for it (as they are supposed to be nonrelevant
                    # if user corrects labels
                    image = session['image']
                    return render_template('index.html', imageuploadform=imageuploadform, photourlform=photourlform,
                                           image=image, customlabelform=customlabelform, invalidlabel=True)
            else:
                labels = google_vision(image_path)[:products_n]

            # So now we have labels (either from image>GoogleVisionAPI or 1 label entered manually)
            # Let's get data for nutrients from Nutrionix.com API
            nutrionix_data = nutrionix_requests(labels)

            #flash(nutrionix_data, 'alert alert-warning alert-dismissible fade show')

            # If no foods can be found for label(-s) in Nutrionix DB, set invalidlabel flag to True and don't create a chart
            if (nutrionix_data['average_percents'][0] + nutrionix_data['average_percents'][1] +
                    nutrionix_data['average_percents'][0]) == 0:
                return render_template('index.html', imageuploadform=imageuploadform, image=image,
                                       invalidlabel=True, labels=labels, customlabelform=customlabelform,
                                       nutrionix_data=nutrionix_data, photourlform=photourlform)
            else:
                # Retrieve average percentages of fats/carbohydrates/proteins
                nutrients_percentage = nutrionix_data['average_percents']
                # labels = google_vision(image_b4_anticaching) # temp
                # nutrients_percentage = labels # temp

                # [ Plot.ly charts ]
                graphs = [
                    dict(
                        data=[
                            dict(
                                values=nutrients_percentage,
                                labels=['Fats', 'Carbohydrates', 'Proteins'],
                                type='pie',
                            ),
                        ],
                        layout=dict(
                            title='Ratio of fats, carbohydrates and proteins by weight',
                            width=660, height=450,
                            modebar=False,
                        )
                    )
                ]

                ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
                graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
                # [ Plot.ly charts END ]

                # flash(labels, 'alert alert-success alert-dismissible fade show')
                # flash('Image successfully uploaded', 'alert alert-success alert-dismissible fade show')
                return render_template('index.html', imageuploadform=imageuploadform, image=image, invalidlabel=False,
                                       nutrients_percentage=nutrients_percentage, labels=labels,
                                       customlabelform=customlabelform, ids=ids, graphJSON=graphJSON,
                                       nutrionix_data=nutrionix_data, photourlform=photourlform)

        # GET request
        # image = default_img
        return render_template('index.html', imageuploadform=imageuploadform, photourlform=photourlform, image=image)

    except Exception as e:
        # 2be removed in final version
        flash(e, 'alert alert-danger')
        return redirect(url_for('index'))


@app.errorhandler(404)
@csrf.exempt
def not_found(e):
    return render_template('404.html')


# Run Flask server (host='0.0.0.0' - for Vagrant)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    # hello
