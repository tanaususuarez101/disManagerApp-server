from src import db, app
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
import json
'''
    Entities Relationships 
'''


class Impart(db.Model):
    __tablename__ = "impart"

    group_cod = db.Column(db.String(64), primary_key=True)
    subject_cod = db.Column(db.String(64), primary_key=True)
    area_cod = db.Column(db.String(64), primary_key=True)
    __table_args__ = (db.ForeignKeyConstraint([group_cod, subject_cod, area_cod], ['group.group_cod',
                                                                                   'group.subject_cod',
                                                                                   'group.area_cod'
                                                                                   ]), {})

    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), primary_key=True)

    hours = db.Column(db.String(64))
    state_solicitation = db.Column(db.String(64))

    teacher = db.relationship('Teacher', back_populates='group')
    group = db.relationship('Group', back_populates='teacher')

    def __init__(self, group=None, teacher=None, hours=None, state_solicitation='pendiente'):
        self.group = group
        self.teacher = teacher
        self.hours = hours
        self.state_solicitation = state_solicitation

    def __repr__(self):
        return '<group: {}, Teacher: {}>'.format(self.group, self.teacher_dni)

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
    def get(group=None, teacher=None):
        if group and teacher:
            return Impart.query.get([group.group_cod, group.subject_cod, group.area_cod, teacher.dni])

    def to_dict(self):
        return {'group_cod': self.group_cod, 'subject_cod': self.subject_cod, 'area_cod': self.area_cod, 'teacher_dni':
                self.teacher_dni, 'assigned_hours': self.hours, 'state_solicitation': self.state_solicitation}


class VeniaI(db.Model):
    __tablename__ = "veniaI"

    area_cod = db.Column(db.String(64), db.ForeignKey('knowledgeArea.area_cod'), primary_key=True)
    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), primary_key=True)

    knowledgeArea = db.relationship('KnowledgeArea', back_populates='veniaI')
    teacher = db.relationship('Teacher', back_populates='veniaI')

    def __init__(self, area, teacher):
        self.knowledgeArea = area
        self.teacher = teacher

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

    def to_dict(self):
        return {'area_cod': self.area_cod, 'teacher_dni': self.teacher_dni}


class VeniaII(db.Model):
    __tablename__ = "veniaII"

    subject_cod = db.Column(db.String(64), primary_key=True)
    area_cod = db.Column(db.String(64), primary_key=True)
    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), primary_key=True)

    __table_args__ = (db.ForeignKeyConstraint([subject_cod, area_cod], ['subject.subject_cod', 'subject.area_cod']), {})

    subject = db.relationship('Subject', back_populates='veniaII')
    teacher = db.relationship('Teacher', back_populates='veniaII')

    def __init__(self, subject, teacher):
        self.subject = subject
        self.teacher = teacher

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

    def to_dict(self):
        return {'subject_cod': self.subject_cod, 'teacher_dni': self.teacher_dni}


'''
    Entities Models
'''


class Subject(db.Model):
    __tablename__ = "subject"

    subject_cod = db.Column(db.String(64), primary_key=True)
    area_cod = db.Column(db.String(64), db.ForeignKey('knowledgeArea.area_cod'), primary_key=True)
    university_cod = db.Column(db.String(64), db.ForeignKey('universityDegree.university_cod'))
    coordinator_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'))
    responsible_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'))

    academic_year = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    course = db.Column(db.String(64), nullable=False)
    semester = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64), nullable=False)

    knowledgeArea = db.relationship('KnowledgeArea', back_populates='subject')
    university_degree = db.relationship('UniversityDegree', back_populates="subject")
    coordinator = db.relationship('Teacher', foreign_keys=[coordinator_dni])
    responsible = db.relationship('Teacher', foreign_keys=[responsible_dni])
    group = db.relationship('Group', back_populates="subject", cascade="all,delete")
    PDA = db.relationship('PDA', back_populates="subject", uselist=False, cascade="all, delete-orphan")
    veniaII = db.relationship('VeniaII', back_populates='subject')

    def __init__(self, subject_cod=None, area_cod=None, university_cod=None, name=None, type=None, semestre=None,
                 course=None, academic_year=None):
        self.subject_cod = subject_cod
        self.area_cod = area_cod
        self.university_cod = university_cod
        self.name = name if not name else name.lower()
        self.type = type if not type else type.lower()
        self.semester = semestre
        self.course = course
        self.academic_year = academic_year

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def __repr__(self):
        return '<Asignatura: cod: {}, name: {}>'.format(self.subject_cod, self.name)

    @staticmethod
    def all():
        return Subject.query.all()

    @staticmethod
    def get(subject_cod=None, area_cod=None):
        return Subject.query.get([subject_cod, area_cod])

    def to_dict(self):
        return {'subject_cod': self.subject_cod, 'area_cod': self.area_cod, 'university_cod': self.university_cod,
                'coordinator_dni': self.coordinator_dni, 'responsible_dni': self.responsible_dni, 'subject_academic_year':
                self.academic_year, 'subject_name': self.name, 'subject_course': self.course, 'subject_semester':
                self.semester, 'subject_type': self.type}


