from src import app
from src.models import *
from src.resources import *
import os
import openpyxl

from flask import Flask, request, redirect, url_for, make_response, Response
from werkzeug.utils import secure_filename


UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = set(['xlsx'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return ''

        requestFile = request.files['file']
        if requestFile and allowed_file(requestFile.filename):
            filename = secure_filename(requestFile.filename)
            dir_filename = os.path.join(UPLOADS_DIR, filename)
            requestFile.save(dir_filename)

            dataFile = Resource.openxlsx(dir_filename) #return value dictionary with column name
            statistics = Resource.import_database(dataFile)

            universityDegree = set(dataFile['Cod Titulacion'])
            subjects = set(dataFile['Cod Asignatura'])
            group = set(dataFile['Cod Grupo'])
            area = set(dataFile['Cod Area'])

            print(statistics)
            print('Nº Titulaciones existentes: {}'.format(len(universityDegree)))
            print('Nº Asignaturas existentes: {}'.format(len(subjects)))
            print('Nº Grupos existentes: {}'.format(len(group)))
            print('Nº Areas de conocimientos existentes: {}'.format(len(area)))

            os.remove(dir_filename)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''