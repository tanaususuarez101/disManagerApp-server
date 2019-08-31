from flask import request, jsonify, Response, send_file, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from src.resources import *
from datetime import *
from functools import wraps
import json

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
def get_all_teacher_load(user):
    list_teacher = []
    for teacher in Teacher.all():
        cover_hours = group_cover_hours(teacher.group)
        dict_teacher = build_dict(teacher=teacher, area=teacher.knowledgeArea)
        dict_teacher.update({'cover_hours': cover_hours})
        dict_teacher.update({'unassigned_hours': float(cover_hours) - float(teacher.potential)})
        list_teacher.append(dict_teacher)
    return make_response(jsonify(list_teacher), 201)


@app.route('/teacher_load/<dni>', methods=['GET'])
@token_required
def get_teacher_load(user, dni=None):
    list_group, teacher = [], Teacher.get(dni)
    if not teacher:
        return make_response(jsonify({'message': 'Techer not found'}), 404)

    for impart in teacher.group:
        output = build_dict(teacher=teacher, impart=impart, group=impart.group, subject=impart.group.subject,
                            area=impart.group.subject.knowledgeArea, university=impart.group.subject.university_degree)
        output.update(teacher_cover_hours(impart.group))
        list_group.append(output)
    return make_response(jsonify({'teacher_name': teacher.name, 'teacher_surnames': teacher.surnames,
                                  'groups': list_group}), 201)


@app.route('/teacher_load', methods=['POST'])
@token_required
def create_teachers_loads(user):
    data = request.get_json()
    if not data:
        return make_response(jsonify({'message': 'Data not found'}), 401)

    try:
        for item in data:
            group = Group.get(item['area_cod'], item['subject_cod'], item['group_cod'])
            if group:
                impart = Impart(group, user.teacher, item['impart_hours'])
                impart.save()

        return make_response(jsonify({'message': 'Data saved'}), 201)

    except:
        return make_response(jsonify({'message': 'There has been some error'}), 501)


@app.route('/teacher_load/<area_cod>/<subject_cod>/<group_cod>', methods=['DELETE'])
@token_required
def delete_teacher_load(user, area_cod=None, subject_cod=None, group_cod=None):
    if not area_cod and not subject_cod and not group_cod:
        return make_response(jsonify({'message': 'Param not found'}), 404)

    group, teacher = Group.get(area_cod, subject_cod, group_cod), user.teacher
    impart = Impart.get(group, teacher)
    if impart:
        impart.delete()
        return make_response(jsonify({'message': 'Teacher load deleted successfully'}), 201)

    return make_response(jsonify({'message': 'Teacher load delete error'}), 404)


@app.route('/teacher_load/<area_cod>/<subject_cod>/<group_cod>/<teacher_dni>', methods=['PUT'])
@app.route('/teacher_load/<area_cod>/<subject_cod>/<group_cod>', methods=['PUT'])
@token_required
def update_teacher_load(user, area_cod=None, subject_cod=None, group_cod=None, teacher_dni=None):

    data = request.get_json()
    if not area_cod and not subject_cod and not group_cod and not data:
        return make_response(jsonify({'message': 'Param not found'}), 404)

    dni = teacher_dni if teacher_dni else user.teacher.dni
    impart = Impart.get(area_cod=area_cod, subject_cod=subject_cod, group_cod=group_cod, teacher_dni=dni)
    impart.update(data)
    if impart.save():
        return make_response(jsonify({'message': 'Teacher load update successfully'}), 201)

    return make_response(jsonify({'message': 'Teacher load update error'}), 404)


@app.route('/teacher_load/request', methods=['GET'])
def get_teacher_request():
    return make_response(jsonify([build_dict(impart=impart, teacher=impart.teacher) for impart in Impart.all()]), 201)

