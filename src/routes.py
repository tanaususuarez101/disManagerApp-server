from src import app
from src.models import Asignado, Asignatura, Grupo

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/test')
def text():
    a1 = Asignatura.query.get(403)
    for item in a1.grupos:
        print(item.grupo.tipo)

    g1 = Grupo.query.get(1)
    for item in g1.asignaturas:
        print(item.asignatura.nombre)

    return 'TEST FINALIZADO'