from datetime import timedelta
from fileinput import filename
from time import sleep
from flask import Flask, Response, flash, request, redirect, url_for, send_file, session, send_from_directory, abort
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
import algoParoles
from flask_session import Session
import tempfile

resultRoute = '/result/'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3'}

app = Flask(__name__)
#app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=0.5)
Session(app)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.post('/send')
def upload_file():

    #Check si le nom file est bien present
    if 'file' not in request.files:
        return Response("{'error' : 'file not in files'}", status=400)

    #print(request.files.getlist('file'))
    with tempfile.TemporaryDirectory(dir='./uploads') as dirPath:
        for file in request.files.getlist('file'):
            fileName = secure_filename(file.filename)
            file.save(dirPath + '/' + fileName)
        resultFileName = algoParoles.paroliser(dirPath, 'testie')
        sleep(1)
        
    res = {'msg': 'ok',
    'urlForDownload': resultRoute + resultFileName}
    return res


@app.get(resultRoute + '<fileName>')
def send_file(fileName):
    try:
        print(os.getcwd())
        return send_from_directory(app.config['UPLOAD_FOLDER'] + './results', fileName, as_attachment=True)
    except FileNotFoundError:
        abort(404)



if __name__ == "__main__":
    app.run()