'''
@app.route('/teacher_load/request/<area_cod>/<subject_cod>/<group_cod>', methods=['PUT'])
def update_teacher_request():
    data = request.get_json()
    if not data:
        return make_response(jsonify({'message': 'data not found'}), 404)

    group = Group.get(data['area_cod'], data['subject_cod'], data['group_cod'])
    teacher = Teacher.get(data['teacher_dni'])

    if not group or not teacher:
        return make_response(jsonify({'message': 'data not found'}), 404)

    impart = Impart.get(group=group, teacher=teacher)
    impart.update(data)

    if impart.save():
        return make_response(jsonify({'message': 'request updated'}), 201)

    return make_response(jsonify({'message': 'request updated'}), 201)
'''

'''
    GROUP
'''


@app.route('/groups', methods=['GET'])
@token_required
def get_groups(user):
    subject_list = []
    for group in Group.all():
        group_dict = build_dict(subject=group.subject, group=group, area=group.subject.knowledgeArea,
                                university=group.subject.university_degree)
        group_dict.update(teacher_cover_hours(group))
        subject_list.append(group_dict)
    return make_response(jsonify(subject_list), 201)


@app.route('/groups/available', methods=['GET'])
@token_required
def get_groups_available(user):
    teacher = user.teacher
    areas_codes = [venia.area_cod for venia in teacher.veniaI if venia.approved]
    subjects = [{venia.area_cod, venia.subject_cod} for venia in teacher.veniaII]

    subject_list = []
    for group in Group.all():
        if group.area_cod in areas_codes or {group.area_cod, group.subject_cod} in subjects or teacher.area_cod \
                in group.area_cod:
            group_dict = build_dict(subject=group.subject, group=group, area=group.subject.knowledgeArea,
                                    university=group.subject.university_degree)
            group_dict.update(teacher_cover_hours(group))
            subject_list.append(group_dict)

    return make_response(jsonify(subject_list), 201)


@app.route('/group/<area_cod>/<subject_cod>/<group_cod>', methods=['GET'])
@token_required
def get_one_group(current_user, area_cod=None, subject_cod=None, group_cod=None):
    group = Group.get(area_cod, subject_cod, group_cod)
    if group:
        output_teacher, teacher, cover_hour = {}, [], 0
        for impart in group.teacher:
            cover_hour += float(impart.hours)
            output_teacher = build_dict(teacher=impart.teacher, impart=impart)
            output_teacher.update(teacher_cover_hours(impart.group))
            teacher.append(output_teacher)

        output_request = build_dict(subject=group.subject, university=group.subject.university_degree,
                                    area=group.subject.knowledgeArea, group=group)
        output_request.update({'teacher': teacher})
        return make_response(jsonify(output_request), 201)

    return make_response(jsonify({'error': 'Not found'}), 404)


'''
    SUBJECT
'''


@app.route('/subjects', methods=['GET'])
@token_required
def get_subjects(current_user):
    # TODO - Utilizar Resource build dict
    output = []
    for subject in Subject.all():
        titulacion = subject.university_degree
        area = subject.knowledgeArea
        subject = subject.to_dict()
        subject.update(titulacion.to_dict())
        subject.update(area.to_dict())
        output.append(subject)

    return make_response(jsonify({'subject': output}), 201)


@app.route('/subject/pda', methods=['GET'])
@token_required
def get_all_pda(current_user):
    list_pda, output = [], {}
    for pda in PDA.all():
        subject = pda.subject
        if subject:
            pda_dict = build_dict(pda=pda, university=subject.university_degree, subject=pda.subject,
                                  teacher=subject.coordinator, area=pda.subject.knowledgeArea)
            list_pda.append(pda_dict)
            print(list_pda)

    return make_response(jsonify(list_pda), 201)


@app.route('/subject/coordinator', methods=['GET'])
@token_required
def get_coordinator(user):
    coordinator_list = []

    for subject in Subject.all():
        coordinator_dict = build_dict(subject=subject, university=subject.university_degree, area=subject.knowledgeArea,
                                      teacher=subject.coordinator)
        coordinator_list.append(coordinator_dict)
    return make_response(jsonify(coordinator_list), 201)


