from src import db
from sqlalchemy.exc import IntegrityError

Tiene = db.Table('Tiene', db.metadata,
                            db.Column('cod_asignatura', db.Integer, db.ForeignKey('asignatura.cod_asignatura')),
                            db.Column('cod_area', db.String(64), db.ForeignKey('areaconocimiento.cod_area'))
                           )

class Titulacion(db.Model):
    __tablename__ = "titulacion"

    cod_titulacion = db.Column(db.Integer, primary_key=True)
    acronimo = db.Column(db.String(64), index=True, unique=True)
    nombre = db.Column(db.String(64), index=True, unique=True)
    centro = db.Column(db.String(64))
    cod_plan = db.Column(db.String(64))
    cod_especial = db.Column(db.String(64))

    asignaturas = db.relationship('Asignatura', backref='Titulacion', lazy='dynamic')

    def __init__(self, universityDegreeCode=None, planCode=None, specialtyCode=None, acronym=None,
                 name=None, studyCenter=None):

        self.cod_titulacion = universityDegreeCode
        self.cod_plan = planCode
        self.cod_especial = specialtyCode
        self.acronimo = acronym
        self.nombre = name
        self.centro = studyCenter

    def __repr__(self):
        return '<Titulacion {}, {}>'.format(self.cod_titulacion, self.nombre)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(universityDegreeCode=None):
        if universityDegreeCode:
            return Titulacion.query.get(universityDegreeCode)

    def add_subject(self, subject=None):
        if subject:
            self.asignaturas.append(subject)

class Asignatura(db.Model):
    __tablename__ = "asignatura"

    cod_asignatura = db.Column(db.Integer, primary_key=True)
    cod_titulacion = db.Column(db.Integer, db.ForeignKey('titulacion.cod_titulacion'))
    nombre = db.Column(db.String(64))
    curso = db.Column(db.Integer)
    cuatrimestre = db.Column(db.Integer)
    tipo = db.Column(db.String(64))

    titulacion = db.relationship('Titulacion', back_populates="asignaturas")
    areasConocimientos = db.relationship('AreaConocimiento', secondary=Tiene, backref="asignatura")
    grupos = db.relationship('Asignado', back_populates="asignatura")
    PDA = db.relationship('PDA', backref='asignatura', lazy='dynamic')


    def __init__(self, subject_code=None, name=None, semester=None,academic_year=None, type=None):

        self.cod_asignatura = subject_code
        self.nombre = name
        self.curso = academic_year
        self.cuatrimestre = semester
        self.tipo = type

    def __repr__(self):
        return '<Asignatura {}, {}>'.format(self.cod_asignatura, self.nombre)

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
            return Asignatura.query.get(subject)

    def create_relactionship(self, area=None, university_degree=None, PDA=None):


        if area:
            self.areasConocimientos.append(area)
        if university_degree:
            self.titulacion = university_degree
        if PDA:
            self.PDA = PDA

    def getId(self):
        return self.cod_asignatura

class Grupo (db.Model):
    __tablename__ = "grupo"

    cod_grupo = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(64))
    asignaturas = db.relationship('Asignado', back_populates="grupo")

    def __init__(self, group_code=None, type=None):

        self.cod_grupo = group_code
        self.tipo = type

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get(group=None):
        if group:
            return Grupo.query.get(group)

    @staticmethod
    def add(data=[]):
        if len(data) == 2:
            grupo = Grupo.query.get(data[0])
            if not grupo:
                grupo = Grupo(cod_grupo=data[0], tipo=data[1])
                db.session.add(grupo)
                db.session.commit()
            return grupo

    def getId(self):
        return self.cod_grupo

class AreaConocimiento(db.Model):
    __tablename__ = "areaconocimiento"

    cod_area = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True, unique=True)

    def __init__(self, area_code=None, name=None):
        self.cod_area = area_code
        self.nombre = name

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def get(area=None):
        if area:
            return AreaConocimiento.query.get(area)

class PDA(db.Model):
    __tablename__ = "PDA"

    id = db.Column(db.Integer, primary_key=True)
    cod_asig = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asignatura'), unique=True)
    estado = db.Column(db.String(64))
    observaciones = db.Column(db.String(64))

class Profesor(db.Model):
    __tablename__ = "profesor"

    DNI = db.Column(db.String(64), primary_key=True)
    nombre = db.Column(db.String(64))
    apellidos = db.Column(db.String(64))
    tutorias = db.Column(db.String(140))
    potencial_docente = db.Column(db.String(64))
    horas_preasignadas = db.Column(db.Integer)

    asignados = db.relationship('Imparte', back_populates='profesor')

class Asignado(db.Model):
    __tablename__ = "asignado"

    cod_grupo = db.Column(db.Integer, db.ForeignKey('grupo.cod_grupo'), primary_key=True)
    cod_asignatura = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asignatura'), primary_key=True)
    num_horas = db.Column(db.Integer)
    horario = db.Column(db.String(140))

    asignatura = db.relationship('Asignatura', back_populates='grupos')
    grupo = db.relationship('Grupo', back_populates='asignaturas')
    profesor = db.relationship('Imparte', back_populates='asignado')

    def __init__(self, hours_numbers=None, schedule=None):
        self.num_horas = hours_numbers
        self.horario = schedule

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
            return Asignado.query.get([group.getId(), subject.getId()])


class Imparte(db.Model):
    __tablename__ = "imparte"

    DNI = db.Column(db.String(64), db.ForeignKey('profesor.DNI'), primary_key=True)
    cod_grupo = db.Column(db.Integer, primary_key=True)
    cod_asignatura = db.Column(db.Integer, primary_key=True)

    coor_asignatura = db.Column(db.Boolean, default=False)
    respon_practica = db.Column(db.Boolean, default=False)
    venia = db.Column(db.Boolean, default=False)
    confirmado = db.Column(db.Boolean, default=False)

    __table_args__ = (db.ForeignKeyConstraint([cod_grupo, cod_asignatura],
                                           ['asignado.cod_grupo', 'asignado.cod_asignatura']), {})

    profesor = db.relationship('Profesor', back_populates='asignados')
    asignado = db.relationship('Asignado', back_populates='profesor')

