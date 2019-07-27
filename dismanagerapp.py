from src import app, db
#from src.models import  Tutorial
from src.models import Subject, Teacher, Group, Impart, KnowledgeArea, PDA, UniversityDegree, User, Tutorial

#KnowledgeAreas,  PDA, , Have,

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Subject': Subject,
            'Teacher': Teacher,
            'Group': Group,
            'Impart': Impart,
            'KnowledgeArea': KnowledgeArea,
            'UniversityDegree': UniversityDegree,
            'PDA': PDA,
            'User': User,
            'Tutorial': Tutorial
            }




if __name__ == '__main__':
    app.run(host='localhost', debug=True)


