from src import app
from src.resources import *
import os

from flask import request, json, jsonify, Response, send_file
from werkzeug.utils import secure_filename

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = set(['xlsx'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def menu():
    return \
        '''
        <p>Menú</p>
        <ul>
            <li><a href="upload_database">Importar Titulaciones, Asignaturas, Areas de conocimiento, Grupos</a></li>
            <li><a href="upload_pda">Importar PDA</a></li>
            <li><a href="upload_teacher">Importar Teacher</a></li>
            <li><a href="download_database">Descargar base de datos</a></li>
            <li><a href="export_database">Exportar datos</a></li>
            <li><a href="test_export">Test de exportacion de datos</a></li>            
        </ul>
        '''


@app.route('/upload_database', methods=['GET', 'POST'])
def upload_database():
    if request.method == 'POST':
        # check if the post request has the file part
        try:
            if 'file' not in request.files:
                return ''

            request_file = request.files['file']
            if request_file and allowed_file(request_file.filename):
                filename = secure_filename(request_file.filename)
                filename_dir = os.path.join(UPLOADS_DIR, filename)
                request_file.save(filename_dir)

                data_file = Resource.openxlsx(filename_dir)  # return value dictionary with column name
                entity_file = Resource.file_statistics(data_file)
                data_saved = Resource.import_database(data_file)
                print('Entidades del fichero: {}\nDatos guardados: {}'.format(entity_file, data_saved))

                os.remove(filename_dir)

                return jsonify(data_saved), 200
            else:
                return Response('File not found', status=404)
        except Exception as error:
            print(error)
            return Response('Internal Server Error', status=500)

    return '''
    <!doctype html>
    <title>Subir un nuevo fichero</title>
    <h1>Cargar contenido principal del PDO en la base de datos</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Cargar>
    </form>
    '''


@app.route('/upload_teacher', methods=['GET', 'POST'])
def upload_teacher():
    if request.method == 'POST':
        # check if the post request has the file part
        try:
            if 'file' not in request.files:
                return ''

            request_file = request.files['file']
            if request_file and allowed_file(request_file.filename):
                filename = secure_filename(request_file.filename)
                filename_dir = os.path.join(UPLOADS_DIR, filename)
                request_file.save(filename_dir)

                data_file = Resource.openxlsx(filename_dir)  # return value dictionary with column name
                Resource.import_teacher(data_file)
                print(data_file)
                os.remove(filename_dir)

                return jsonify(), 200
            else:
                return Response('File not found', status=404)
        except Exception as error:
            print(error)
            return Response('Internal Server Error', status=500)

    return '''
    <!doctype html>
    <title>Subir fichero</title>
    <h1>Subir un nuevo fichero con profesores</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Cargar>
    </form>
    '''


@app.route('/upload_simulation', methods=['GET', 'POST'])
def upload_simulation():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return ''

        request_file = request.files['file']
        if request_file and allowed_file(request_file.filename):
            filename = secure_filename(request_file.filename)
            filename_dir = os.path.join(UPLOADS_DIR, filename)
            request_file.save(filename_dir)

            data_file = Resource.openxlsx(filename_dir)  # return value dictionary with column name
            Resource.load_simulation(data_file)
            os.remove(filename_dir)

            return jsonify(), 200
        else:
            return Response('File not found', status=404)

    return '''
    <!doctype html>
    <title>Subir fichero</title>
    <h1>Subir un nuevo fichero con profesores</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Cargar>
    </form>
    '''


@app.route('/upload_pda', methods=['GET', 'POST'])
def upload_pda():
    if request.method == 'POST':
        # check if the post request has the file part
        try:
            if 'file' not in request.files:
                return ''

            request_file = request.files['file']
            if request_file and allowed_file(request_file.filename):
                filename = secure_filename(request_file.filename)
                filename_dir = os.path.join(UPLOADS_DIR, filename)
                request_file.save(filename_dir)

                data_file = Resource.openxlsx(filename_dir)  # return value dictionary with column name
                Resource.import_pda(data_file)
                print(data_file)
                os.remove(filename_dir)

                return jsonify(), 200
            else:
                return Response('File not found', status=404)
        except Exception as error:
            print(error)
            return Response('Internal Server Error', status=500)

    return '''
    <!doctype html>
    <title>Subir un nuevo fichero con Proyecto docente</title>
    <h1>Subir un nuevo fichero</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Cargar>
    </form>
    '''


@app.route('/download_database', methods=['GET'])
def download_database():
    file_data = Resource.backup_database()
    return send_file(file_data)


@app.route('/export_database', methods=['GET'])
def export_database():
    file_data = Resource.export_database()
    return send_file(file_data)


@app.route('/test_export', methods=['GET', 'POST'])
def test_export():
    if request.method == 'POST':
        # check if the post request has the file part

        if 'file1' not in request.files:
            return ''

        try:
            requestFile1 = request.files['file1']
            requestFile2 = request.files['file2']

            entity_file1 = entity_file2 = {}
            filename1 = filename2 = ''
            if requestFile1 and allowed_file(requestFile1.filename):
                filename1 = secure_filename(requestFile1.filename)
                filename_dir1 = os.path.join(UPLOADS_DIR, filename1)
                requestFile1.save(filename_dir1)

                data_file1 = Resource.openxlsx(filename_dir1)
                entity_file1 = Resource.file_statistics(data_file1)
                print(entity_file1)

                os.remove(filename_dir1)

            if requestFile2 and allowed_file(requestFile2.filename):
                filename2 = secure_filename(requestFile2.filename)
                filename_dir2 = os.path.join(UPLOADS_DIR, filename2)
                requestFile2.save(filename_dir2)

                data_file2 = Resource.openxlsx(filename_dir2)
                entity_file2 = Resource.file_statistics(data_file2)
                print(entity_file2)

                os.remove(filename_dir2)

            return jsonify({filename1: entity_file1, filename2: entity_file2})
        except Exception as e:
            return Response('Error server internal {}'.format(e), status=500)

    return '''
    <!doctype html>
    <title>Comparar fichero</title>
    <h1>Comparar ficheros de salida: </h1>    
    <form method=post enctype=multipart/form-data>
        <p><input type=file name=file1></p>
        <p><input type=file name=file2></p>          
        <p><input type=submit value=Cargar></p>
    </form>
    '''


@app.route('/group', methods=['GET'])
@app.route('/group/<group_cod>/<subject_cod>/<area_cod>', methods=['GET'])
def get_group(group_cod=None, subject_cod=None, area_cod=None,):
    if not subject_cod and not area_cod and not group_cod:
        subject_list = []

        for university in UniversityDegree.get_all():
            for subject in university.subject:
                for group in subject.group:
                    area = KnowledgeArea.get(group.area_cod)
                    cover_hour = 0
                    for impart in group.teacher:
                        cover_hour += float(impart.hours)

                    cover_hour -= float(group.hours)
                    subject_list.append({
                        "university_degree_name": university.name,
                        "university_degree_cod": university.university_degree_cod,
                        "university_degree_acronym": university.acronym,
                        "subject_cod": subject.subject_cod,
                        "subject_name": subject.name,
                        "subject_course": subject.course,
                        "subject_semester": subject.semester,
                        "group_cod": group.group_cod,
                        "group_area_name": area.name,
                        "group_area_cod": area.area_cod,
                        "group_type": group.type,
                        "group_hours": group.hours,
                        "cover_hours": cover_hour
                    })
        return jsonify(subject_list)
    else:
        group = Group.get(group_cod, subject_cod, area_cod)
        if group:
            subject = Subject.get(subject_cod)
            university = subject.university_degree
            area = KnowledgeArea.get(area_cod)
            teacher = []
            for impart in group.teacher:
                te = impart.teacher
                print(te.name)
                teacher.append({
                    'teacher_name': te.name,
                    'teacher_surname': te.surnames,
                    'teacher_assigned': impart.hours
                })
            return jsonify({
                "university_degree_name": university.name,
                "knowledge_area_name": area.name,
                "subject_name": subject.name,
                "group_cod": group.group_cod,
                "group_type": group.type,
                "group_hours": group.hours,
                "teacher": teacher
            })
    return jsonify({})


@app.route('/pda/', methods=['GET'])
@app.route('/pda', methods=['GET'])
def get_pda():
    list_pda = []
    PDAs = PDA.getAll()
    for pda in PDAs:
        sub = Subject.get(pda.subject_cod)
        if sub:
            university_degree = UniversityDegree.get(sub.university_degree_cod)
            for coor in sub.teacher:
                if coor.subject_coor:
                    coor_subject = Teacher.get(coor.teacher_dni)
                    area = KnowledgeArea.get(coor_subject.area_cod)



            list_pda.append({
                'id': pda.id,
                'status': pda.status,
                'observations': pda.observations,
                'university_degree_name': university_degree.name,
                'university_degree_cod': university_degree.university_degree_cod,
                'subject_name': sub.name,
                'subject_cod': sub.subject_cod
                #'knowledge_area_name': area.name,
                #'knowledge_area_cod': area.area_cod,
                #'teacher_name': coor_subject.name,
                #'teacher_surnames': coor_subject.surnames,
                #'teacher_dni': coor_subject.dni
            })

    return jsonify(list_pda)


@app.route('/coordinator/', methods=['GET'])
@app.route('/coordinator', methods=['GET'])
def get_coordinator():
    coor_subject = []
    coor_practice = []
    for coordinate in Coordinator.get_all():
        sub = Subject.get(coordinate.subject_cod)
        tea = Teacher.get(coordinate.teacher_dni)
        area = KnowledgeArea.get(tea.area_cod)
        university_degree = UniversityDegree.get(sub.university_degree_cod)

        item = {
            'university_degree_name': university_degree.name,
            'knowledge_area_name': area.name,
            'subject_name': sub.name,
            'subject_type': sub.type,
            'subject_semester': sub.semester,
            'teacher_name': tea.name,
            'teacher_surnames': tea.surnames
        }
        if coordinate.practice_coor:
            coor_practice.append(item)
        if coordinate.subject_coor:
            coor_subject.append(item)

    return jsonify({'subject': coor_subject, 'practice': coor_practice})


@app.route('/tutorial/', methods=['GET'])
@app.route('/tutorial', methods=['GET'])
def get_tutorial():

    list_tutorial = []
    for teacher in Teacher.get_all():
        area = KnowledgeArea.get(teacher.area_cod)
        tutorial = teacher.tutorial
        if tutorial:
            list_tutorial.append({
                'teacher_name': teacher.name,
                'teacher_surnames': teacher.surnames,
                'teacher_dni': teacher.dni,
                'knowledge_area_name': area.name,
                'tutorial_hours': teacher.tutorial_hours,
                'cover_hours': tutorial.hours,
                'unassigned_hours': float(tutorial.hours) - float(teacher.tutorial_hours)
            })
    return jsonify(list_tutorial)


@app.route('/teacher_load/<dni>', methods=['GET'])
@app.route('/teacher_load', methods=['GET'])
def get_teacher_load(dni=None):

    if not dni:
        list_teacher = []
        for teacher in Teacher.get_all():
            area = KnowledgeArea.get(teacher.area_cod)
            cover_hours = 0.

            for impart in teacher.group:
                group = Group.get(impart.group_cod, impart.subject_cod, impart.area_cod)
                cover_hours += float(group.hours)

            list_teacher.append({
                'teacher_name': teacher.name,
                'teacher_surnames': teacher.surnames,
                'teacher_dni': teacher.dni,
                'knowledge_area_name': area.name,
                'potential': teacher.potential,
                'cover_hours': cover_hours,
                'unassigned_hours': float(cover_hours) - float(teacher.potential)
            })
        return jsonify(list_teacher)
    else:
        list_group = []
        teacher = Teacher.get(dni)
        if teacher:
            for impart in teacher.group:
                group = Group.get(impart.group_cod, impart.subject_cod, impart.area_cod)
                area = KnowledgeArea.get(impart.area_cod)
                subject = Subject.get(impart.subject_cod)
                list_group.append({
                    'teacher_name': teacher.name,
                    'teacher_surnames': teacher.surnames,
                    'university_degree_name': area.name,
                    'subject_name': subject.name,
                    'subject_course': subject.course,
                    'subject_type': subject.type,
                    'subject_semester': subject.semester,
                    'group_type': group.type,
                    'group_cod': group.group_cod,
                    'assigned_hours': impart.hours
                })
        return jsonify({'teacher_name': teacher.name, 'teacher_surnames': teacher.surnames, 'groups': list_group})


