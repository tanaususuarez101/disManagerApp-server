from src.models import *
import os
import openpyxl
from openpyxl import Workbook

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

        data = {}
        keys = []
        havent_keys = True
        for row in hoja.rows:
            if havent_keys and row[0].value and type(row[0].value) is str:
                havent_keys = False
                for i in range(0, len(row)):
                    data[row[i].value] = []
                    keys.append(row[i].value)
            else:
                for i in range(0, len(row)):
                    data[keys[i]].append(row[i].value)
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
    print('Ejecutando...')
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

        if data or allowed_field(data):
            message = {'subject': 0, 'degreeUniversity': 0, 'knowledgeArea': 0, 'groups': 0, 'row_log': []}


            # TODO - Eliminar espacios y mayúsculas de las claves de 'data'

            for i in range(0, len(data['Curso_Academico'])):
                row_saved = False
                if data['Curso_Academico'][i] is not '':

                    '''
                    TÍTULOS UNIVERSITARIOS
                    '''
                    university = UniversityDegree.get(data['Cod Titulacion'][i])
                    if not university:
                        university = UniversityDegree(data['Cod Titulacion'][i], data['Nombre Titulacion'][i],
                                                      data['Cod Plan'][i], data['Cod Especialidad'][i],
                                                      data['Acronimo Titulacion'][i], data['Centro Imparticion'][i])

                        if university.save():
                            message['degreeUniversity'] += 1
                            row_saved = True

                    '''
                    ÁREAS DE CONOCIMIENTOS
                    '''
                    area = KnowledgeArea.get(data['Cod Area'][i])
                    if not area:
                        area = KnowledgeArea(data['Cod Area'][i], data['Nombre Area'][i])
                        if area.save():
                            message['knowledgeArea'] += 1
                            row_saved = True

                    '''
                    ASIGNATURAS
                    '''

                    subject = Subject.get(data['Cod Asignatura'][i], data['Cod Area'][i])
                    if not subject:
                        subject = Subject(data['Cod Asignatura'][i], data['Cod Area'][i], data['Cod Titulacion'][i],
                                          data['Nombre Asignatura'][i], data['Tipo Asignatura'][i],
                                          data['Cuatrimestre Asignatura'][i], data['Curso Asignatura'][i],
                                          data['Curso_Academico'][i])
                        if subject.save():
                            message['subject'] += 1
                            row_saved = True

                    '''
                    GRUPOS
                    '''

                    group = Group.get(data['Cod Grupo'][i], data['Cod Asignatura'][i], data['Cod Area'][i])
                    if not group:
                        group = Group(subject, data['Cod Grupo'][i], data['Tipo Grupo'][i], data['Horas'][i])
                        if group.save():
                            message['groups'] += 1
                            row_saved = True

                    if row_saved:
                        message['row_log'].append(build_dict(university=university, area=area, subject=subject,
                                                             group=group))

        return message


def import_pda(data=None):
    if not data or (data and not contains_keys(['Cod Asignatura', 'Cod Area', 'Estado', 'Observaciones'], data.keys())):
        return ''

    PDAs = []
    for i in range(0, len(data['Cod Asignatura'])):
        subject = Subject.get(data['Cod Asignatura'][i], data['Cod Area'][i])
        if subject:
            pda = PDA(subject, data['Estado'][i], data['Observaciones'][i])
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
    if data and not contains_keys(['dni', 'nombre', 'apellidos', 'potencial', 'horas tutorias', 'Cod Area'], data.keys()):
        return ''

    for i in range(0, len(data['dni'])): # TODO - formatear nombres en minuculas y quitar espacio
        if not data['dni'] and not data['nombre'] and not data['apellidos'] and not data['potencial'] \
                and not data['horas tutorias'] and data['Cod Area']:
            continue

        list_teacher = []
        if not Teacher.get(data['dni'][i]):
            area = KnowledgeArea.get(data['Cod Area'][i])
            if area:
                teacher = Teacher(dni=data['dni'][i], name=data['nombre'][i], surnames=data['apellidos'][i],
                                  potential=data['potencial'][i], tutorial_hours=data['horas tutorias'][i],
                                  area=area)
                if teacher.save():
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
