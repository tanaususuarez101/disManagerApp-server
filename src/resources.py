from src.models import *
import os
import openpyxl


class Resource:

    def openxlsx(filename=None):
        if filename and filename == '':
            return {}

        doc = openpyxl.load_workbook(filename)
        hoja = doc.get_sheet_by_name('Hoja1')

        data = {}
        keys = []
        for row in hoja.rows:
            if row[0].value and type(row[0].value) is str:
                for i in range(0, len(row)):
                    data[row[i].value] = []
                    keys.append(row[i].value)
            elif row[0].value and type(row[0].value) is not str:
                for i in range(0, len(row)):
                    data[keys[i]].append(row[i].value)
        return data

    @staticmethod
    def import_database(data=None):
        if not data:
            return {}

        subjectCount = universityDegreeCodeCount = groupCount = areaCount = 0

        print(data)
        for i in range(0, len(data['Curso_Academico'])):
#        for i in range(0, 3):
            titulacion = Titulacion.get(data['Cod Titulacion'][i])
            if not titulacion:
                universityDegreeCodeCount += 1
                titulacion = Titulacion(data['Cod Titulacion'][i],
                                        data['Cod Plan'][i],
                                        data['Cod Especialidad'][i],
                                        data['Acronimo Titulacion'][i],
                                        data['Nombre Titulacion'][i],
                                        data['Centro Imparticion'][i])
                titulacion.save()

            group = Grupo.get(data['Cod Grupo'][i])
            if not group:
                groupCount += 1
                group = Grupo(data['Cod Grupo'][i], data['Tipo Grupo'][i])
                group.save()

            area = AreaConocimiento.get(data['Cod Area'][i])
            if not area:
                areaCount += 1
                area = AreaConocimiento(data['Cod Area'][i], data['Nombre Area'][i])
                area.save()

            asignatura = Asignatura.get(data['Cod Asignatura'][i])
            if not asignatura:
                subjectCount += 1
                asignatura = Asignatura(data['Cod Asignatura'][i],
                                        data['Nombre Asignatura'][i],
                                        data['Curso Asignatura'][i],
                                        data['Cuatrimestre Asignatura'][i],
                                        data['Tipo Asignatura'][i])
                titulacion.add_subject(asignatura)
                asignatura.create_relactionship(area=area)
                titulacion.save()
                asignatura.save()


            res = Asignado.get(asignatura, group)
            if res is None:
                assigned = Asignado(data['Horas'][i])
                assigned.grupo = group
                assigned.asignatura = asignatura
                assigned.save()


        return {'subjects': subjectCount,
                'universitiesDegree': universityDegreeCodeCount,
                'groups': groupCount,
                'areas': areaCount}