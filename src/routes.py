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
            cover = group_cover_hours(teacher.group)
            dict_teacher = build_dict(teacher=teacher, area=teacher.knowledgeArea)
            dict_teacher.update({'cover_hours': cover, 'unassigned_hours': float(cover) - float(teacher.potential)})
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
                                area=impart.group.subject.knowledgeArea, university=impart.group.subject.university_degree)
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

    try:
        for item in data:
            group = Group.get(item['area_cod'], item['subject_cod'], item['group_cod'])
            if group:
                impart = Impart(group, user.teacher, item['impart_hours'])
                impart.save()

        return response({'message': 'Data saved'})
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


@app.route('/groups/available', methods=['GET'])
@token_required
def get_groups_available(user):
    try:
        teacher = user.teacher
        areas_codes = [venia.area_cod for venia in teacher.veniaI if venia.approved]
        subjects = [{venia.area_cod, venia.subject_cod} for venia in teacher.veniaII if venia.approved]

        subject_list = []
        for g in Group.all():
            if g.area_cod in areas_codes or {g.area_cod, g.subject_cod} in subjects or teacher.area_cod in g.area_cod:
                g_dict = build_dict(subject=g.subject, group=g, area=g.subject.knowledgeArea,
                                    university=g.subject.university_degree)
                g_dict.update(teacher_cover_hours(g))
                subject_list.append(g_dict)

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
def get_coordinator(user):
    try:
        return response([build_dict(subject=sub, university=sub.university_degree, area=sub.knowledgeArea,
                        teacher=sub.coordinator) for sub in Subject.all()])
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subject/responsible', methods=['GET'])
@token_required
def get_responsible(user):

    try:
        return response([build_dict(subject=sub, university=sub.university_degree, area=sub.knowledgeArea,
                                    teacher=sub.responsible) for sub in Subject.all()])
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subject/coordinator', methods=['POST'])
@token_required
def create_coordinator(user):
    try:
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

            return response(data_infor)

        return response({'message': 'Have had any errors'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/subjects/area/<area_cod>')
@token_required
def get_subjects_area(user, area_cod=None):
    try:
        return response([subject.to_dict() for subject in Subject.query.filter_by(area_cod=area_cod).all()])
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
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow() + timedelta(minutes=30)},
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


@app.route('/currentUser', methods=['PUT'])
@token_required
def update_currentuser(current_user):
    data = request.get_json()
    if data:
        current_user.password = generate_password_hash(data['password'], method='sha256')
        if current_user.save():
            return response({'message': 'password success saved'})
        else:
            return response({'message': 'data could not update'}, 401)
    else:
        return response({'message': 'no data found'}, 401)


@app.route('/user/<username>', methods=['GET'])
@token_required
def get_user(user, username=None):
    u = User.get(username=username)
    if u:
        if u.teacher:
            return response(build_dict(user=u, teacher=u.teacher))
        else:
            return response(u.to_dict())

    return response({'message': 'User not found'}, 404)


@app.route('/user/<username>', methods=['DELETE'])
@token_required
def remove_user(user, username=None):
    u = User.get(username=username)
    if not u or u.username in 'test':
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

                    teacher = Teacher(data['dni'], data['name'], data['surnames'], data['potential'], data['tutorial_hours']
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
            return response(Teacher.get(dni).to_dict())
        return response({'message': 'Data not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher/<dni>', methods=['PUT'])
@token_required
def update_teacher(user, dni=None):

    try:
        if not request.get_json() and not dni:
            return response({'message': 'Data not found'}, 404)

        teacher = Teacher.get(dni)
        if teacher:
            teacher.update(request.get_json())
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


@app.route('/teacher/tutorial', methods=['POST'])
@token_required
def create_tutorial(current_user):
    try:
        data = request.get_json()
        if data:
            if not contains_keys(['first_semester', 'second_semester', 'hours'], data.keys()):
                return response({'message': 'data not found'}, 404)

            if not current_user.teacher_dni:
                return response({'message': 'User is not teacher'}, 404)

            teacher = Teacher.get(current_user.teacher_dni)
            if not teacher:
                return response({'message': 'Teacher not found'}, 404)

            if teacher.tutorial:
                teacher.tutorial.delete()

            teacher.tutorial = Tutorial(first_semester=json.dumps(data['first_semester']),
                                        second_semester=json.dumps(data['second_semester']), hours=data['hours'])
            if teacher.save():
                return response({'message': 'Tutorial has been saved'})

        return response({'message': 'Data not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher/coordinator/<dni>', methods=['GET'])
@token_required
def get_teacher_coordinator(user, dni=None):
    try:
        if dni:
            subject_all = Subject.query.filter_by(coordinator_dni=dni).all()
            responsible_list = [subject.to_dict() for subject in subject_all]
            return response(responsible_list)
        return response({}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/teacher/responsible/<dni>', methods=['GET'])
@token_required
def get_teacher_responsible(user, dni=None):
    try:
        if dni:
            subject_all = Subject.query.filter_by(responsible_dni=dni).all()
            resp_subject = [subject.to_dict() for subject in subject_all]
            return response(resp_subject)
        return response({'message': 'Data not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


'''
   DATA BASES
'''


@app.route('/database', methods=['POST'])
def upload_database():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            # try:
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
        if request.method == 'GET':
            return send_file(export_schema(), cache_timeout=-1)
        return response({'message': 'Value not found'})
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

            if message_pda['count'] is 0:
                return response({'message': message_pda}, 404)
            return response({'message': message_pda})
        else:
            return response({'message': 'Data not found'}, 404)
    except Exception as e:
        return response({'error': e}, 500)


'''
    Knowledge Area
'''


@app.route('/knowledgeAreas', methods=['GET'])
@token_required
def get_knowledge_area(user):
    try:
        return response([area.to_dict() for area in KnowledgeArea.all()])
    except Exception as ex:
        return response({'message': ex}, 500)


'''
    Venias
'''


@app.route('/veniaI', methods=['GET'])
@token_required
def get_all_venia1(user):
    try:
        return response([venia.to_dict() for venia in VeniaI.all()])
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/veniaI/<teacher_dni>', methods=['GET'])
@token_required
def get_venia1(user, teacher_dni=None):
    try:
        teacher = Teacher.get(teacher_dni=teacher_dni)
        if not teacher:
            return response({'message': 'Teacher not found'})
        return response([build_dict(veniaI=venia, area=venia.knowledgeArea) for venia in teacher.veniaI])

    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/veniaII', methods=['GET'])
@token_required
def get_all_venia2(user):
    try:
        return response([venia.to_dict() for venia in VeniaII.all()])
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/veniaII/<teacher_dni>', methods=['GET'])
@token_required
def get_venia2(user, teacher_dni=None):
    try:
        teacher = Teacher.get(teacher_dni=teacher_dni)
        if teacher:
            return response([build_dict(veniaII=venia, subject=venia.subject) for venia in teacher.veniaII])
        return response({'message': 'Teacher not found'})

    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/veniaI', methods=['POST'])
@token_required
def create_venia1(user):
    try:
        data = request.get_json()
        if data:
            area = KnowledgeArea.get(data['area_cod'])
            if not area:
                return response({'message': 'Knowledge area not found'}, 404)

            venia = VeniaI(area=area, teacher=user.teacher)
            if venia.save():
                return response({'message': 'Create venia of type 1'})
            return response({'message': 'Venia of type 1 not could created'})

        return response({'message': 'Data not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/veniaII', methods=['POST'])
@token_required
def create_venia2(user):
    try:
        data = request.get_json()
        if data:
            subject = Subject.get(subject_cod=data['subject_cod'], area_cod=data['area_cod'])
            if not subject:
                return response({'message': 'Subject not found'}, 404)

            venia = VeniaII(subject=subject, teacher=user.teacher)
            if venia.save():
                return response({'message': 'Create venia of type 2'})

            return response({'message': 'Venia of type 1 not could created'}, 401)

        return response({'message': 'Data not found'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/veniaI/<area_cod>/<teacher_dni>', methods=['PUT'])
@token_required
def update_venia1(user, area_cod=None, teacher_dni=None):
    try:
        if not area_cod and not teacher_dni:
            return response({'message': 'teacher or Knowlegde Area not found'}, 404)

        impart = VeniaI.get(area_cod=area_cod, teacher_dni=teacher_dni)
        impart.update(request.get_json())
        if impart.save():
            return response({'message': 'Venia I update successfully'})

        return response({'message': 'Venia I not could saved'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)


@app.route('/veniaII/<area_cod>/<subject_cod>/<teacher_dni>', methods=['PUT'])
@token_required
def update_venia2(user, area_cod=None, subject_cod=None, teacher_dni=None):

    try:
        data = request.get_json()
        if not area_cod or not subject_cod or not teacher_dni or not data:
            return response({'message': 'teacher or subject not found'}, 404)

        impart = VeniaII.get(area_cod=area_cod, subject_cod=subject_cod, teacher_dni=teacher_dni)
        impart.update(data)
        if impart.save():
            return response({'message': 'Venia II update successfully'})
        return response({'message': 'Venia II not could saved'}, 404)
    except Exception as ex:
        return response({'message': ex}, 500)
