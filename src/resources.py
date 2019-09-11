from src.models import *
import os
import openpyxl
from openpyxl import Workbook
import uuid

ALLOWED_COLUMNS = ['Curso_Academico', 'Cod Titulacion', 'Cod Plan', 'Cod Especialidad', 'Acronimo Titulacion',
                  'Nombre Titulacion', 'Centro Imparticion', 'Cod Asignatura', 'Nombre Asignatura', 'Curso Asignatura',
                  'Cuatrimestre Asignatura', 'Tipo Asignatura', 'Cod Grupo', 'Tipo Grupo', 'Dni', 'Horas', 'Cod Area',
                  'Nombre Area', 'Venia']
ALLOWED_KEYS = ['Cod Titulacion', 'Cod Asignatura', 'Cod Grupo', 'Cod Area']
ALLOWED_EXTENSIONS = set(['xlsx'])

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_field(data=None):

    if len(data.keys()) != len(ALLOWED_COLUMNS):
        return False

    keys = data.keys()
    for allow in ALLOWED_COLUMNS:
        if allow not in keys:
            return False

    return True


def allowed_keys(keys=None, data=None):
    if data and keys:
        for key in data.keys():
            if key not in keys:
                return False
        return True
    return False


class Resource:

    @staticmethod
    def openxlsx(filename=None):
        if filename and filename == '':
            return {}

        doc = openpyxl.load_workbook(filename)
        hoja = doc.get_sheet_by_name(str(doc.get_sheet_names()[0]))

        data, keys, first_row = {}, [], True

        for row in hoja.rows:
            if first_row and row[0].value:
                first_row = False
                keys = [col.value.replace(' ', '_').lower() for col in row if col]
                data = {key: [] for key in keys}
            else:
                for i in range(0, len(row)):
                    data[keys[i]].append(row[i].value)
        doc.close()
        return data

    @staticmethod
    def file_statistics(data=None):
        if data:
            value = {key: len(set(data[key])) if None not in data[key] else 0 for key in data.keys()}
            return value

    @staticmethod
    def join_file(filename):
        return os.path.join(UPLOADS_DIR, filename)


def export_schema():
    wb = Workbook()
    download_file = os.path.join(UPLOADS_DIR, 'database.xlsx') # TODO- add date to exit file
    sheet = wb.active

    sheet.append(['Curso Acad.', 'Codigo Titulacion', 'Codigo Plan', 'Codigo Espec.', 'Codigo Asignatura.',
                  'Codigo Grupo', 'DNI (sin letra)', 'Num Horas', 'Codigo area.', 'Venia'])

    count = 0
    for g in Group.all():
        impart, sub = [], g.subject
        for i in g.teacher:
            if i.approved:
                v, teacher = '', i.teacher
                if teacher.knowledgeArea is not sub.knowledgeArea:
                    area_cod = [v.area_cod for v in teacher.veniaI if v.approved]
                    subject = [{v.subject_cod, v.area_cod} for v in teacher.veniaII if v.approved]
                    v = 'Si 'if sub.area_cod in area_cod or {sub.subject_cod, sub.area_cod} in subject else 'No'

                impart.append({'dni': i.teacher_dni, 'hours': i.hours, 'venia': v})

        if impart:
            for i in impart:
                row = ['201920', sub.university_cod, sub.university_degree.plan_cod, sub.university_degree.special_cod,
                       sub.subject_cod, g.group_cod, i['dni'], i['hours'], sub.area_cod, i['venia']]
                sheet.append(row)
                wb.save(download_file)
        else:
            row = ['201920', sub.university_cod, sub.university_degree.plan_cod, sub.university_degree.special_cod,
                   sub.subject_cod, g.group_cod, '', '', sub.area_cod, '']
            sheet.append(row)
            wb.save(download_file)

    return download_file


