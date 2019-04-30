from src import app, db
#from src.models import Titulacion, Asignatura, PDA, Grupo, Profesor, AreaConocimiento, Imparte, Tiene, Asignado
from src.models import Asignatura,  Grupo,  AreaConocimiento, Tiene, Asignado, Titulacion, PDA, Profesor, Imparte

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Titulacion': Titulacion,
            'Asignatura': Asignatura,
            'PDA': PDA,
            'Grupo':Grupo,
            'Profesor': Profesor,
            'AreaConocimiento': AreaConocimiento,
            "Imparte": Imparte,
            "Tiene": Tiene,
            "Asignado": Asignado
            }




if __name__ == '__main__':
    app.run(host='localhost', debug=True)


