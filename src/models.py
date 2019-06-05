from src import db
from sqlalchemy.exc import IntegrityError

Have = db.Table('Have', db.metadata,
                 db.Column('subject_cod', db.Integer, db.ForeignKey('subjects.subject_cod')),
                 db.Column('area_cod', db.String(64), db.ForeignKey('knowledgeAreas.area_cod'))
                 )


class UniversityDegrees(db.Model):
    __tablename__ = "universityDegrees"

    university_degree_cod = db.Column(db.Integer, primary_key=True)
    acronym = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)
    study_center = db.Column(db.String(64))
    plan_cod = db.Column(db.String(64))
    special_cod = db.Column(db.String(64))

    subjects = db.relationship('Subjects', backref='UniversityDegrees', lazy='dynamic')

    def __init__(self, university_degree_cod=None, plan_code=None, specialty_cod=None, acronym=None,
                 name=None, study_center=None):

        self.university_degree_cod = university_degree_cod
        self.plan_cod = plan_code
        self.special_cod = specialty_cod
        self.acronym = acronym
        self.name = name
        self.study_center = study_center

    def __repr__(self):
        return '<Titulacion {}, {}>'.format(self.university_degree_cod, self.name)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(university_degree_cod=None):
        if university_degree_cod:
            return UniversityDegrees.query.get(university_degree_cod)

    def add_subject(self, subject=None):
        if subject:
            self.subjects.append(subject)

    @staticmethod
    def get_all():
        return UniversityDegrees.query.all()


class Subjects(db.Model):
    __tablename__ = "subjects"

    subject_cod = db.Column(db.Integer, primary_key=True)
    university_degree_code = db.Column(db.Integer, db.ForeignKey('universityDegrees.university_degree_cod'))
    name = db.Column(db.String(64))
    course = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    type = db.Column(db.String(64))

    universityDegrees = db.relationship('UniversityDegrees', back_populates="subjects")
    knowledge_areas = db.relationship('KnowledgeAreas', secondary=Have, backref="subjects")
    groups = db.relationship('Assigned', back_populates="subjects")
    PDA = db.relationship('PDA', backref='subjects', lazy='dynamic')

    def __init__(self, subject_cod=None, name=None, semester=None, academic_year=None, type=None):
        self.subject_cod = subject_cod
        self.name = name
        self.course = academic_year
        self.semestre = semester
        self.type = type

    def __repr__(self):
        return '<Asignatura {}, {}>'.format(self.subjects_cod, self.name)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(subject=None):
        if subject:
            return Subjects.query.get(subject)

    def get_cod(self):
        return self.subjects_cod

    @staticmethod
    def get_all():
        return Subjects.query.all()



class Groups(db.Model):
    __tablename__ = "groups"

    group_cod = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64))
    subjects = db.relationship('Assigned', back_populates="groups")

    def __init__(self, group_code=None, type=None):

        self.group_cod = group_code
        self.type = type

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(group_id=None):
        if group_id:
            return Groups.query.get(group_id)


class KnowledgeAreas(db.Model):
    __tablename__ = "knowledgeAreas"

    area_cod = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __init__(self, area_cod=None, name=None):
        self.area_cod = area_cod
        self.name = name

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def get(area_cod=None):
        if area_cod:
            return KnowledgeAreas.query.get(area_cod)


class PDA(db.Model):
    __tablename__ = "PDA"

    id = db.Column(db.Integer, primary_key=True)
    subject_cod = db.Column(db.Integer, db.ForeignKey('subjects.subject_cod'), unique=True)
    status = db.Column(db.String(64))
    observations = db.Column(db.String(128))


class Teachers(db.Model):
    __tablename__ = "teachers"

    DNI = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64))
    surnames = db.Column(db.String(64))
    tutorial = db.Column(db.String(140))
    potential_teaching = db.Column(db.String(64))
    preassigned_hours = db.Column(db.Integer)

    assigned = db.relationship('Give', back_populates='teachers')


class Assigned(db.Model):
    __tablename__ = "assigned"

    group_cod = db.Column(db.Integer, db.ForeignKey('groups.group_cod'), primary_key=True)
    subject_cod = db.Column(db.Integer, db.ForeignKey('subjects.subject_cod'), primary_key=True)
    number_hours = db.Column(db.Integer)
    study_hours = db.Column(db.String(140))

    subjects = db.relationship('Subjects', back_populates='groups')
    groups = db.relationship('Groups', back_populates='subjects')
    teachers = db.relationship('Give', back_populates='assigned')

    def __init__(self, hours_numbers=None, study_hours=None):
        self.number_hours = hours_numbers
        self.study_hours = study_hours

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(subject=None, group=None):
        if subject and group:
            return Assigned.query.get([group.group_cod, subject.subject_cod])

    @staticmethod
    def get_subject_relationship(subject=None):
        if subject:
            return Assigned.query.filter_by(subject_cod=subject.subject_cod).all()

    @staticmethod
    def get_all():
        return Assigned.query.all()


class Give(db.Model):
    __tablename__ = "give"

    DNI = db.Column(db.String(64), db.ForeignKey('teachers.DNI'), primary_key=True)
    group_cod = db.Column(db.Integer, primary_key=True)
    subject_cod = db.Column(db.Integer, primary_key=True)

    coor_asignatura = db.Column(db.Boolean, default=False)
    respon_practica = db.Column(db.Boolean, default=False)
    venia = db.Column(db.Boolean, default=False)
    confirmado = db.Column(db.Boolean, default=False)

    __table_args__ = (db.ForeignKeyConstraint([group_cod, subject_cod],
                                              ['assigned.group_cod', 'assigned.subject_cod']), {})

    teachers = db.relationship('Teachers', back_populates='assigned')
    assigned = db.relationship('Assigned', back_populates='teachers')