def import_schema(data=None):
    message = {'subject': 0, 'degreeUniversity': 0, 'knowledgeArea': 0, 'groups': 0, 'row_log': []}
    if data or allowed_field(data):
        # TODO - Eliminar espacios y mayúsculas de las claves de 'data'
        for i in range(0, len(data['curso_academico'])):
            row_saved = False
            if data['curso_academico'][i] is not '':

                '''
                TÍTULOS UNIVERSITARIOS
                '''
                university = UniversityDegree.get(data['cod_titulacion'][i])
                if not university:
                    university = UniversityDegree(data['cod_titulacion'][i], data['nombre_titulacion'][i],
                                                  data['cod_plan'][i], data['cod_especialidad'][i],
                                                  data['acronimo_titulacion'][i], data['centro_imparticion'][i])

                    if university.save():
                        message['degreeUniversity'] += 1
                        row_saved = True

                '''
                ÁREAS DE CONOCIMIENTOS
                '''
                area = KnowledgeArea.get(data['cod_area'][i])
                if not area:
                    area = KnowledgeArea(data['cod_area'][i], data['nombre_area'][i])
                    if area.save():
                        message['knowledgeArea'] += 1
                        row_saved = True

                '''
                ASIGNATURAS
                '''

                subject = Subject.get(data['cod_asignatura'][i], data['cod_area'][i])
                if not subject:
                    subject = Subject(data['cod_asignatura'][i], data['cod_area'][i], data['cod_titulacion'][i],
                                      data['nombre_asignatura'][i], data['tipo_asignatura'][i],
                                      data['cuatrimestre_asignatura'][i], data['curso_asignatura'][i],
                                      data['curso_academico'][i])
                    if subject.save():
                        message['subject'] += 1
                        row_saved = True

                '''
                GRUPOS
                '''

                group = Group.get(data['cod_grupo'][i], data['cod_asignatura'][i], data['cod_area'][i])
                if not group:
                    group = Group(subject, data['cod_grupo'][i], data['tipo_grupo'][i], data['horas'][i])
                    if group.save():
                        message['groups'] += 1
                        row_saved = True

                if row_saved:
                    message['row_log'].append(build_dict(university=university, area=area, subject=subject,
                                                         group=group))

    return message


def import_pda(data=None):
    if not data or (data and not contains_keys(['cod_asignatura', 'cod_area', 'estado', 'observaciones'], data.keys())):
        return ''

    PDAs = []
    for i in range(0, len(data['cod_asignatura'])):
        subject = Subject.get(data['cod_asignatura'][i], data['cod_area'][i])
        if subject:
            pda = PDA(subject, data['estado'][i], data['observaciones'][i])
            if pda.save():
                PDAs.append(pda.to_dict())

    return {'pda': PDAs, 'count': len(PDAs)}


def build_dict(subject=None, group=None, teacher=None, area=None, university=None, pda=None, user=None, tutorial=None,
               impart=None, veniaI=None, veniaII=None):

    output_dict = {}
    output_dict.update(teacher.to_dict()) if teacher else output_dict
    output_dict.update(subject.to_dict()) if subject else output_dict
    output_dict.update(group.to_dict()) if group else output_dict
    output_dict.update(area.to_dict()) if area else output_dict
    output_dict.update(university.to_dict()) if university else output_dict
    output_dict.update(pda.to_dict()) if pda else output_dict
    output_dict.update(user.to_dict()) if user else output_dict
    output_dict.update(tutorial.to_dict()) if tutorial else output_dict
    output_dict.update(impart.to_dict()) if impart else output_dict
    output_dict.update(veniaI.to_dict()) if veniaI else output_dict
    output_dict.update(veniaII.to_dict()) if veniaII else output_dict
    return output_dict


def import_teacher(data=None):
    if data and not contains_keys(['dni', 'nombre', 'apellidos', 'potencial', 'horas_tutorias', 'cod_area'], data.keys()):
        return ''

    list_teacher = []
    for i in range(0, len(data['dni'])):
        if not Teacher.get(data['dni'][i]):
            area = KnowledgeArea.get(data['cod_area'][i])
            if area:
                teacher = Teacher(dni=data['dni'][i], name=data['nombre'][i], surnames=data['apellidos'][i],
                                  potential=data['potencial'][i], tutorial_hours=data['horas_tutorias'][i],
                                  area=area)

                password = {'password': 'prueba'}
                user = User(str(data['dni'][i]), generate_password(password), False, public_id())
                user.teacher = teacher
                if user.save():
                    list_teacher.append(teacher.to_dict())

    return {'teachers': list_teacher, 'count': len(list_teacher)}


def group_cover_hours(group=None):
    cover_hours = 0.
    if group:
        for impart in group:
            group = Group.get(impart.area_cod, impart.subject_cod, impart.group_cod)
            cover_hours += float(group.hours)
    return cover_hours


def teacher_cover_hours(group=None):
    if group:
        cover_hour = 0
        for impart in group.teacher:
            cover_hour += float(impart.hours)
        return {"group_cover_hours": cover_hour - float(group.hours)}


def contains_keys(list_keys=None, data_keys=None):
    if list_keys is None:
        list_keys = []
    if len(list_keys) > 0 and data_keys:
        for key in list_keys:
            if key not in data_keys:
                return False
        return True


def generate_password(data=None):
    if data and 'password' in data:
        return generate_password_hash(data['password'], method='sha256')


def public_id():
    return str(uuid.uuid4())
