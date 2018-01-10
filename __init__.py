from flask import Flask, render_template, url_for, request, redirect, flash
from wtforms import Form, FileField
from wtforms.validators import DataRequired
#from flask_bootstrap import Bootstrap
from pymongo import MongoClient
from keys import api_key, app_secret_key

app = Flask(__name__)
#bootstrap = Bootstrap(app)
app.secret_key = app_secret_key

class UploadForm(Form):
    image_file = FileField('')

@app.route('/index/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        indexform = IndexForm(request.form)
        #flash(makemodeloutput)

        # POST-request
        if request.method == 'POST' and indexform.validate():
            makemodelurl = indexform.makemodels.data
            return redirect(makemodelurl)

        # the first (GET) request for a index page
        return render_template('index.html', makemodellist=makemodellist, indexform=indexform)

    except Exception as e:
        # 2be removed in final version
        #flash(e, 'alert alert-danger')
        return redirect(url_for('index'))

@app.route('/avatar/', methods=['GET', 'POST'])
@login_required
def avatar():
    try:
        # get the name for the avatar image from DB (by default = default.jpg, else - str(_id).jpg)
        client = MongoClient()
        db = client.db
        users = db.users  # collection 'users' in 'db' database
        docID = None
        username = session['username']  # getting username from session variable (to determine document's ID)
        docID = users.find_one({'username': username}).get('_id')
        image = '../static/uploads/' + users.find_one({'_id': docID})['avatar'] + '?' + str(
            random.randint(1, 10000))
        # flash(image) # temp
        # flash(str(docID)) # temp

        avatarform = UploadForm()

        if request.method == 'POST':
            if request.files['image_file'].filename == '':
                flash('Looks like you didn\'t select any file to upload. Please choose one',
                      'alert alert-warning')
                return render_template('avatar.html', avatarform=avatarform, image=image)
            if request.files['image_file'].filename[-4:].lower() != '.jpg':
                flash('Invalid file extension. Only .jpg/.jpeg images allowed',
                      'alert alert-warning')
                return render_template('avatar.html', avatarform=avatarform, image=image)
            if imghdr.what(request.files['image_file']) != 'jpeg':
                flash(
                    'Invalid image format. Are you sure that\'s really a .jpeg image? Please choose a different one',
                    'alert alert-warning')
                return render_template('avatar.html', avatarform=avatarform, image=image)

            path = 'uploads/' + str(docID) + '.jpg'
            request.files['image_file'].save(os.path.join(app.static_folder, path))
            users.update_one({'_id': docID}, {'$set': {'avatar': str(docID) + '.jpg'}})
            # avoid image caching
            image = '../static/uploads/' + str(docID) + '.jpg' + '?' + str(random.randint(1, 10000))
            # flash(image) # temp
            flash(
                'Avatar successfully updated!', 'alert alert-success')
        return render_template('avatar.html', avatarform=avatarform, image=image)

        # GET request
        return render_template('avatar.html', avatarform=avatarform, image=image)

    except Exception as e:
        # 2be removed in final version
        #flash(e, 'alert alert-danger')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

# Run Flask server (host='0.0.0.0' - for Vagrant)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
# hello