@app.route('/subject/responsible', methods=['GET'])
@token_required
def get_responsible(user):
    responsible_list = []

    for subject in Subject.all():
        responsible_dict = build_dict(subject=subject, university=subject.university_degree, area=subject.knowledgeArea,
                                      teacher=subject.responsible)
        responsible_list.append(responsible_dict)

    return make_response(jsonify(responsible_list), 201)


@app.route('/subject/coordinator', methods=['POST'])
@token_required
def create_coordinator(user):
    data = request.get_json()
    if data and user.teacher:

        teacher = user.teacher
        for sub in Subject.query.filter_by(coordinator_dni=teacher.dni).all():
            sub.coordinator = None
            sub.save()

        for sub in Subject.query.filter_by(responsible_dni=teacher.dni).all():
            sub.responsible = None
            sub.save()

        data_infor = []
        if 'coordinator' in data.keys():
            for obj in data['coordinator']:
                if contains_keys(['subject_cod', 'area_cod'], obj.keys()):
                    subject = Subject.get(obj['subject_cod'], obj['area_cod'])
                    if subject.coordinator and subject.coordinator not in teacher:
                        data_infor.append({'subject_cod': obj['subject_cod'], 'area_cod': obj['area_cod'],
                                           'message': 'Error replacing coordinator'})
                    subject.coordinator = teacher
                    if subject.save():
                        data_infor.append({'subject_cod': obj['subject_cod'], 'area_cod': obj['area_cod'],
                                           'message': 'Added new coordinator'})

        if 'responsible' in data.keys():

            for obj in data['responsible']:
                if contains_keys(['subject_cod', 'area_cod'], obj.keys()):
                    subject = Subject.get(obj['subject_cod'], obj['area_cod'])
                    if subject.responsible and subject.responsible not in teacher:
                        data_infor.append({'subject_cod': obj['subject_cod'], 'area_cod': obj['area_cod'],
                                           'message': 'Error replacing coordinator'})
                    subject.responsible = teacher
                    if subject.save():
                        data_infor.append({'subject_cod': obj['subject_cod'], 'area_cod': obj['area_cod'],
                                           'message': 'Added new responsible'})

        return make_response(jsonify(data_infor), 201)

    return make_response(jsonify({'message': 'Have had any errors'}), 404)


@app.route('/subjects/area/<area_cod>')
@token_required
def get_subjects_area(user, area_cod=None):
    return make_response(jsonify([subject.to_dict() for subject in Subject.query.filter_by(area_cod=area_cod).all()]))


