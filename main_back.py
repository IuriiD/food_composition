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
from wtforms import FileField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL
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
    image_link = StringField('Paste image URL',validators=[URL])
    imagesubmit = SubmitField('Submit')

class RemoteImgUrl(Form):
    image_link = StringField('Paste image URL', validators=[URL])
    imagesubmit = SubmitField('Submit')

class CustomLabel(Form):
    customlabel = StringField('', validators=[Length(2, 50)])
    labelsubmit = SubmitField('Update')

@app.route('/index/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@csrf.exempt
def index():
    try:
        imageuploadform = UploadForm(request.form)
        customlabelform = CustomLabel(request.form)
        nutrionix_data = {}
        nutrients_percentage = []
        labels = ['No labels']
        image = '/static/uploads/default_340x340.jpg'

        # POST-request
        if request.method == 'POST':
            session['products_n'] = products_n

            # So we have 2 forms:
            # Form 1 - imageuploadform [UploadForm(Form)] - with 2 fields, FileField ('Choose file') and StringField for custom image URL, and a button ('Submit')
            # Form 2 - customlabelform [CustomLabel(Form)] - with 1 StringField for user's labels for image and a button ('Update')
            # First check which one of the 2 buttons/forms is clicked
            # If 'Submit' button under upload image/provide URL is clicked...
            if imageuploadform.imagesubmit.data and imageuploadform.validate():
                # So 'Submit' button for image/image URL has been clicked
                # If image URL field is not empty - check if it validates and if yes, get the URL
                if imageuploadform.image_link.data != '':
                    #if imageuploadform.validate():
                        # Image URL may be subjected to additional checks here
                        # https://timmyomahony.com/blog/upload-and-validate-image-from-url-in-django/
                    image_path = imageuploadform.image_link.data
                    image = imageuploadform.image_link.data
                    session['image'] = imageuploadform.image_link.data
                    #else:
                    #    flash('Invalid image URL. Please provide a correct one',
                    #          'alert alert-warning alert-dismissible fade show')
                    #    return render_template('index.html', imageuploadform=imageuploadform, image=image)
                # If image URL field is empty - check if image upload for validates, save file and get the path
                else:
                    #if imageuploadform.validate():
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

                    path = 'uploads/' + request.files['image_file'].filename
                    request.files['image_file'].save(os.path.join(app.static_folder, path))
                    # avoid image caching
                    image_path = 'static/uploads/' + request.files['image_file'].filename
                    image = image_path + '?' + str(randint(1, 10000))
                    session['image'] = image

                # So now we have a link to image (uploaded to server or via remote URL) in variable 'image_path'
                # Let's get labels from Google Vision API
                # Errors may be returned at this step
                labels = google_vision(image_path)[:products_n]

            # If 'Update' button under 'Incorrect labels? Please provide a better variant:' field is clicked
            if customlabelform.labelsubmit.data:
                invalidlabel = False
                #flash('Update button hit')
                if customlabelform.validate():
                    #flash('Update form validated')
                    labels = [customlabelform.customlabel.data]
                    image = session['image']
                    session['products_n'] = 1
                else:
                    #flash('Invalid label. Please enter a correct label (word 2-50 characters long)', 'alert alert-warning alert-dismissible fade show')
                    image = session['image']
                    return render_template('index.html', imageuploadform=imageuploadform, image=image, customlabelform=customlabelform, invalidlabel=True)

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
            return render_template('index.html', imageuploadform=imageuploadform, image=image, nutrients_percentage=nutrients_percentage, labels=labels, customlabelform=customlabelform, ids=ids, graphJSON=graphJSON, nutrionix_data=nutrionix_data)

        # GET request
        #image = default_img
        return render_template('index.html', imageuploadform=imageuploadform, image=image)

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