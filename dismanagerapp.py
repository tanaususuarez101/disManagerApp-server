from src import app, db
from src.models import Subject, Group, Teacher, Impart, UniversityDegree, PDA, KnowledgeArea
#KnowledgeAreas,  PDA, , Have,

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Subject': Subject,
            'Group': Group,
            'Impart': Impart,
            'Teacher': Teacher,
            'UniversityDegrees': UniversityDegree,
            'PDA': PDA,
            'AreaKnowledge': KnowledgeArea,
            }




if __name__ == '__main__':
    app.run(host='localhost', debug=True)


