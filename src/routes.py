from flask import request, jsonify, send_file, make_response
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from src.resources import *
from datetime import *
from functools import wraps
import json

import jwt
import os

'''
   decorator
'''


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


def response(data=None, status=201):
    return make_response(jsonify(data), status)


'''
 API RESTFULL
'''


@app.route('/teacher_load', methods=['GET'])
@token_required
def get_all_teacher_load(user):
    try:
        list_teacher = []
        for teacher in Teacher.all():
            dict_teacher = build_dict(teacher=teacher, area=teacher.knowledgeArea)
            dict_teacher.update(group_cover_hours(teacher))
            list_teacher.append(dict_teacher)

        return response(list_teacher)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher_load/<dni>', methods=['GET'])
@token_required
def get_teacher_load(user, dni=None):
    try:
        list_group, teacher = [], Teacher.get(dni)
        if not teacher:
            return response({'message': 'Techer not found'}, 404)

        for impart in teacher.group:
            output = build_dict(teacher=teacher, impart=impart, group=impart.group, subject=impart.group.subject,
                                area=impart.group.subject.knowledgeArea,
                                university=impart.group.subject.university_degree)
            output.update(teacher_cover_hours(impart.group))
            list_group.append(output)
        return response({'teacher_name': teacher.name, 'teacher_surnames': teacher.surnames, 'groups': list_group})
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher_load', methods=['POST'])
@token_required
def create_teachers_loads(user):
    data = request.get_json()
    if not data:
        return response({'message': 'Data not found'}, 401)
    if not user.teacher:
        return response({'message': 'User is not teacher'}, 401)

    try:
        group = Group.get(data['area_cod'], data['subject_cod'], data['group_cod'])
        if group:
            impart = Impart(group, user.teacher, str(data['impart_hours']))
            if impart.save():
                return response({'message': impart.to_dict()})
        return response({'message': 'Group not found'}, 404)

    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher_load/<area_cod>/<subject_cod>/<group_cod>', methods=['DELETE'])
