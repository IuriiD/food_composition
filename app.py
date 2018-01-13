# also started but didn't finish improved Nutr requests

import os, imghdr, json, plotly
from flask import Flask, render_template, url_for, request, redirect, flash, session
from wtforms import Form, FileField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL
from flask_wtf.csrf import CSRFProtect
from random import randint
from functions import google_vision, nutrionix_requests
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
        nutrients_percentage = []
        labels = ['nothing']
        image = '/static/uploads/default_340x340.jpg'

        # POST-request
        if request.method == 'POST':
            if imageuploadform.imagesubmit.data:
                if imageuploadform.validate():
                    session['image'] = ''
                    if request.files['image_file'].filename == '':
                        flash('Looks like you didn\'t select any file to upload. Please choose one',
                              'alert alert-warning alert-dismissible fade show')
                        return render_template('index.html', imageuploadform=imageuploadform, image=image)
                    if request.files['image_file'].filename[-4:].lower() != '.jpg':
                        flash('Invalid file extension. Only .jpg/.jpeg images allowed at the moment',
                              'alert alert-warning alert-dismissible fade show')
                        return render_template('index.html', imageuploadform=imageuploadform, image=image)
                    if imghdr.what(request.files['image_file']) != 'jpeg':
                        flash(
                            'Invalid image format. Are you sure that\'s really a .jpeg image (only .jpg/.jpeg images allowed at the moment)? Please choose a different one',
                            'alert alert-warning alert-dismissible fade show')
                        return render_template('index.html', imageuploadform=imageuploadform, image=image)

                    path = 'uploads/' + request.files['image_file'].filename
                    request.files['image_file'].save(os.path.join(app.static_folder, path))
                    # avoid image caching
                    image_b4_anticaching = 'static/uploads/' + request.files['image_file'].filename
                    image = image_b4_anticaching + '?' + str(randint(1, 10000))
                    session['image'] = image

                    labels = google_vision(image_b4_anticaching)[:3]

            if customlabelform.labelsubmit.data and customlabelform.validate():
                labels = [customlabelform.customlabel.data]
                image = session['image']

            nutrients_percentage = nutrionix_requests(labels)
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
            return render_template('index.html', imageuploadform=imageuploadform, image=image, nutrients_percentage=nutrients_percentage, labels=labels, customlabelform=customlabelform, ids=ids, graphJSON=graphJSON)

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