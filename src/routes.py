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
        <p>Rutas disponibles</p>
        <ul>
            <li><a href="upload_database">Cargar base de datos</a></li>
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
        #group = Group.get('17', '40304', '35')
        print(group)
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
                "group_cod": group.area_cod,
                "group_type": group.type,
                "group_hours": group.hours,
                "teacher": teacher
            })
    return jsonify({})

@app.route('/pda/', methods=['GET'])
@app.route('/pda', methods=['GET'])
def get_pda():
    listPDA = []
    PDAs = PDA.getAll()
    for pda in PDAs:
        sub = Subject.get(pda.subject_cod)
        if sub:
            university_degree = UniversityDegree.get(sub.university_degree_cod)
            listCoor = sub.teacher
            for coor in listCoor:
                if coor.subject_coor:
                    coor_subject = Teacher.get(coor.teacher_dni)
                    area = KnowledgeArea.get(coor_subject.area_cod)

            listPDA.append({
                'id': pda.id,
                'status': pda.status,
                'observations': pda.observations,
                'university_degree_name': university_degree.name,
                'university_degree_cod': university_degree.university_degree_cod,
                'subject_name': sub.name,
                'subject_cod': sub.subject_cod,
                'knowledge_area_name': area.name,
                'knowledge_area_cod': area.area_cod,
                'teacher_name': coor_subject.name,
                'teacher_surnames': coor_subject.surnames,
                'teacher_dni': coor_subject.dni
            })

    return jsonify(listPDA)


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
