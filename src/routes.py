from flask import request, jsonify, Response, send_file, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from src.resources import *
from datetime import *
from functools import wraps

import jwt
import os
import uuid


UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = set(['xlsx'])


'''
    PRIVATE METHOD
'''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated



'''
 API RESTFULL
'''


@app.route('/teacher_load', methods=['GET'])
@token_required
def get_all_teacher_load(current_user):
    list_teacher = []
    for teacher in Teacher.all():

        cover_hours = 0.
        for impart in teacher.group:
            group = Group.get(impart.area_cod, impart.subject_cod, impart.group_cod)
            cover_hours += float(group.hours)

        dict_teacher = Resource.build_dict(teacher=teacher, area=teacher.area)
        dict_teacher.update({'cover_hours': cover_hours})
        dict_teacher.update({'unassigned_hours': float(cover_hours) - float(teacher.potential)})
        list_teacher.append(dict_teacher)

    return make_response(jsonify(list_teacher), 201)


@app.route('/teacher_load/<dni>', methods=['GET'])
@token_required
def get_one_teacher_load(current_user, dni=None):

    list_group, teacher = [], Teacher.get(dni)
    if teacher:
        for impart in teacher.group:
            output = Resource.build_dict(teacher=teacher,
                                         impart=impart,
                                         group=impart.group,
                                         subject=impart.group.subject,
                                         area=impart.group.subject.knowledgeArea,
                                         university=impart.group.subject.university_degree)
            output.update(Resource.teacher_cover_hours(impart.group))
            list_group.append(output)

    return make_response(jsonify({'teacher_name': teacher.name, 'teacher_surnames': teacher.surnames, 'groups': list_group}), 201)


@app.route('/teacher_load', methods=['POST'])
@token_required
def post_list_teacher_load(current_user):
    data = request.get_json()
    if not data:
        return make_response(jsonify({'message': 'Data not found'}), 401)

    try:
        for item in data:
            group = Group.get(item['area_cod'], item['subject_cod'], item['group_cod'])
            if group:
                print(item)
                impart = Impart(group, current_user.teacher, item['selected_hours'])
                impart.save()

        return make_response(jsonify({'message': 'Data saved'}), 201)

    except:
        return make_response(jsonify({'message': 'There has been some error'}), 501)


'''
    GROUP
'''


@app.route('/groups', methods=['GET'])
@token_required
def get_all_groups(current_user):

    subject_list = []
    for group in Group.all():
        group_dict = Resource.build_dict(subject=group.subject,
                                         group=group,
                                         area=group.subject.knowledgeArea,
                                         university=group.subject.university_degree)
        group_dict.update(Resource.teacher_cover_hours(group))
        subject_list.append(group_dict)

    return make_response(jsonify(subject_list), 201)


@app.route('/group/<area_cod>/<subject_cod>/<group_cod>', methods=['GET'])
@token_required
def get_one_group(current_user, area_cod=None, subject_cod=None, group_cod=None):

    group = Group.get(area_cod, subject_cod, group_cod)
    if group:
        output_teacher, teacher, cover_hour = {},  [], 0
        for impart in group.teacher:
            print(impart.teacher.name)
            cover_hour += float(impart.hours)
            output_teacher = Resource.build_dict(teacher=impart.teacher, impart=impart)
            output_teacher.update(Resource.teacher_cover_hours(impart.group))
            print(output_teacher)
            '''
            output_teacher['teacher_name'] = impart.teacher.name
            output_teacher['teacher_surname'] = impart.teacher.surnames
            output_teacher['teacher_assigned'] = impart.hours
            '''
            teacher.append(output_teacher)

        output_request = Resource.build_dict(subject=group.subject,
                                             university=group.subject.university_degree,
                                             area=group.subject.knowledgeArea,
                                             group=group)
        output_request.update({'teacher': teacher})
        return make_response(jsonify(output_request), 201)

    return make_response(jsonify({'error': 'Not found'}), 404)


'''
    PDA
'''


@app.route('/pda', methods=['GET'])
@token_required
def get_all_pda(current_user):
    list_pda, output = [], {}
    for pda in PDA.all():
        subject = pda.subject
        if subject:
            pda_dict = Resource.build_dict(pda=pda,
                                           university=subject.university_degree,
                                           subject=pda.subject,
                                           teacher=subject.coordinator,
                                           area=pda.subject.knowledgeArea)
            list_pda.append(pda_dict)
            print(list_pda)

    return make_response(jsonify(list_pda), 201)


'''
    COORDINATOR AND RESPONSIBLE
'''


@app.route('/coordinator', methods=['GET'])
@token_required
def get_all_coordinator(current_user):

    coordinator_list, responsible_list = [], []

    for subject in Subject.all():
        coordinator_dict = Resource.build_dict(subject=subject,
                                               university=subject.university_degree,
                                               area=subject.knowledgeArea,
                                               teacher=subject.coordinator)
        responsible_dict = Resource.build_dict(subject=subject,
                                               university=subject.university_degree,
                                               area=subject.knowledgeArea,
                                               teacher=subject.responsible)
        coordinator_list.append(coordinator_dict)
        responsible_list.append(responsible_dict)

    return make_response(jsonify({'subject': coordinator_list, 'practice': responsible_list}), 201)