'''
    USER
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
            teacher_dict = build_dict(teacher=user.teacher, area=user.teacher.knowledgeArea)
            user_dict.update(teacher_dict)

        return make_response(jsonify({'token': token.decode('UTF-8'), 'user': user_dict}))

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/currentUser', methods=['GET'])
@token_required
def get_currentuser(user):
    try:
        return make_response(jsonify(user.to_dict()), 201)
    except Exception as e:
        return make_response(jsonify({'message': 'Server error internal'}), 500)


@app.route('/currentUser', methods=['PUT'])
@token_required
def update_currentuser(current_user):
    data = request.get_json()
    if data:
        current_user.password = generate_password_hash(data['password'], method='sha256')
        if current_user.save():
            return make_response(jsonify({'message': 'password success saved'}), 201)
        else:
            return make_response(jsonify({'message': 'data could not update'}), 401)
    else:
        return make_response(jsonify({'message': 'no data found'}), 401)


@app.route('/user/<username>', methods=['GET'])
@token_required
def get_user(user, username=None):
    u = User.get(username=username)
    if u:
        if u.teacher:
            return make_response(jsonify(build_dict(user=u, teacher=u.teacher)), 201)
        else:
            return make_response(jsonify(build_dict(user=u)), 201)

    return make_response(jsonify({'message': 'User not found'}), 201)


@app.route('/user/<username>', methods=['DELETE'])
@token_required
def remove_user(user, username=None):
    u = User.get(username=username)
    if not u or u.username in 'test':
        return make_response(jsonify({'message': 'User not found'}), 404)

    if u.delete():
        return make_response(jsonify({'message': 'User successfully removed'}), 201)

    return make_response(jsonify({'message': 'User not could delete'}), 401)


@app.route('/user/<username>', methods=['PUT'])
@token_required
def update_user(user, username=None):
    u = User.get(username=username)
    if not u or not request.get_json():
        return make_response(jsonify({'message': 'User not found'}), 404)

    u.update(request.get_json())
    if u.save():
        return make_response(jsonify({'message': 'User successfully update'}), 201)

    return make_response(jsonify({'message': 'User not could update'}), 404)


@app.route('/users', methods=['GET'])
def get_users():
    users = User.all()
    if users:
        return make_response(jsonify([build_dict(user=user, teacher=user.teacher) for user in users]), 201)
    return make_response(jsonify({'message': 'Users not found'}), 404)


@app.route('/sign-in', methods=['POST'])
def create_user():
    data = request.get_json()

    if data and contains_keys(['username', 'password', 'admin'], data.keys()):
        user = User.get(username=data['username'])
        if user:
            return make_response(jsonify({'message': 'User already exists'}), 301)

        hashed_password = generate_password_hash(data['password'], method='sha256')
        user = User(data['username'], hashed_password, data['admin'], str(uuid.uuid4()))

        if 'dni' in data.keys() and data['dni']:
            teacher = Teacher.get(data['dni'])
            if teacher:
                user.teacher = teacher
                if user.save():
                    return make_response(jsonify({'message': 'User and Teacher have been created!'}), 201)
                else:
                    return make_response(jsonify({'message': 'User and Teacher could not have been created!'}), 401)

            if contains_keys(['name', 'surnames', 'potential', 'tutorial_hours', 'area_cod'], data.keys()):
                area = KnowledgeArea.get(data['area_cod'])
                if not area:
                    return make_response(jsonify({'message': 'Knowledge Area could not been find'}), 404)

                teacher = Teacher(data['dni'], data['name'], data['surnames'], data['potential'], data['tutorial_hours']
                                  , area)
                user.teacher = teacher
                if teacher.save():
                    return make_response(jsonify({'message': 'Teacher created'}), 201)
        else:
            if user.save():
                return make_response(jsonify({'message': 'User created'}), 201)

    return make_response(jsonify({'message': 'User could not have been created!'}), 404)


'''
    TEACHER
