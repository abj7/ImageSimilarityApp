"""
This script runs the ImageSimilarity application using a development server.
"""

import os, shutil
from similar import findsim
from flask import Flask, render_template, request, session, url_for, redirect
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, patch_request_class, IMAGES
from werkzeug.utils import secure_filename


basedir = os.path.abspath(os.path.dirname(__file__))

try:
    os.mkdir("static/uploads")
except:
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = "key"
app.config.update(
    UPLOADED_PATH=os.path.join('static', 'uploads'),
    DROPZONE_ALLOWED_FILE_TYPE='image',
    DROPZONE_MAX_FILE_SIZE=3,
    #DROPZONE_MAX_FILES=100,
    DROPZONE_PARALLEL_UPLOADS=100,
    DROPZONE_UPLOAD_MULTIPLE=True,
)

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

dropzone = Dropzone(app)

@app.route('/', methods=['POST', 'GET'])
def upload():
    if "file_urls" not in session:
        session['file_urls'] = []
    filenames = session['file_urls']
    if request.method == 'POST':
        for key, f in request.files.items():
            if key.startswith('file'):
                path = os.path.join(app.config['UPLOADED_PATH'], f.filename)
                f.save(path)
                filenames.append(path)
        session['file_urls'] = filenames
    return render_template('index.html')

@app.route('/query', methods=['POST', 'GET'])
def query():
    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('upload'))
    filenames = session['file_urls']

    query_image = ""
    if 'photo' in request.files and request.method == "POST":
        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        query_image = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    topn = findsim(filenames, query_image)
    sim = []
    for i in topn[0]:
        sim.append(os.path.join(app.config['UPLOAD_FOLDER'], os.path.split(filenames[i])[1]))
    session.pop('file_urls', None)
    return render_template('results.html', file_urls = sim)

if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug = True)
