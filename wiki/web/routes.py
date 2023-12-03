"""
    Routes
    ~~~~~~
"""
import base64
import io
import os

from wiki.core import db
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
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect

bp = Blueprint('wiki', __name__)


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
    return render_template('index.html', pages=pages)


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://wiki_user:Zion1997@myriki.vwplv3x.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(app)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)

    # Fetch the uploaded file
    uploaded_file = None
    if page.file_id:
        gridout = fs.get(page.file_id)
        if gridout.content_type.startswith('image'):
            # If the file is an image, embed it in the page
            image_url = url_for('wiki.file', filename=gridout.filename)
            page.body += f'\n<img src="{image_url}" alt="{gridout.filename}">'
        else:
            # Otherwise, add a download link to the page
            file_url = url_for('wiki.file', filename=gridout.filename)
            page.body += f'\nDownload file: <a href="{file_url}" download="{gridout.filename}">{gridout.filename}</a>'

    return render_template('page.html', page=page)


from flask import send_file
from io import BytesIO

@bp.route('/image/<identifier>')
def serve_image(identifier):
    # Create a GridFS object
    fs = gridfs.GridFS(db)

    try:
        # Try to use the identifier as a GridFS ID
        _id = ObjectId(identifier)
        grid_out = fs.get(_id)
    except:
        # If that fails, use the identifier as a filename
        grid_out = fs.get_last_version(filename=identifier)

    # Send the image data to the client
    response = send_file(grid_out, mimetype=grid_out.content_type)
    return response

@bp.route('/file/<filename>', methods=['GET'])
@protect
def file(filename):
    gridout = fs.get_last_version(filename=filename)
    if gridout:
        return send_file(io.BytesIO(gridout.read()), mimetype=gridout.content_type, as_attachment=True,
                         download_name=filename)
    else:
        flash('File not found', 'error')
        return redirect(url_for('wiki.home'))


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    session['current_url'] = url  # Store the current URL in the session
    upload_form = UploadForm()
    page = current_wiki.get(url)
    form = EditorForm(obj=page)

    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)

        form.populate_obj(page)
        file = form.file.data

        print("Request files:", request.files)  # Print the files in the request
        print("File:", file)  # Print the file
        print("Form data:", form.data)  # Print the form data

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_id = fs.put(file, filename=filename)  # Store file in MongoDB
            print("File ID:", file_id)  # Print the file ID

            # Read the uploaded file content
            uploaded_file = fs.get(file_id)
            print("Uploaded file:", uploaded_file)

            uploaded_content = uploaded_file.read().decode('utf-8')

            # Add the uploaded content to the page body
            page.body += '\n' + uploaded_content

            page.file_id = file_id
            page.filepath = url_for('wiki.uploaded_file', filename=filename)

        # Handle the image data
        image_data = form.imageData.data
        if image_data:
            # The data URL includes a MIME type and base64 data. We only need the data.
            image_data = image_data.split(',', 1)[1]
            image_data = base64.b64decode(image_data)
            image_file = io.BytesIO(image_data)

            # Save the image file
            image_filename = secure_filename(form.imageName.data)
            image_file_id = fs.put(image_file, filename=image_filename)

            # Add the image to the page
            image_url = url_for('wiki.file', filename=image_filename)
            page.body += f'\n<img src="{image_url}" alt="{image_filename}">'

        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))

    return render_template('editor.html', upload_form=upload_form, form=form, page=page)


from wiki.core import fs
from wiki.web.forms import UploadForm
from flask import session


@bp.route('/upload/', methods=['POST'])
@protect
def upload():
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_id = fs.put(file, filename=filename)  # Store file in MongoDB
            session['file_id'] = str(file_id)  # Convert ObjectId to string
            flash('File was uploaded.', 'success')

            # Return the file ID and filename in the response
            return jsonify({'file_id': str(file_id), 'filename': filename})

    return redirect(url_for('wiki.edit', url=session.get('current_url', '')))

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