'''


@app.route('/teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.all()
    if teachers:
        return make_response(jsonify([teacher.to_dict() for teacher in teachers]), 201)
    return make_response(jsonify({'message': 'Teachers not found'}), 404)


@app.route('/teacher/<dni>', methods=['GET'])
@token_required
def get_teacher(user, dni=None):
    teacher = Teacher.get(dni)
    if not teacher:
        return make_response(jsonify({'message': 'Teacher not found'}), 404)
    return make_response(jsonify(teacher.to_dict()), 201)


@app.route('/teacher/<dni>', methods=['PUT'])
@token_required
def update_teacher(user, dni=None):
    teacher = Teacher.get(dni)

    if not teacher or not request.get_json():
        return make_response(jsonify({'message': 'User not found'}), 404)

    teacher.update(request.get_json())
    if teacher.save():
        return make_response(jsonify({'message': 'User successfully update'}), 201)

    return make_response(jsonify({'message': 'User not could update'}), 404)


@app.route('/teacher/<dni>', methods=['DELETE'])
@token_required
def remove_teacher(user, dni=None):
    teacher = Teacher.get(dni)
    if not teacher:
        return make_response(jsonify({'message': 'Teacher not found'}), 404)

    if teacher.delete():
        return make_response(jsonify({'message': 'Teacher successfully removed'}), 201)

    return make_response(jsonify({'message': 'Teacher not could delete'}), 401)


@app.route('/teacher/tutorial', methods=['GET'])
@token_required
def get_tutorials(current_user):
    list_tutorial, output = [], {}
    for teacher in Teacher.all():
        if teacher.tutorial:
            output = build_dict(teacher=teacher, tutorial=teacher.tutorial, area=teacher.knowledgeArea)
            if teacher.tutorial.hours and teacher.tutorial_hours:
                output.update({'cover_hours': float(teacher.tutorial.hours)})
                output.update({'unassigned_hours': float(teacher.tutorial.hours) - float(teacher.tutorial_hours)})
            list_tutorial.append(output)
    return make_response(jsonify(list_tutorial), 201)


@app.route('/teacher/tutorial/<dni>', methods=['GET'])
@token_required
def get_teacher_tutorial(current_user, dni=None):
    teacher = Teacher.get(dni)
    return make_response(jsonify(teacher.tutorial.to_dict()), 201) if teacher else \
        make_response(jsonify({'message': 'Data not found'}), 404)


@app.route('/teacher/tutorial', methods=['POST'])
@token_required
def create_tutorial(current_user):
    data = request.get_json()

    if data:
        if not contains_keys(['first_semester', 'second_semester', 'hours'], data.keys()):
            return make_response(jsonify({'message': 'data not found'}), 404)

        if not current_user.teacher_dni:
            return make_response(jsonify({'message': 'User is not teacher'}), 404)

        teacher = Teacher.get(current_user.teacher_dni)
        if not teacher:
            return make_response(jsonify({'message': 'Teacher not found'}), 404)

        if teacher.tutorial:
            teacher.tutorial.delete()

        teacher.tutorial = Tutorial(first_semester=json.dumps(data['first_semester']),
                                    second_semester=json.dumps(data['second_semester']),
                                    hours=data['hours'])
        if teacher.save():
            return make_response(jsonify({'message': 'Tutorial has been saved'}), 201)

    return make_response(jsonify({'message': 'Error saved data'}), 201)


@app.route('/teacher/coordinator/<dni>', methods=['GET'])
@token_required
def get_teacher_coordinator(user, dni=None):
    if dni:
        subject_all = Subject.query.filter_by(coordinator_dni=dni).all()
        responsible_list = [subject.to_dict() for subject in subject_all]
        return make_response(jsonify(responsible_list), 201)
    return make_response(jsonify({}), 404)


@app.route('/teacher/responsible/<dni>', methods=['GET'])
@token_required
def get_teacher_responsible(user, dni=None):
    if dni:
        subject_all = Subject.query.filter_by(responsible_dni=dni).all()
        resp_subject = [subject.to_dict() for subject in subject_all]
        return make_response(jsonify(resp_subject), 201)
    return make_response(jsonify({}), 404)


'''
    API ADMINISTRATOR
'''


@app.route('/upload_database', methods=['POST'])
def upload_database():
    if request.method == 'POST':
        # check if the post request has the file part
        # try:
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
            os.remove(filename_dir)

            return make_response(jsonify(data_saved), 200)
        else:
            return Response('File not found', status=404)


@app.route('/upload_teacher', methods=['POST'])
def upload_teacher():
    if request.method == 'POST':
        # check if the post request has the file part
        try:
            if 'file' not in request.files:
                return make_response(jsonify({'message': 'File not found'}), 404)

            request_file = request.files['file']
            if request_file and allowed_file(request_file.filename):
                filename = secure_filename(request_file.filename)
                filename_dir = os.path.join(UPLOADS_DIR, filename)
                request_file.save(filename_dir)

                data_file = Resource.openxlsx(filename_dir)  # return value dictionary with column name
                Resource.import_teacher(data_file)
                os.remove(filename_dir)

                return make_response(jsonify({'message': 'List teacher saved'}), 201)
            else:
                return make_response(jsonify({'message': 'File not found'}), 404)
        except Exception as error:
            return make_response(jsonify({'message': 'Internal Server Error'}), 500)


@app.route('/upload_pda', methods=['POST'])
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

                return make_response(jsonify({'message': 'saved'}), 201)
            else:
                return make_response(jsonify({'error': 'Not found'}), 404)
        except Exception as error:
            print(error)
            return make_response(jsonify({'error': 'Internal server error'}), 500)


@app.route('/download_database', methods=['GET'])
def download_database():
    file_data = Resource.backup_database()
    return send_file(file_data)


@app.route('/export_database', methods=['GET'])
def export_database():
    file_data = Resource.export_database()
    return send_file(file_data)


'''
    Knowledge Area
