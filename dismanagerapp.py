from src import app, db
from src.models import Titulacion, Asignatura,PDA

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Titulacion': Titulacion,
            'Asignatura': Asignatura,
            'PDA': PDA}

if __name__ == '__main__':
    app.run(host='localhost', debug=True)