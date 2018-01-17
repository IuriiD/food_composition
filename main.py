# also started but didn't finish improved Nutr requests

# [ Tickets ]
# Google Vision (GV) API - limit search from 10 to, say, 3-5 terms
# DONE: Analyse/range/filter GV results using Google Graph (?) - fail, can't be used for food
# Sort Nutrionix (Nutr) API results by score (https://developer.nutritionix.com/docs/v1_1#/nutritionix_api_v1_1)
# Allow users to edit results of GV results (maybe with search from Nutr DB)
# Sexy results presentation (dynamic and/or stylish)
# Mobile platforms

import os, imghdr, json, plotly
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_wtf import Form
from wtforms import FileField, StringField, SubmitField, validators
from flask_wtf.csrf import CSRFProtect
from random import randint
from functions import google_vision, nutrionix_requests
from parameters import products_n, how_many_terms
#import plotly.plotly as py
#import plotly.graph_objs as go
from keys import flask_secret_key


app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
app.secret_key = flask_secret_key


class UploadForm(Form):
    image_file = FileField('Upload an image')
    imagesubmit = SubmitField('Submit')


class ImageUrl(Form):
    image_link = StringField('', [validators.URL('Invalid URL. Please provide a correct one')])
    image_link_submit = SubmitField('Submit')


class CustomLabel(Form):
    customlabel = StringField('', [validators.DataRequired('Please enter some food label'), validators.Length(2, 50, 'Food label should be a word from 2 to 50 characters long')])
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
            if imageuploadform.imagesubmit.data and imageuploadform.validate():
                session['image'] = ''
                if request.files['image_file'].filename == '':
                    flash('Looks like you didn\'t select any image to analyse. Please choose one',
                          'alert alert-warning alert-dismissible fade show')
                    return render_template('index.html', imageuploadform=imageuploadform, image=image)
                if request.files['image_file'].filename[-4:].lower() != '.jpg':
                    flash('Invalid file extension. Only .jpg images allowed at the moment',
                          'alert alert-warning alert-dismissible fade show')
                    return render_template('index.html', imageuploadform=imageuploadform, image=image)
                if imghdr.what(request.files['image_file']) != 'jpeg':
                    flash(
                        'Invalid image format. Are you sure that\'s really a .jpeg image (only .jpg images allowed at the moment)? Please choose a different one',
                        'alert alert-warning alert-dismissible fade show')
                    return render_template('index.html', imageuploadform=imageuploadform, image=image)
                # If image passed our ckecks,
                path = 'uploads/' + request.files['image_file'].filename
                request.files['image_file'].save(os.path.join(app.static_folder, path))
                # avoid image caching
                image_path = 'static/uploads/' + request.files['image_file'].filename
                image = image_path + '?' + str(randint(1, 10000))
                session['image'] = image

            # If 'Submit' button for provide URL field is clicked, ...
            if photourlform.image_link_submit.data:
                if photourlform.validate():
                    # Image URL may be subjected to additional checks here
                    # https://timmyomahony.com/blog/upload-and-validate-image-from-url-in-django/
                    image_path = photourlform.image_link.data
                    image = photourlform.image_link.data
                    session['image'] = photourlform.image_link.data
                else:
                    print('Image URL not valid')
                    return render_template('index.html', imageuploadform=imageuploadform, photourlform=photourlform,
                                           image=image)

            # So now we have a link to image (uploaded to server or via remote URL) in variable 'image_path')
            # Let's get labels from Google Vision API
            # Errors may be returned at this step
            labels = google_vision(image_path)[:products_n]

            # If 'Update' button under 'Incorrect labels? Please provide a better variant:' field is clicked
            if customlabelform.labelsubmit.data and customlabelform.validate():
                invalidlabel = False
                labels = [customlabelform.customlabel.data]
                image = session['image']
                session['products_n'] = 1

            # So now we have labels (either from image>GoogleVisionAPI or 1 label entered manually)
            # Let's get data for nutrients from Nutrionix.com API
            nutrionix_data = nutrionix_requests(labels)

            # Retrieve average percentages of fats/carbohydrates/proteins
            nutrients_percentage = nutrionix_data['average_percents']
            #labels = google_vision(image_b4_anticaching) # temp
            #nutrients_percentage = labels # temp

            # [ Plot.ly charts ]
            graphs = [
                dict(
                    data=[
                        dict(
                            values=nutrients_percentage,
                            labels=['Fats','Carbohydrates','Proteins'],
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

            #flash(labels, 'alert alert-success alert-dismissible fade show')
            #flash('Image successfully uploaded', 'alert alert-success alert-dismissible fade show')
            return render_template('index.html', imageuploadform=imageuploadform, image=image, nutrients_percentage=nutrients_percentage, labels=labels, customlabelform=customlabelform, ids=ids, graphJSON=graphJSON, nutrionix_data=nutrionix_data, photourlform=photourlform)

        # GET request
        #image = default_img
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