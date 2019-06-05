from src import app, db
from src.models import Subjects,  Groups,  KnowledgeAreas, Give, Assigned, UniversityDegrees, PDA, Teachers, Have

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'UniversityDegrees': UniversityDegrees,
            'Subjects': Subjects,
            'PDA': PDA,
            'Groups': Groups,
            'Teachers': Teachers,
            'AreaKnowledge': KnowledgeAreas,
            "Have": Have,
            "Give": Give,
            "Assigned": Assigned
            }




if __name__ == '__main__':
    app.run(host='localhost', debug=True)