class Group(db.Model):
    __tablename__ = "group"

    group_cod = db.Column(db.String(64), primary_key=True)
    subject_cod = db.Column(db.String(64), primary_key=True)
    area_cod = db.Column(db.String(64), primary_key=True)

    __table_args__ = (db.ForeignKeyConstraint([subject_cod, area_cod], ['subject.subject_cod', 'subject.area_cod']), {})

    type = db.Column(db.String(64))
    hours = db.Column(db.String(64))

    subject = db.relationship('Subject', back_populates='group')
    teacher = db.relationship('Impart', back_populates='group')

    def __init__(self, subject=None, group_code=None, type=None, hours=None):
        self.subject = subject
        self.group_cod = group_code
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
    def all():
        return Group.query.all()

    @staticmethod
    def get(area_cod=None, subject_cod=None, group_cod=None):
        if group_cod and subject_cod and area_cod:
            return Group.query.get([group_cod, subject_cod, area_cod])

    def to_dict(self):
        return {'group_cod': self.group_cod, 'subject_cod': self.subject_cod, 'area_cod': self.area_cod,
                'group_type': self.type, 'group_hours': self.hours}


class Teacher(db.Model):
    __tablename__ = "teacher"

    dni = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    surnames = db.Column(db.String(64), nullable=True)
    area_cod = db.Column(db.String(64), db.ForeignKey('knowledgeArea.area_cod'), nullable=True)
    potential = db.Column(db.String(64), nullable=True)
    tutorial_hours = db.Column(db.String(64), nullable=True)

    group = db.relationship('Impart', back_populates='teacher')
    knowledgeArea = db.relationship('KnowledgeArea', back_populates='teacher', uselist=False)
    veniaI = db.relationship('VeniaI', back_populates='teacher')
    veniaII = db.relationship('VeniaII', back_populates='teacher')
    user = db.relationship('User', back_populates='teacher')
    tutorial = db.relationship('Tutorial', back_populates='teacher', uselist=False)

    def __init__(self, dni=None, name=None, surnames=None, potential=None, tutorial_hours=None, area=None):
        self.dni = dni
        self.name = name
        self.surnames = surnames
        self.potential = potential
        self.tutorial_hours = tutorial_hours
        self.knowledgeArea = area

    def __repr__(self):
        return '<Profesor: dni: {}, nombre: {}>'.format(self.dni, self.name)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def update(self, data):
        if not data:
            return None

        try:
            self.dni = data['teacher_dni']
            self.name = data['teacher_name']
            self.surnames = data['teacher_surnames']
            self.area_cod = data['area_cod']
            self.potential = data['teacher_potential']
            self.tutorial_hours = data['tutorial_hours']

        except Exception as e:
            return None

    @staticmethod
    def all():
        return Teacher.query.all()

    @staticmethod
    def get(teacher_dni=None):
        return Teacher.query.get(teacher_dni)

    def to_dict(self):
        return {'teacher_dni': self.dni, 'teacher_name': self.name, 'area_cod': self.area_cod,
                'teacher_surnames': self.surnames, 'teacher_potential': self.potential, 'tutorial_hours':
                    self.tutorial_hours}


class KnowledgeArea(db.Model):
    __tablename__ = "knowledgeArea"

    area_cod = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    teacher = db.relationship('Teacher', back_populates='knowledgeArea', cascade="all,delete")
    subject = db.relationship('Subject', back_populates="knowledgeArea", cascade='all,delete')

    veniaI = db.relationship('VeniaI', back_populates='knowledgeArea')

    def __init__(self, area_cod=None, name=None):
        self.area_cod = area_cod
        self.name = name

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def all():
        return KnowledgeArea.query.all()

    @staticmethod
    def get(area_cod=None):
        return KnowledgeArea.query.get(area_cod)

    def to_dict(self):
        return {'area_cod': self.area_cod, 'area_name': self.name}


