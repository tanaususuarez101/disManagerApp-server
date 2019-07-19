from src import db, app
from sqlalchemy.exc import IntegrityError


belong = db.Table('belong', db.metadata,
                    db.Column('area_cod', db.String(64), db.ForeignKey('knowledgeArea.area_cod'), primary_key=True),
                    db.Column('subject_cod', db.String(64), db.ForeignKey('subject.subject_cod'), primary_key=True)
                  )


class VeniaI(db.Model):
    __tablename__ = "veniaI"

    area_cod = db.Column(db.String(64), db.ForeignKey('knowledgeArea.area_cod'), primary_key=True)
    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), primary_key=True)

    knowledgeArea = db.relationship('KnowledgeArea', back_populates='veniaI')
    teacher = db.relationship('Teacher', back_populates='veniaI')


class VeniaII(db.Model):
    __tablename__ = "veniaII"

    subject_cod = db.Column(db.String(64), db.ForeignKey('subject.subject_cod'), primary_key=True)
    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), primary_key=True)

    subject = db.relationship('Subject', back_populates='veniaII')
    teacher = db.relationship('Teacher', back_populates='veniaII')


class Subject(db.Model):
    __tablename__ = "subject"

    subject_cod = db.Column(db.String(64), primary_key=True)
    coordinator_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'))
    practice_responsible_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'))
    university_cod = db.Column(db.String(64), db.ForeignKey('universityDegree.university_cod'))

    academic_year = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    course = db.Column(db.String(64), nullable=False)
    semester = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64), nullable=False)

    coordinator = db.relationship('Teacher', foreign_keys=[coordinator_dni])
    practice_responsible = db.relationship('Teacher', foreign_keys=[practice_responsible_dni])
    group = db.relationship('Group', back_populates="subject", cascade="all,delete")
    knowledgeArea = db.relationship('KnowledgeArea', secondary=belong, back_populates="subject")
    university_degree = db.relationship('UniversityDegree', back_populates="subject")
    PDA = db.relationship('PDA', back_populates="subject", uselist=False, cascade="all, delete-orphan")
    veniaII = db.relationship('VeniaII', back_populates='subject')


    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def __repr__(self):
        return '<Asignatura: cod: {}, name: {}>'.format(self.subject_cod, self.name)


class Group(db.Model):
    __tablename__ = "group"

    group_cod = db.Column(db.String(64), primary_key=True)
    subject_cod = db.Column(db.String(64), db.ForeignKey('subject.subject_cod'), primary_key=True)

    type = db.Column(db.String(64))
    hours = db.Column(db.String(64))

    subject = db.relationship('Subject', back_populates='group')
    teacher = db.relationship('Impart', back_populates='group')

    def __init__(self, group_code=None, subject_cod=None, area_cod=None, type=None, hours=None):
        if group_code and subject_cod and area_cod:
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

    @staticmethod
    def get_all():
        return Group.query.all()

    def to_dict(self):
        return {
            'group_cod': self.group_cod,
            'subject_cod': self.subject_cod,
            'area_cod': self.area_cod,
            'group_type': self.type,
            'group_hours': self.hours
        }


class Impart(db.Model):
    __tablename__ = "impart"

    group_cod = db.Column(db.String(64), primary_key=True)
    subject_cod = db.Column(db.String(64), primary_key=True)
    __table_args__ = (db.ForeignKeyConstraint([group_cod, subject_cod], ['group.group_cod', 'group.subject_cod']), {})

    teacher_dni = db.Column(db.String(64), db.ForeignKey('teacher.dni'), primary_key=True)

    hours = db.Column(db.String(64))
    state_solicitation = db.Column(db.String(64))

    teacher = db.relationship('Teacher', back_populates='group')
    group = db.relationship('Group', back_populates='teacher')

    def __init__(self, group=None, teacher=None, hours=None, state_solicitation='pendiente'):
        if group and teacher and hours:
            self.teacher = teacher
            self.group = group
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

    def to_dict(self):
        return {'group_cod': self.group_cod, 'subject_cod': self.subject_cod, 'area_cod': self.area_cod, 'teacher_dni':
                self.teacher_dni, 'assigned_hours': self.hours, 'state_solicitation': self.state_solicitation}


class Teacher(db.Model):
    __tablename__ = "teacher"

    dni = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    area_cod = db.Column(db.String(64), db.ForeignKey('knowledgeArea.area_cod'), nullable=True)

    group = db.relationship('Impart', back_populates='teacher')
    area = db.relationship('KnowledgeArea', back_populates='teacher')
    veniaI = db.relationship('VeniaI', back_populates='teacher')
    veniaII = db.relationship('VeniaII', back_populates='teacher')

    def __repr__(self):
        return '<Profesor: dni: {}, nombre: {}>'.format(self.dni, self.name)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False


class KnowledgeArea(db.Model):
    __tablename__ = "knowledgeArea"

    area_cod = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    teacher = db.relationship('Teacher', backref='knowledgeArea', cascade="all,delete")
    subject = db.relationship('Subject', secondary=belong, back_populates="knowledgeArea")

    veniaI = db.relationship('VeniaI', back_populates='knowledgeArea')

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
        return {'university_cod': self.university_degree_cod, 'university_acronym': self.acronym,
                'university_name': self.name, 'university_study_center': self.study_center, 'university_plan_cod':
                    self.plan_cod, 'university_special_cod': self.special_cod}


class PDA(db.Model):
    __tablename__ = "PDA"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_cod = db.Column(db.Integer, db.ForeignKey('subject.subject_cod'), unique=True, nullable=False)
    status = db.Column(db.String(64))
    observations = db.Column(db.String(128))

    subject = db.relationship('Subject', back_populates='PDA')

    def __init__(self, subject_cod=None, status=None, observations=None):
        self.subject_cod = subject_cod
        self.status = status
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
