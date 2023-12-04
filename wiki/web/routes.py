"""
    Routes
    ~~~~~~
"""
import base64
import io
import os


import gridfs
from bson import ObjectId
from flask import Blueprint, Flask, render_template, url_for, send_file, current_app, flash, jsonify
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_pymongo import PyMongo

from wiki.core import Processor
from wiki.web.forms import EditorForm
from wiki.web.forms import LoginForm
from wiki.web.forms import RegistrationForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_pymongo import PyMongo
from io import BytesIO
from PIL import Image
from bson.objectid import ObjectId

bp = Blueprint('wiki', __name__)


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://wiki_user:Zion1997@myriki.vwplv3x.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(app)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
uri = "mongodb+srv://wiki_user:Zion1997@myriki.vwplv3x.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['<MyRiki>']
collection = db["images"]

collections = db.list_collection_names()
'''
for collection in collections:
    # drop each collection
    db[collection].drop()
'''

@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    images = collection.find()
    return render_template('index.html', images=images, pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    form = EditorForm(obj=page)

    # Retrieve images associated with the page from MongoDB using '_id'
    images = collection.find({"page_id": page._id})
    image_ids = [str(image['_id']) for image in images]

    return render_template('page.html', page=page, form=form, images=image_ids)

@bp.route('/image/<image_id>')
@protect
def display_image(image_id):
    # Retrieve image data from MongoDB
    image_data = collection.find_one({"_id": ObjectId(image_id)})["image"]

    # Convert binary image data to an image object
    image = Image.open(BytesIO(image_data))

    # Create a dynamic route to serve the image
    img_io = BytesIO()
    image.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

from flask import send_file


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    session['current_url'] = url
    upload_form = UploadForm()
    page = current_wiki.get(url)
    form = EditorForm(obj=page)

    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)

        form.populate_obj(page)
        file = form.file.data

        print("Request files:", request.files)
        print("File:", file)
        print("Form data:", form.data)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Store image in MongoDB
            image_data = file.read()
            image_id = collection.insert_one({"image": image_data}).inserted_id
            print("Image ID:", image_id)

            # Create image URL
            image_url = url_for('display_image', image_id=str(image_id))
            page.body += f'\n<img src="{image_url}" alt="{filename}">'

        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))

    return render_template('editor.html', upload_form=upload_form, form=form, page=page)



from wiki.web.forms import UploadForm
from flask import session


@bp.route('/upload/', methods=['POST'])
@protect

def upload():
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Store image in MongoDB
            image_data = file.read()
            image_id = collection.insert_one({"image": image_data}).inserted_id
            flash('Image was uploaded.', 'success')

            # Return the image ID and filename in the response
            return jsonify({'message': 'Image was uploaded successfully', 'image_id': str(image_id), 'filename': filename})
        else:
            flash('Unable to upload image.', 'error')
            return jsonify({'message': 'Unable to upload image.'})
    else:
        flash('No file part in the request.', 'error')
        return jsonify({'message': 'No file part in the request.'})


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from wiki.web.forms import ChangePasswordForm
from wiki.web import current_users

@bp.route('/changepass/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Assuming current_users is an instance of UserManager
        user_manager = current_users

        # Retrieve the current user
        current_user = user_manager.get_user(form.name.data)

        # Check the current password
        if current_user.check_password(form.password.data):
            # Change the password using UserManager methods
            new_password = form.new_password.data
            current_user.data['authentication_method'] = 'cleartext'
            current_user.data['password'] = new_password
            current_user.save()

            flash('Password changed successfully.', 'success')
            return redirect(url_for('wiki.index'))
        else:
            flash('Current password is incorrect.', 'danger')

    return render_template('changepass.html', form=form)


@bp.route('/register/', methods=['GET', 'POST'])
def user_register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Using current_users directly, assuming it's a UserManager instance
        user = current_users.add_user(username, password)

        if user:
            login_user(user)
            user.set('authenticated', True)
            flash('Registration and login successful.', 'success')
            return redirect(request.args.get("next") or url_for('wiki.index'))
        else:
            flash('Username already exists. Please choose a different one.', 'danger')

    return render_template('register.html', form=form)



@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/')
def user_index():
    pass


@bp.route('/user/create/')
def user_create():
    pass


@bp.route('/user/<int:user_id>/')
def user_admin(user_id):
    pass


@bp.route('/user/delete/<int:user_id>/')
def user_delete(user_id):
    pass


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
