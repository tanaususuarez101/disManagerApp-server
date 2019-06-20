from src import db
from sqlalchemy.exc import IntegrityError
import sys

Belong_to = db.Table('Belong_to', db.metadata,
                 db.Column('subject_cod', db.String(64), db.ForeignKey('subject.subject_cod')),
                 db.Column('area_cod', db.String(64), db.ForeignKey('knowledgeArea.area_cod')))


Venia = db.Table('Venia', db.metadata,
                 db.Column('area_cod', db.String(64), db.ForeignKey('knowledgeArea.area_cod')),
                 db.Column('teacher_dni', db.String(64), db.ForeignKey('teacher.dni')))


class Coordinator(db.Model):
    __tablename__ = "coordinator"

    subject_cod = db.Column(db.String(64), db.ForeignKey('subject.subject_cod'), primary_key=True)
    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), primary_key=True)

    practice_coor = db.Column(db.Boolean, default=False)
    subject_coor = db.Column(db.Boolean, default=False)

    subject = db.relationship('Subject', back_populates='teacher')
    teacher = db.relationship('Teacher', back_populates='subject')

    def __init__(self, subject=None, teacher=None, practice_coordinator=False, subject_coordinator=False):
        if subject and teacher:
            self.subject = subject
            self.teacher = teacher
            self.practiceCoordinator = practice_coordinator
            self.subjectCoordinator = subject_coordinator

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(subject_cod=None, teacher_dni=None):
        if subject_cod and teacher_dni:
            return Coordinator.query.get([subject_cod, teacher_dni])

    @staticmethod
    def get_all():
        return Coordinator.query.all()

class Subject(db.Model):
    __tablename__ = "subject"

    subject_cod = db.Column(db.String(64), primary_key=True)
    university_degree_cod = db.Column(db.String(64), db.ForeignKey('universityDegree.university_degree_cod'),
                                      nullable=False)
    academic_year = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    course = db.Column(db.String(64), nullable=False)
    semester = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64), nullable=False)

    group = db.relationship('Group', back_populates="subject", cascade="all,delete")
    university_degree = db.relationship('UniversityDegree', back_populates="subject")
    knowledge_area = db.relationship('KnowledgeArea', secondary=Belong_to, back_populates="subject")
    PDA = db.relationship('PDA', back_populates="subject", cascade="all, delete-orphan")

    teacher = db.relationship('Coordinator', back_populates='subject')

    def __init__(self, subject_cod=None, name=None, type=None, semester=None, course=None, academic_year=None,
                 university_degree_cod=None):
        self.subject_cod = subject_cod
        self.name = name
        self.academic_year = academic_year
        self.course = course
        self.semester = semester
        self.type = type
        self.university_degree_cod = university_degree_cod

    def __repr__(self):
        return '<Asignatura: cod: {}, Nombre: {}, Titulación: {}>'.format(self.subject_cod, self.name,
                                                                          self.university_degree_cod)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(subject_cod=None):
        if subject_cod:
            return Subject.query.get(subject_cod)


class Impart(db.Model):
    __tablename__ = "impart"

    group_cod = db.Column(db.String(64), primary_key=True)
    subject_cod = db.Column(db.String(64), primary_key=True)
    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), primary_key=True)
    hours = db.Column(db.String(64))

    __table_args__ = (db.ForeignKeyConstraint([group_cod, subject_cod], ['group.group_cod', 'group.subject_cod']), {})

    teacher = db.relationship('Teacher', back_populates='group')
    group = db.relationship('Group', back_populates='teacher')

    def __init__(self, group=None, teacher=None, hours=None):
        if group and teacher and hours:
            self.teacher = teacher
            self.group = group
            self.hours = hours

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False


