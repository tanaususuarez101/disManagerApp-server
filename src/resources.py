from src.models import *
import os
import openpyxl
from openpyxl import Workbook

ALLOWED_COLUMNS = ['Curso_Academico', 'Cod Titulacion', 'Cod Plan', 'Cod Especialidad', 'Acronimo Titulacion',
                  'Nombre Titulacion', 'Centro Imparticion', 'Cod Asignatura', 'Nombre Asignatura', 'Curso Asignatura',
                  'Cuatrimestre Asignatura', 'Tipo Asignatura', 'Cod Grupo', 'Tipo Grupo', 'Dni', 'Horas', 'Cod Area',
                  'Nombre Area', 'Venia']
ALLOWED_KEYS = ['Cod Titulacion', 'Cod Asignatura', 'Cod Grupo', 'Cod Area']
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')


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
    def backup_database():
        wb = Workbook()
        download_file = os.path.join(UPLOADS_DIR, 'backup.xlsx')# TODO- add date to exit file
        sheet = wb.active

        university_degrees = UniversityDegree.get_all()
        sheet.append(ALLOWED_COLUMNS)

        for us in university_degrees:
            us_row = [201920, us.university_degree_cod, us.plan_cod, us.special_cod, us.acronym, us.name,
                      us.study_center]
            subjects = us.subjects
            for sub in subjects:
                sub_row = [sub.subject_cod, sub.name, sub.course, sub.semester, sub.type]
                all_assign = Assigned.get_subject_relationship(sub)
                areas = sub.knowledge_areas
                for assigned in all_assign:
                    group = Groups.get(assigned.group_cod)
                    group_row = [group.group_cod, group.type, '', assigned.number_hours]
                    for area in areas:
                        area_row = [area.area_cod, area.name]
                        sheet.append(us_row + sub_row + group_row + area_row)
                        area_row.clear()
                    group_row.clear()
                sub_row.clear()
            us_row.clear()
        wb.save(download_file)
        return download_file

    @staticmethod
    def export_database():
        wb = Workbook()
        download_file = os.path.join(UPLOADS_DIR, 'database.xlsx')# TODO- add date to exit file
        sheet = wb.active

        groups = Group.get_all()
        sheet.append(['Curso Acad.', 'Codigo Titulacion', 'Codigo Plan', 'Codigo Espec.', 'Codigo Asignatura.',
                      'Codigo Grupo', 'DNI (sin letra)', 'Num Horas', 'Codigo area.', 'Venia'])

        for group in groups:
            subject = Subject.get(group.subject_cod)
            area = KnowledgeArea.get(group.area_cod)
            titulation = UniversityDegree.get(subject.university_degree_cod)
            sheet.append(['201920', titulation.university_degre_cod, titulation.plan_cod, titulation.special_cod,
                         subject.subject_cod, group.group_cod, '', group.group_hours, area.area_cod, 'N'])
            wb.save(download_file)

        return download_file

    @staticmethod
    def import_database(data=None):

        if data or allowed_field(data):
            message_output = {'asignaturas': [], 'titulacion': [], 'area_conocimiento': [], 'grupos': []}

            # TODO - Eliminar espacios y mayúsculas de las claves de 'data'
            for i in range(0, len(data['Curso_Academico'])):
                if data['Curso_Academico'][i] is not '':

                    '''
                    TÍTULOS UNIVERSITARIOS
                    '''

                    university_degree = UniversityDegree.get(data['Cod Titulacion'][i])
                    if not university_degree:
                        university_degree = UniversityDegree(
                                                data['Cod Titulacion'][i],
                                                data['Nombre Titulacion'][i],
                                                data['Cod Plan'][i],
                                                data['Cod Especialidad'][i],
                                                data['Acronimo Titulacion'][i],
                                                data['Centro Imparticion'][i])
                        if university_degree.save():
                            message_output['titulacion'].append(
                                {'SUCCESS': 'Se ha añadido {}: {}'.format(university_degree.university_cod,
                                                                          university_degree.name)})
                        else:
                            message_output['titulacion'].append(
                                {'ERROR': 'No se ha guardado {}: {}'.format(university_degree.university_cod,
                                                                            university_degree.name)})

                    '''
                    ÁREAS DE CONOCIMIENTOS
                    '''

                    area = KnowledgeArea.get(data['Cod Area'][i])
                    if not area:
                        area = KnowledgeArea(data['Cod Area'][i], data['Nombre Area'][i])
                        if area.save():
                            message_output['area_conocimiento'].append(
                                {'SUCCESS': 'Se ha añadido {}: {}'.format(area.area_cod, area.name)})
                        else:
                            message_output['area_conocimiento'].append(
                                {'ERROR': 'No se ha gaurdado {}: {}'.format(area.area_cod, area.name)})

                    '''
                    ASIGNATURAS
                    '''

                    subject = Subject.get(data['Cod Asignatura'][i], data['Cod Area'][i])
                    if not subject:
                        subject = Subject(data['Cod Asignatura'][i],
                                          data['Cod Area'][i],
                                          data['Cod Titulacion'][i],
                                          data['Nombre Asignatura'][i],
                                          data['Tipo Asignatura'][i],
                                          data['Cuatrimestre Asignatura'][i],
                                          data['Curso Asignatura'][i],
                                          data['Curso_Academico'][i])
                        if subject.save():
                            message_output['asignaturas'].append(
                                {'SUCCESS': 'Se ha añadido {}: {}'.format(subject.subject_cod, subject.name)})
                        else:
                            message_output['asignaturas'].append(
                                {'ERROR': 'No se ha añadido {}: {}'.format(subject.subject_cod, subject.name)})

                    '''
                    GRUPOS
                    '''

                    group = Group.get(data['Cod Grupo'][i], data['Cod Asignatura'][i], data['Cod Area'][i])
                    if not group:
                        group = Group(subject, data['Cod Grupo'][i], data['Tipo Grupo'][i], data['Horas'][i])
                        if group.save():
                            message_output['grupos'].append(
                                {'SUCCESS': 'Se ha añadido grupo {}: {}, de la asignatura {}'.format(group.group_cod,
                                                                                                     group.type,
                                                                                                     subject.name)})
                        else:
                            message_output['grupos'].append(
                                {'ERROR': 'No se ha añadido grupo {}: {}, de la asignatura {}'.format(group.group_cod,
                                                                                                     group.type,
                                                                                                     subject.name)})
        return message_output

    @staticmethod
    def import_teacher(data=None):
        if data and not contains_keys(['dni', 'nombre', 'apellidos', 'potencial', 'horas tutorias', 'Cod Area'],
                                      data.keys()):
            return ''

        for i in range(0, len(data['dni'])): # TODO - formatear nombres en minuculas y quitar espacio
            if not data['dni'] and not data['nombre'] and not data['apellidos'] and not data['potencial'] \
                    and not data['horas tutorias'] and data['Cod Area']:
                continue

            if Teacher.get(data['dni'][i]) is None:
                area = KnowledgeArea.get(data['Cod Area'][i])
                if area:
                    teacher = Teacher(dni=data['dni'][i],
                                      name=data['nombre'][i],
                                      surnames=data['apellidos'][i],
                                      potential=data['potencial'][i],
                                      tutorial_hours=data['horas tutorias'][i],
                                      area=area)
                    teacher.save()


    @staticmethod
    def import_pda(data=None):
        if not data or (data and not contains_keys(['Cod Asignatura', 'Cod Area', 'Estado', 'Observaciones'], data.keys())):
            return ''

        for i in range(0, len(data['Cod Asignatura'])):
            subject = Subject.get(data['Cod Asignatura'][i], data['Cod Area'][i])
            if subject:
                pda = PDA(subject, data['Estado'][i], data['Observaciones'][i])
                pda.save()

    @staticmethod
    def file_statistics(data=None):
        if data:
            value = {key: len(set(data[key])) if None not in data[key] else 0 for key in data.keys()}
            return value

    @staticmethod
    def join_file(filename):
        return os.path.join(UPLOADS_DIR, filename)

def build_dict(subject=None, group=None, teacher=None, area=None, university=None, pda=None, user=None,
               tutorial=None, impart=None, veniaI=None, veniaII=None):

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


def contains_keys(list_keys=[], data_keys=None):
    if len(list_keys) > 0 and data_keys:
        for key in list_keys:
            if key not in data_keys:
                return False
        return True