'''


@app.route('/knowledgeAreas', methods=['GET'])
@token_required
def get_knowledgeArea(user):
    return make_response(jsonify([area.to_dict() for area in KnowledgeArea.all()]), 201)


'''
    VENIAS
'''


@app.route('/veniaI', methods=['GET'])
@token_required
def get_all_veniaI(user):
    return make_response(jsonify([venia.to_dict() for venia in VeniaI.all()]), 201)


@app.route('/veniaI/<teacher_dni>', methods=['GET'])
@token_required
def get_veniaI(user, teacher_dni=None):
    teacher = Teacher.get(teacher_dni=teacher_dni)
    if not teacher:
        return make_response(jsonify({'message': 'Teacher not found'}), 201)

    data = [build_dict(veniaI=venia.knowledgeArea) for venia in teacher.veniaI]
    return make_response(jsonify(data), 201)


@app.route('/veniaII', methods=['GET'])
@token_required
def get_all_veniaII(user):
    return make_response(jsonify([venia.to_dict() for venia in VeniaII.all()]), 201)


@app.route('/veniaII/<teacher_dni>', methods=['GET'])
@token_required
def get_veniaII(user, teacher_dni=None):
    teacher = Teacher.get(teacher_dni=teacher_dni)
    if not teacher:
        return make_response(jsonify({'message': 'Teacher not found'}), 201)

    data = [build_dict(veniaII=venia.subject) for venia in teacher.veniaII]
    return make_response(jsonify(data), 201)


@app.route('/veniaI', methods=['POST'])
@token_required
def create_veniaI(user):
    data = request.get_json()
    if data:
        area = KnowledgeArea.get(data['area_cod'])
        if not area:
            return make_response(jsonify({'message': 'Knowledge area not found'}), 404)

        venia = VeniaI(area=area, teacher=user.teacher)
        if venia.save():
            return make_response(jsonify({'message': 'Create venia of type 1'}), 201)
        return make_response(jsonify({'message': 'Venia of type 1 not could created'}), 404)

    return make_response(jsonify({'message': 'Data not found'}), 404)


@app.route('/veniaII', methods=['POST'])
@token_required
def create_veniaII(user):
    data = request.get_json()
    if data:
        subject = Subject.get(subject_cod=data['subject_cod'], area_cod=data['area_cod'])
        if not subject:
            return make_response(jsonify({'message': 'Subject not found'}), 404)

        venia = VeniaII(subject=subject, teacher=user.teacher)
        if venia.save():
            return make_response(jsonify({'message': 'Create venia of type 2'}), 201)

        return make_response(jsonify({'message': 'Venia of type 1 not could created'}), 401)

    return make_response(jsonify({'message': 'Data not found'}), 404)


@app.route('/veniaI/<area_cod>/<teacher_dni>', methods=['PUT'])
@token_required
def update_veniaI(user, area_cod=None, teacher_dni=None):
    if not area_cod and not teacher_dni:
        return make_response(jsonify({'message': 'teacher or Knowlegde Area not found'}), 404)

    impart = VeniaI.get(area_cod=area_cod, teacher_dni=teacher_dni)
    impart.update(request.get_json())
    if impart.save():
        return make_response(jsonify({'message': 'Venia I update successfully'}), 201)

    return make_response(jsonify({'message': 'Venia I not could saved'}), 404)


@app.route('/veniaII/<area_cod>/<subject_cod>/<teacher_dni>', methods=['PUT'])
@token_required
def update_veniaII(user, area_cod=None, subject_cod=None, teacher_dni=None):

    data = request.get_json()
    if not area_cod or not subject_cod or not teacher_dni or not data:
        return make_response(jsonify({'message': 'teacher or subject not found'}), 404)

    impart = VeniaII.get(area_cod=area_cod, subject_cod=subject_cod, teacher_dni=teacher_dni)
    impart.update(data)
    if impart.save():
        return make_response(jsonify({'message': 'Venia II update successfully'}), 201)

    return make_response(jsonify({'message': 'Venia II not could saved'}), 404)
