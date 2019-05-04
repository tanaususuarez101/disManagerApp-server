from src import app
from src.models import *
import os
import openpyxl
from flask import Flask, request, redirect, url_for, make_response, Response
from werkzeug.utils import secure_filename


UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = set(['xlsx'])



@app.route('/test')
def text():
    return "Test Finalizado"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return ''
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            dir_filename = os.path.join(UPLOADS_DIR, filename)
            file.save(dir_filename)
            resp = open_file(dir_filename)
            os.remove(dir_filename)
            return Response(status=200)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

def open_file(dir_filename=None):

    doc = openpyxl.load_workbook(dir_filename)
    hoja = doc.get_sheet_by_name('Hoja1')

    for row in hoja.rows:
        if row[0].value and type(row[0].value) is not str:

            titulacion = Titulacion.query.get(row[1].value)
            if titulacion is None:
                titulacion = Titulacion(
                    cod_titulacion=row[1].value,
                    cod_plan=row[2].value,
                    cod_especial=row[3].value,
                    acronimo=row[4].value,
                    nombre=row[5].value,
                    centro=row[6].value
                ).add()
                print("titulacion añadida: " + titulacion.nombre)

            grupo = Grupo.query.get(row[12].value)
            if grupo is None:
                grupo = Grupo(
                    cod_grupo=row[12].value,
                    tipo=row[13].value
                ).add()
                print("Grupo añadido")

            area = AreaConocimiento.query.get(row[16].value)
            if area is None:
                area = AreaConocimiento(
                    cod_area=row[16].value,
                    nombre=row[17].value
                ).add()
                print('Area conocimiento añadida:' + area.nombre)

            asignatura = Asignatura.query.get(row[7].value)
            if asignatura is None:
                asignatura = Asignatura(
                        cod_asignatura=row[7].value,
                        nombre=row[8].value,
                        curso=row[9].value,
                        cuatrimestre=row[10].value,
                        tipo=row[11].value
                )
                print("Asignatura añadida: " + asignatura.nombre)

            asignatura = titulacion.addAsignatura(asignatura)
            asignatura.addArea(area)
            asignado = Asignado(num_horas=row[15].value)
            asignado.grupo = grupo
            asignado.asignatura = asignatura
            asignado.add()


    return 'Dato guardo'