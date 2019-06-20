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

        university_degrees = UniversityDegrees.get_all()
        sheet.append(['Curso Acad.', 'Codigo Titulacion', 'Codigo Plan', 'Codigo Espec.', 'Codigo Asignatura.',
                      'Codigo Grupo', 'DNI (sin letra)', 'Num Horas', 'Codigo area.', 'Venia'])

        for us in university_degrees:
            us_row = ['201920', us.university_degree_cod, us.plan_cod, us.special_cod]
            subjects = us.subjects
            for sub in subjects:
                sub_row = [sub.subject_cod]
                all_assign = Assigned.get_subject_relationship(sub)
                areas = sub.knowledge_areas
                for assigned in all_assign:
                    group = Groups.get(assigned.group_cod)
                    group_row = [group.group_cod, '', assigned.number_hours]
                    for area in areas:
                        area_row = [area.area_cod, 'N']
                        sheet.append(us_row + sub_row + group_row + area_row)
                        area_row.clear()
                    group_row.clear()
                sub_row.clear()
            us_row.clear()
        wb.save(download_file)
        return download_file

    @staticmethod
    def import_database(data=None, academic_year='2019/2020'):

        if not data or not allowed_field(data):
            return {}

        subjectCount = universityDegreeCodeCount = groupCount = areaCount = 0

        for i in range(0, len(data['Curso_Academico'])):
            if data['Curso_Academico'][i]:
                university_degree = UniversityDegree.get(data['Cod Titulacion'][i])
                if not university_degree:
                    universityDegreeCodeCount += 1
                    university_degree = UniversityDegree(
                                            data['Cod Titulacion'][i],
                                            data['Nombre Titulacion'][i],
                                            data['Cod Plan'][i],
                                            data['Cod Especialidad'][i],
                                            data['Acronimo Titulacion'][i],
                                            data['Centro Imparticion'][i])
                    university_degree.save()

                area = KnowledgeArea.get(data['Cod Area'][i])
                if not area:
                    areaCount += 1
                    area = KnowledgeArea(data['Cod Area'][i], data['Nombre Area'][i])
                    area.save()

                subject = Subject.get(data['Cod Asignatura'][i])
                if not subject:
                    subjectCount += 1
                    subject = Subject(data['Cod Asignatura'][i],
                                        data['Nombre Asignatura'][i],
                                        data['Tipo Asignatura'][i],
                                        data['Cuatrimestre Asignatura'][i],
                                        data['Curso Asignatura'][i],
                                        data['Curso_Academico'][i],
                                        data['Cod Titulacion'][i])
                    subject.save()

                if subject not in area.subject:
                    area.subject.append(subject)
                    area.save()

                group = Group.get(data['Cod Grupo'][i], data['Cod Asignatura'][i])
                if not group:
                    groupCount += 1
                    group = Group(data['Cod Grupo'][i], data['Cod Asignatura'][i], data['Tipo Grupo'][i], data['Horas'][i])
                    group.save()
                else:
                    print('Grupo no añadido {}'.format(group))

        return {'subjects': subjectCount, 'universityDegrees': universityDegreeCodeCount, 'groups': groupCount,
                'areas': areaCount}

    @staticmethod
    def file_statistics(data=None):
        if data:
            value = {key: len(set(data[key])) if None not in data[key] else 0 for key in data.keys()}
            return value
        else:
            return {}
