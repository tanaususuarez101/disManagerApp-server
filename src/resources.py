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
            subject_count = university_degree_code_count = group_count = area_count = 0

            for i in range(0, len(data['Curso_Academico'])):
                if data['Curso_Academico'][i]:
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
                            university_degree_code_count += 1

                    subject = Subject.get(data['Cod Asignatura'][i])
                    if not subject:
                        subject = Subject(data['Cod Asignatura'][i],
                                          data['Nombre Asignatura'][i],
                                          data['Tipo Asignatura'][i],
                                          data['Cuatrimestre Asignatura'][i],
                                          data['Curso Asignatura'][i],
                                          data['Curso_Academico'][i],
                                          data['Cod Titulacion'][i])
                        if subject.save():
                            subject_count += 1

                    area = KnowledgeArea.get(data['Cod Area'][i])
                    if not area:

                        area = KnowledgeArea(data['Cod Area'][i], data['Nombre Area'][i])
                        area.save()
                        if area.save():
                            area_count += 1

                    group = Group.get(data['Cod Grupo'][i], data['Cod Asignatura'][i], data['Cod Area'][i])
                    if not group:
                        group = Group(data['Cod Grupo'][i], data['Cod Asignatura'][i], data['Cod Area'][i],
                                      data['Tipo Grupo'][i], data['Horas'][i])
                        if group.save():
                            group_count += 1

        return {
            'subjects': subject_count,
            'universityDegrees': university_degree_code_count,
            'groups': group_count,
            'areas': area_count
        }

    @staticmethod
    def import_teacher(data=None):
        if data:
            for i in range(0, len(data['dni'])):
                teacher = Teacher.get(data['dni'][i])
                if not teacher:
                    teacher = Teacher(
                        data['dni'][i],
                        data['nombre'][i],
                        data['apellidos'][i],
                        data['potencial'][i],
                        data['horas tutorias'][i],
                        data['Cod Area'][i])
                    if teacher.save():
                        print('Ha sido guardado {}'.format(teacher))

    @staticmethod
    def import_pda(data=None):
        if data:
            for i in range(0, len(data['Cod Asignatura'])):
                pda = PDA(data['Cod Asignatura'][i], data['Estado'][i], data['Observaciones'][i])
                if pda.save():
                    print('Ha sido guardado {}'.format(pda))

    @staticmethod
    def file_statistics(data=None):
        if data:
            value = {key: len(set(data[key])) if None not in data[key] else 0 for key in data.keys()}
            return value

    @staticmethod
    def load_simulation(data=None):
        if data:
            for i in range(0, len(data['Cod Asignatura'])):
                subject = Subject.get(data['Cod Asignatura'][i])
                group = Group.get(data['Cod Grupo'][i], data['Cod Asignatura'][i], data['Cod Area'][i])
                teacher = Teacher.get(data['dni'][i])
                impart = Impart(group, teacher, data['Horas'][i])
                impart.save()

                if data['Coord_practica'][i] == 'S' and data['Coord_asignatura'][i] == 'S':
                    coordinator = Coordinator(subject, teacher, True, True)
                    coordinator.save()
                elif data['Coord_practica'][i] == 'S':
                    coordinator = Coordinator(subject, teacher, True)
                    coordinator.save()
                elif data['Coord_asignatura'][i] == 'S':
                    coordinator = Coordinator(subject, teacher, True)
                    coordinator.save()