class UniversityDegree(db.Model):
    __tablename__ = "universityDegree"

    university_cod = db.Column(db.String(64), primary_key=True)
    acronym = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)
    study_center = db.Column(db.String(64))
    plan_cod = db.Column(db.String(64))
    special_cod = db.Column(db.String(64))

    subject = db.relationship('Subject', backref='UniversityDegree', cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, university_degree_cod=None, name=None, plan_code=None, specialty_cod=None, acronym=None,
                 study_center=None):

        self.university_cod = university_degree_cod
        self.plan_cod = plan_code
        self.special_cod = specialty_cod
        self.acronym = acronym
        self.name = name
        self.study_center = study_center

    def __repr__(self):
        return '<Titulacion {}, {}>'.format(self.university_cod, self.name)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def get(university_cod=None):
        if university_cod:
            return UniversityDegree.query.get(university_cod)

    @staticmethod
    def all():
        return UniversityDegree.query.all()

    def to_dict(self):
        return {'university_cod': self.university_cod, 'university_acronym': self.acronym, 'university_name': self.name,
                'university_study_center': self.study_center, 'university_plan_cod': self.plan_cod,
                'university_special_cod': self.special_cod}


class PDA(db.Model):
    __tablename__ = "PDA"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_cod = db.Column(db.String(64), nullable=False)
    area_cod = db.Column(db.String(64), nullable=False)

    __table_args__ = (db.ForeignKeyConstraint([subject_cod, area_cod], ['subject.subject_cod', 'subject.area_cod']), {})

    status = db.Column(db.String(64))
    observations = db.Column(db.String(128))

    subject = db.relationship('Subject', back_populates='PDA', uselist=False)

    def __init__(self, subject=None, status='pendiente', observations=None):
        self.subject = subject
        self.status = status if not status else status.lower()
        self.observations = observations if not observations else status.lower()

    def __repr__(self):
        return '<PDA id: {}, subject_cod: {}, status: {}, observations: {} >'.format(self.id, self.subject_cod,
                                                                                     self.status, self.observations)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def all():
        return PDA.query.all()

    @staticmethod
    def get(area_cod=None):
        return PDA.query.get(area_cod)

    def to_dict(self):
        return {
            'subject_cod': self.subject_cod,
            'subject_name': self.subject.name,
            'pda_status': self.status,
            'pda_observations': self.observations}


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), index=True, unique=True, nullable=True)
    isAdmin = db.Column(db.Boolean, default=False, nullable=False)
    public_id = db.Column(db.String(50), unique=True)

    teacher = db.relationship('Teacher', back_populates='user', uselist=False)

    def __init__(self, username=None, password=None, is_admin=False, public_id=None):
        if username and password and public_id:
            self.username = username
            self.password = password
            self.isAdmin = is_admin
            self.public_id = public_id

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def update(self, data):
        if not data:
            return None
        try:
            self.password = generate_password_hash(data['password'], method='sha256') if data['password'] else self.password
            self.isAdmin = data['isAdmin']
            self.teacher_dni = data['teacher_dni'] if data['teacher_dni'] else None
            return self
        except Exception as e:
            return None


    @staticmethod
    def all():
        return User.query.all()

    @staticmethod
    def get(dni=None, username=None):
        if dni:
            return User.query.filter_by(teacher_dni=dni).first()
        if username:
            return User.query.filter_by(username=username).first()

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'teacher_dni': self.teacher_dni, "isAdmin": self.isAdmin}


class Tutorial(db.Model):
    __tablename__ = "tutorial"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), index=True, unique=True, nullable=False)
    first_semester = db.Column(db.String(128))
    second_semester = db.Column(db.String(128))
    hours = db.Column(db.String(50))

    teacher = db.relationship('Teacher', back_populates='tutorial', uselist=False)

    def __init__(self, first_semester=None, second_semester=None, hours=None):
        self.hours = hours

        if first_semester:
            self.first_semester = first_semester
        if second_semester:
            self.second_semester = second_semester

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def get(dni=None):
        if dni:
            return Tutorial.query.filter_by(teacher_dni=dni).first()

    def to_dict(self):
        return {'first_semester': json.loads(self.first_semester), 'second_semester': json.loads(self.second_semester),
                'hours': self.hours}
