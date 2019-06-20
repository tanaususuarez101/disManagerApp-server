from src import app, db
from src.models import Subject, Group, Teacher, Impart, UniversityDegree, PDA, KnowledgeArea, Coordinator
#KnowledgeAreas,  PDA, , Have,

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Subject': Subject,
            'Group': Group,
            'Impart': Impart,
            'Teacher': Teacher,
            'UniversityDegree': UniversityDegree,
            'PDA': PDA,
            'AreaKnowledge': KnowledgeArea,
            'Coordinator': Coordinator
            }




if __name__ == '__main__':
    app.run(host='localhost', debug=True)