class Group(db.Model):
    __tablename__ = "group"

    group_cod = db.Column(db.String(64), primary_key=True)
    subject_cod = db.Column(db.String(64), db.ForeignKey('subject.subject_cod'), primary_key=True)

    type = db.Column(db.String(64), nullable=False)
    hours = db.Column(db.String(64))

    subject = db.relationship('Subject', back_populates='group')
    teacher = db.relationship('Impart', back_populates='group')

    def __init__(self, group_code=None, subject_cod=None, type=None, hours=None):
        print('Creando grupo: {}, {}, {}, {}'.format(group_code, subject_cod, type, hours))
        if group_code and subject_cod and type and hours:
            self.group_cod = group_code
            self.subject_cod = subject_cod
            self.type = type
            self.hours = hours

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(group_cod=None, subject_cod=None):
        if group_cod and subject_cod:
            return Group.query.get([group_cod, subject_cod])

    def to_dict(self):
        return {
            'group_cod': self.group_cod,
            'subject_cod': self.subject_cod,
            'type': self.type
        }


class Teacher(db.Model):
    __tablename__ = "teacher"

    dni = db.Column(db.String(64), primary_key=True)
    area_cod = db.Column(db.String(64), db.ForeignKey('knowledgeArea.area_cod'), nullable=True)
    name = db.Column(db.String(64), nullable=True)
    surnames = db.Column(db.String(64), nullable=True)
    tutorial = db.Column(db.String(140))
    potential = db.Column(db.String(64), nullable=True)

    group = db.relationship('Impart', back_populates='teacher')
    subject = db.relationship('Coordinator', back_populates='teacher')

    def __init__(self, dni=None, name=None, surname=None, tutorial=None, potential=None, cod_area=None):
        self.dni = dni
        self.name = name
        self.surnames = surname
        self.tutorial = tutorial
        self.potential = potential
        self.area_cod = cod_area

    def __repr__(self):
        return '<Profesor: {}, {}>'.format(self.dni, self.name)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(dni):
        if dni:
            return Teacher.query.get(dni)


class UniversityDegree(db.Model):
    __tablename__ = "universityDegree"

    university_degree_cod = db.Column(db.String(64), primary_key=True)
    acronym = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)
    study_center = db.Column(db.String(64))
    plan_cod = db.Column(db.String(64))
    special_cod = db.Column(db.String(64))

    subject = db.relationship('Subject', backref='UniversityDegree', cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, university_degree_cod=None, name=None, plan_code=None, specialty_cod=None, acronym=None,
                 study_center=None):

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

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(university_degree_cod=None):
        if university_degree_cod:
            return UniversityDegree.query.get(university_degree_cod)

    def add_subject(self, subject=None):
        if subject:
            self.subjects.append(subject)

    @staticmethod
    def get_all():
        return UniversityDegree.query.all()

    def to_dict(self):
        return {'university_degree_cod': self.university_degree_cod, 'acronym': self.acronym, 'name': self.name,
                'study_center': self.study_center, 'plan_cod': self.plan_cod, 'special_cod': self.special_cod}


class KnowledgeArea(db.Model):
    __tablename__ = "knowledgeArea"

    area_cod = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    subject = db.relationship('Subject', secondary=Belong_to, back_populates="knowledge_area", cascade="all,delete")
    teacher = db.relationship('Teacher', backref='knowledgeArea', cascade="all,delete")

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

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(area_cod=None):
        if area_cod:
            return KnowledgeArea.query.get(area_cod)


class PDA(db.Model):
    __tablename__ = "PDA"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_cod = db.Column(db.Integer, db.ForeignKey('subject.subject_cod'), unique=True, nullable=False)
    status = db.Column(db.String(64))
    observations = db.Column(db.String(128))

    subject = db.relationship('Subject', back_populates='PDA')

    def __init__(self, subject_cod=None, status=None, observations=None):
        self.subject_cod = subject_cod
        self.status = status.lower()
        self.observations = observations

    def __repr__(self):
        return '<PDA id: {}, subject_cod: {}, status: {}, observations: {} >'.format(self.id, self.subject_cod,
                                                                                     self.status, self.observations)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def getAll():
        return PDA.query.all()

    def to_dict(self):
        return {
            'id': self.id,
            'subject_cod': self.subject_cod,
            'subject_name': self.subject.name,
            'status': self.status,
            'observations': self.observations}