'''
    TUTORIAL
'''


@app.route('/tutorial', methods=['GET'])
@token_required
def get_all_tutorials(current_user):

    list_tutorial, output = [], {}
    for teacher in Teacher.all():
        if teacher.tutorial:
            output = Resource.build_dict(teacher=teacher, tutorial=teacher.tutorial, area=teacher.area)
            print(output)
            output.update({'cover_hours': float(teacher.tutorial.hours)})
            output.update({'unassigned_hours': float(teacher.tutorial.hours) - float(teacher.tutorial_hours)})
            list_tutorial.append(output)
    return make_response(jsonify(list_tutorial), 201)


'''
    RESTFUL USER
'''


@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or not auth['username'] or not auth['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.get(username=auth['username'])
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth['password']):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                           app.config['SECRET_KEY'])

        user_dict = user.to_dict()
        if user.teacher:
            teacher_dict = Resource.build_dict(teacher=user.teacher, area=user.teacher.area)
            user_dict.update(teacher_dict)

        return make_response(jsonify({'token': token.decode('UTF-8'), 'user': user_dict}))

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/sign-in', methods=['POST'])
def create_user():
    data = request.get_json()
    user_created = False

    if data and 'username' in data.keys() and 'password' in data.keys() and 'admin' in data.keys():
        user = User.get(username=data['username']) #will search by dni or username
        if not user:
            hashed_password = generate_password_hash(data['password'], method='sha256')
            user = User(data['username'], hashed_password, data['admin'], str(uuid.uuid4()))
            if not user.save():
                return make_response(jsonify({'message': 'Teacher could not have been created!'}))
            user_created = True

    if data and 'dni' in data.keys() and 'name' in data.keys() and 'surnames' in data.keys()\
            and 'potential' in data.keys() and 'tutorial_hours' in data.keys():

            user = User.get(username=data['username'])
            if not user:
                return make_response(jsonify({'message': 'User could not been find'}), 404)

            area = KnowledgeArea.get(data['area_cod'])
            if not area:
                return make_response(jsonify({'message': 'Knowledge Area could not been find'}), 404)

            teacher = Teacher(data['dni'], data['name'], data['surnames'], data['potential'], data['tutorial_hours'],
                              data['area_cod'])
            user.teacher = teacher

            if teacher.save():
                return make_response(jsonify({'message': 'New teacher created'}), 201)

    if user_created:
        return make_response(jsonify({'message': 'New user created'}), 201)

    return make_response(jsonify({'message': 'User could not have been created!'}), 404)


'''
    TEACHER
'''


@app.route('/teacher', methods=['GET'])
@token_required
def get_one_teacher(current_user):
    try:
        return make_response(jsonify(current_user.to_dict()), 201)
    except:
        return make_response(jsonify({}), 500)


@app.route('/teacher', methods=['PUT'])
@token_required
def update_one_teacher(current_user):
    data = request.get_json()
    if data:
        current_user.password = generate_password_hash(data['password'], method='sha256')
        if current_user.save():
            return make_response(jsonify({'message': 'password success saved'}), 201)
        else:
            return make_response(jsonify({'message': 'data could not update'}), 401)
    else:
        return make_response(jsonify({'message': 'no data found'}), 401)


'''
    API ADMINISTRATOR
'''


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
        #try:
            if 'file' not in request.files:
                return ''

            request_file = request.files['file']
            if request_file and allowed_file(request_file.filename):
                filename = secure_filename(request_file.filename)
                filename_dir = Resource.join_file(filename)
                request_file.save(filename_dir)

                data_file = Resource.openxlsx(filename_dir)  # return value dictionary with column name
                entity_file = Resource.file_statistics(data_file)
                data_saved = Resource.import_database(data_file)
                print('Entidades del fichero: {}'.format(data_saved))

                os.remove(filename_dir)

                return make_response(jsonify(data_saved), 200)
            else:
                return Response('File not found', status=404)
       # except Exception as error:
        #    print(error)
         #   return Response('Internal Server Error', status=500)

    return '''
    <!doctype html>
    <title>Subir un nuevo fichero</title>
    <h1>Cargar contenido principal del PDO en la base de datos</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Cargar>
    </form>
    '''


@app.route('/delete_database', methods=['GET', 'POST'])
def delete_database():

    for subject in Subject.all():
        subject.delete()

    for area in KnowledgeArea.all():
        area.delete()

    for university in UniversityDegree.all():
        university.delete()

    for group in Group.all():
        group.delete()

    return make_response(jsonify({}), 200)


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

            return make_response(jsonify({'success': 'data saved'}), 200)
        else:
            return make_response(jsonify({'error': 'Not found'}), 404)

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
                return make_response(jsonify({'error': 'Not found'}), 404)
        except Exception as error:
            print(error)
            return make_response(jsonify({'error': 'Internal server error'}), 500)

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