@token_required
def delete_teacher_load(user, area_cod=None, subject_cod=None, group_cod=None):
    try:
        if not area_cod or not subject_cod or not group_cod:
            return response({'message': 'Param not found'}, 404)

        impart = Impart.get(group_cod, subject_cod, area_cod, user.teacher.dni)
        if impart.delete():
            return response({'message': 'Teacher load deleted successfully'}, 201)

        return response({'message': 'Teacher load delete error'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher_load/<area_cod>/<subject_cod>/<group_cod>/<teacher_dni>', methods=['PUT'])
@app.route('/teacher_load/<area_cod>/<subject_cod>/<group_cod>', methods=['PUT'])
@token_required
def update_teacher_load(user, area_cod=None, subject_cod=None, group_cod=None, teacher_dni=None):
    try:
        data = request.get_json()
        if not area_cod and not subject_cod and not group_cod and not data:
            return response({'message': 'Param not found'}, 404)

        dni = teacher_dni if teacher_dni else user.teacher.dni
        impart = Impart.get(area_cod=area_cod, subject_cod=subject_cod, group_cod=group_cod, teacher_dni=dni)
        impart.update(data)
        if impart.save():
            return response({'message': 'Teacher load update successfully'})
        return response({'message': 'Teacher load update error'}, 404)

    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher_load/request', methods=['GET'])
def get_teacher_request():
    try:
        return response([build_dict(impart=impart, teacher=impart.teacher) for impart in Impart.all()], 201)
    except Exception as ex:
        return response({'message': ex}, 500)


'''
    GROUP
'''


@app.route('/groups', methods=['GET'])
@token_required
def get_groups(user):
    try:
        subject_list = []
        for group in Group.all():
            group_dict = build_dict(subject=group.subject, group=group, area=group.subject.knowledgeArea,
                                    university=group.subject.university_degree)
            group_dict.update(teacher_cover_hours(group))
            subject_list.append(group_dict)
        return response(subject_list)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/group/<area_cod>/<subject_cod>/<group_cod>', methods=['GET'])
@token_required
def get_one_group(current_user, area_cod=None, subject_cod=None, group_cod=None):
    try:
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
            return response(output_request)

        return response({'error': 'Not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


'''
    SUBJECT
'''


@app.route('/subjects', methods=['GET'])
@token_required
def get_subjects(current_user):
    try:
        return response({'subject': [build_dict(university=subject.university_degree, area=subject.knowledgeArea,
                                                subject=subject) for subject in Subject.all()]})
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subject/<subject_cod>/<area_cod>', methods=['GET'])
@token_required
def get_subject(user, subject_cod=None, area_cod=None):

    if not area_cod and not subject_cod:
        return response({'message': 'Param not found'}, 404)

    sub = Subject.get(subject_cod, area_cod)
    if sub:
        return response(sub.to_dict())
    return response({'message': 'Subject not found'}, 404)


@app.route('/subject/pda', methods=['GET'])
@token_required
def get_all_pda(current_user):
    try:
        list_pda, output = [], {}
        for pda in PDA.all():
            subject = pda.subject
            if subject:
                pda_dict = build_dict(pda=pda, university=subject.university_degree, subject=pda.subject,
                                      teacher=subject.coordinator, area=pda.subject.knowledgeArea)
                list_pda.append(pda_dict)
        return response(list_pda, 201)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subject/coordinator', methods=['GET'])
@token_required
def get_coordinators(user):
    try:
        return response([build_dict(subject=sub, university=sub.university_degree, area=sub.knowledgeArea,
                                    teacher=sub.coordinator) for sub in Subject.all()])
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subject/coordinator/<dni>', methods=['GET'])
@token_required
def get_coordinator(user, dni=None):
    try:
        if not dni:
            return response({'message': 'Param not found'}, 404)

        subjects = Subject.query.filter_by(coordinator_dni=dni).all()
        return response([build_dict(subject=sub, university=sub.university_degree, area=sub.knowledgeArea)
                         for sub in subjects])
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subject/coordinator/<dni>', methods=['POST'])
@token_required
def create_coordinator(user, dni=None):
    try:
        data = request.get_json()
        if not data and not dni:
            return response({'message': 'Param not found'}, 404)

        for sub in Subject.query.filter_by(coordinator_dni=dni).all():
            sub.coordinator = None
            sub.save()

        teacher = Teacher.get(dni)
        if teacher:
            message = []
            for value in data:
                subject = Subject.get(value['subject_cod'], value['area_cod'])
                if subject:
                    subject.coordinator = teacher
                    if subject.save():
                        message.append({'subject': subject.to_dict()})
            return response(message)

        return response({'message': 'Have had any errors'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subject/responsible', methods=['GET'])
@token_required
def get_responsibles(user):
    try:
        return response([build_dict(subject=sub, university=sub.university_degree, area=sub.knowledgeArea,
                                    teacher=sub.responsible) for sub in Subject.all()])
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subject/responsible/<dni>', methods=['GET'])
@token_required
def get_responsible(user, dni=None):

    try:
        if not dni:
            return response({'message': 'Param not found'}, 404)

        subjects = Subject.query.filter_by(responsible_dni=dni).all()
        return response([build_dict(subject=sub, university=sub.university_degree, area=sub.knowledgeArea)
                         for sub in subjects])
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subject/responsible/<dni>', methods=['POST'])
@token_required
def create_responsible(user, dni=None):
    try:
        data = request.get_json()
        if not data and not dni:
            return response({'message': 'Param not found'}, 404)

        for sub in Subject.query.filter_by(responsible_dni=dni).all():
            sub.responsible = None
            sub.save()

        teacher = Teacher.get(dni)
        if teacher:
            message = []
            for value in data:
                subject = Subject.get(value['subject_cod'], value['area_cod'])
                if subject:
                    subject.responsible = teacher
                    if subject.save():
                        message.append({'subject': subject.to_dict()})

            return response(message)
        return response({'message': 'Have had any errors'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)

'''
    USER
'''


@app.route('/login', methods=['POST'])
def login():
    try:
        auth = request.get_json()

        if not auth or not auth['username'] or not auth['password']:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        user = User.get(username=auth['username'])
        if not user:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

        if check_password_hash(user.password, auth['password']):
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow() + timedelta(minutes=59)},
                               app.config['SECRET_KEY'])

            user_dict = user.to_dict()
            if user.teacher:
                teacher_dict = build_dict(teacher=user.teacher, area=user.teacher.knowledgeArea)
                user_dict.update(teacher_dict)

            return response({'token': token.decode('UTF-8'), 'user': user_dict})

        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    except Exception as e:
        return response({'message': e}, 500)


@app.route('/currentUser', methods=['GET'])
@token_required
def get_currentuser(user):
    try:
        return response(user.to_dict(), 201)
    except Exception as e:
        return response({'message': e}, 500)

@app.route('/user/<username>', methods=['GET'])
@token_required
def get_user(user, username=None):
    u = User.get(username=username)
    if u:
        if u.teacher:
            return response(build_dict(user=u, teacher=u.teacher))
        else:
            return response(u.to_dict())

    return response({'message': 'User not found'}, 400)


@app.route('/user/<username>', methods=['DELETE'])
@token_required
def remove_user(user, username=None):
    u = User.get(username=username)
    if not u or u.username in 'admin':
        return response({'message': 'User not found'}, 404)

    if u.delete():
        return response({'message': 'User successfully removed'})

    return response({'message': 'User not could delete'}, 401)


@app.route('/user/<username>', methods=['PUT'])
@token_required
def update_user(user, username=None):
    u = User.get(username=username)
    data = request.get_json()
    if not u or not data:
        return response({'message': 'User not found'}, 404)

    u.update(data)
    if u.save():
        return response({'message': 'User successfully update'})

    return response({'message': 'User not could update'}, 404)


@app.route('/users', methods=['GET'])
def get_users():
    users = User.all()
    if users:
        return response([build_dict(user=user, teacher=user.teacher) for user in users])
    return response({'message': 'Users not found'}, 404)


@app.route('/sign-in', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if data and contains_keys(['username', 'password', 'admin'], data.keys()):
            user = User.get(username=data['username'])
            if user:
                return response({'message': 'User already exists'}, 301)
            user = User(data['username'], generate_password(data), data['admin'], public_id())
            if 'dni' in data.keys() and data['dni']:
                teacher = Teacher.get(data['dni'])
                if teacher:
                    user.teacher = teacher
                    if user.save():
                        return response({'message': 'User and Teacher have been created!'})
                    else:
                        return response({'message': 'User and Teacher could not have been created!'}, 401)

                if contains_keys(['name', 'surnames', 'potential', 'tutorial_hours', 'area_cod'], data.keys()):
                    area = KnowledgeArea.get(data['area_cod'])
                    if not area:
                        return response({'message': 'Knowledge Area could not been find'}, 404)

                    teacher = Teacher(data['dni'], data['name'], data['surnames'], data['potential'],
                                      data['tutorial_hours']
                                      , area)
                    user.teacher = teacher
                    if teacher.save():
                        return response({'message': 'Teacher created'})
            else:
                if user.save():
                    return response({'message': 'User created'})

        return response({'message': 'User could not have been created!'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


'''
    TEACHER
'''


@app.route('/teachers', methods=['GET'])
def get_teachers():
    try:
        return response([teacher.to_dict() for teacher in Teacher.all()], 201)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher/<dni>', methods=['GET'])
@token_required
def get_teacher(user, dni=None):
    try:
        if dni:
            teacher = Teacher.get(dni)
            if teacher:
                return response(teacher.to_dict())
        return response({'message': 'Data not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher/<dni>', methods=['PUT'])
@token_required
def update_teacher(user, dni=None):
    try:
        data=request.get_json()
        if not data and not dni:
            return response({'message': 'Data not found'}, 404)

        teacher = Teacher.get(dni)
        if teacher:
            teacher.update(data)
            if teacher.save():
                return response({'message': 'User successfully update'})

        return response({'message': 'User not could update'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher/<dni>', methods=['DELETE'])
@token_required
def remove_teacher(user, dni=None):
    try:
        if not dni:
            return response({'message': 'Teacher not found'}, 404)

        if Teacher.get(dni).delete():
            return response({'message': 'Teacher successfully removed'})

        return response({'message': 'Teacher not could delete'}, 401)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher/tutorial', methods=['GET'])
@token_required
def get_tutorials(current_user):
    try:
        tutorials = []
        for teacher in Teacher.all():
            if teacher.tutorial:
                out = build_dict(teacher=teacher, tutorial=teacher.tutorial, area=teacher.knowledgeArea)
                if teacher.tutorial.hours and teacher.tutorial_hours:
                    out.update({'cover_hours': float(teacher.tutorial.hours),
                                'unassigned_hours': float(teacher.tutorial.hours) - float(teacher.tutorial_hours)})
                tutorials.append(out)
        return response(tutorials)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher/tutorial/<dni>', methods=['GET'])
@token_required
def get_teacher_tutorial(current_user, dni=None):
    try:
        teacher = Teacher.get(dni)
        if teacher and teacher.tutorial:
            return response(teacher.tutorial.to_dict())
        return response({'message': 'Data not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher/tutorial/<teacher_dni>', methods=['POST'])
@token_required
def create_tutorial(current_user, teacher_dni):
    try:
        data = request.get_json()
        if data and teacher_dni:

            teacher = Teacher.get(teacher_dni)
            if not teacher:
                return response({'message': 'Teacher not found'}, 404)

            if teacher.tutorial:
                teacher.tutorial.delete()

            tutorial = Tutorial(first_semester=json.dumps(data['first_semester']),
                                second_semester=json.dumps(data['second_semester']), hours=data['hours'])
            teacher.tutorial = tutorial
            if teacher.save():
                return response({'message': 'Tutorial has been saved'})

        return response({'message': 'Data not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


'''
   DATA BASES
'''


@app.route('/database', methods=['POST'])
@token_required
def upload_database(user):
    try:
        if user.isAdmin:
            # check if the post request has the file part
            if 'file' not in request.files:
                return response({'message': 'File not found'}, 404)

            request_file = request.files['file']
            if request_file and allowed_file(request_file.filename):
                filename = secure_filename(request_file.filename)
                filename_dir = Resource.join_file(filename)
                request_file.save(filename_dir)

                data_file = Resource.openxlsx(filename_dir)  # return value dictionary with column name
                data_saved = import_schema(data_file)
                os.remove(filename_dir)

                return response({'message': data_saved})
            else:
                return response({'message': 'File not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/database', methods=['GET'])
def download_database():
    try:
        return send_file(export_schema(), cache_timeout=-1)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/database', methods=['DELETE'])
@token_required
def delete_database(user):
    try:
        if not user.isAdmin:
            return response({'message': 'Unauthorized User'}, 404)

        areas = [area.delete() for area in KnowledgeArea.all()]
        message = {'knowledgeArea': len(KnowledgeArea.all()),
                   'subject': len(Subject.all()),
                   'universityDegree': len(UniversityDegree.all()),
                   'teacher': len(Teacher.all()),
                   'pda': len(PDA.all()),
                   'tutorial': len(Tutorial.all())}
        return response({'message': message})
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/database/teacher', methods=['POST'])
@token_required
def upload_teacher(user):
    try:
        if 'file' not in request.files:
            return response({'message': 'File not found'}, 404)

        request_file = request.files['file']
        if request_file and allowed_file(request_file.filename):
            filename = secure_filename(request_file.filename)
            filename = Resource.join_file(filename)
            request_file.save(filename)

            data_file = Resource.openxlsx(filename)  # return value dictionary with column name
            message = import_teacher(data_file)
            os.remove(filename)
            return response({'message': message})

        else:
            return response({'message': 'File not found'}, 404)

    except Exception as e:
        return response({'message': e}, 500)


@app.route('/database/pda', methods=['POST'])
@token_required
def upload_pda(user):
    try:
        if 'file' not in request.files:
            return response({'message': 'Data not found'}, 404)

        request_file = request.files['file']
        if request_file and allowed_file(request_file.filename):
            filename = secure_filename(request_file.filename)
            filename = Resource.join_file(filename)
            request_file.save(filename)

            data_file = Resource.openxlsx(filename)  # return value dictionary with column name
            message_pda = import_pda(data_file)
            os.remove(filename)

            if 'count' in message_pda and message_pda['count']:
                return response({'message': message_pda})
            return response({'message': message_pda}, 404)
        else:
            return response({'message': 'Data not found'}, 404)
    except Exception as e:
        return response({'error': e}, 500)