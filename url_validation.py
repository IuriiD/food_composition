from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_wtf import Form
from wtforms import FileField, StringField, SubmitField, validators
from wtforms.validators import DataRequired, Length, URL
from flask_wtf.csrf import CSRFProtect
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
        #imageuploadform = UploadForm()
        customlabelform = CustomLabel()
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
                    print('Validation URL Ok')
                    flash('Url Ok', 'alert alert-warning alert-dismissible fade show')
                    image = photourlform.image_link.data
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