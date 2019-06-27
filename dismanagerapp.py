from src import app, db
from src.models import Subject, Group, Teacher, UniversityDegree, PDA, KnowledgeArea, Coordinator, Impart, Tutorial


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
            'Coordinator': Coordinator,
            'Tutorial': Tutorial
            }




if __name__ == '__main__':
    app.run(host='localhost', debug=True)


