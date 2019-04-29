from src import db

asignatura_area = db.Table('asignatura_area', db.metadata,
                           db.Column('cod_asig', db.Integer, db.ForeignKey('asignatura.cod_asignatura')),
                           db.Column('cod_area', db.String(64), db.ForeignKey('area_conocimiento.cod_area'))
                           )

asignatura_grupo = db.Table('asignatura_grupo', db.metadata,
                           db.Column('cod_asig', db.Integer, db.ForeignKey('asignatura.cod_asignatura')),
                           db.Column('cod_grupo', db.String(64), db.ForeignKey('grupo.cod_grupo'))
                           )

asignatura_profesor = db.Table('asignatura_profesor', db.metadata,
                           db.Column('cod_asig', db.Integer, db.ForeignKey('asignatura.cod_asignatura')),
                           db.Column('dni', db.String(64), db.ForeignKey('profesor.DNI'))
                           )

class Titulacion(db.Model):
    __tablename__ = "titulacion"

    cod_titulacion = db.Column(db.Integer, primary_key=True)
    acronimo = db.Column(db.String(64), index=True, unique=True)
    nombre = db.Column(db.String(64), index=True, unique=True)
    centro = db.Column(db.String(64))
    cod_plan = db.Column(db.String(64))
    cod_especial = db.Column(db.String(64))

    asignaturas = db.relationship('Asignatura', backref='titulacion', lazy='dynamic')

    def __repr__(self):
        return '<Titulacion: {} // {} // {} // {}>'.format(self.cod_titulacion, self.acronimo, self.nombre, self.centro)

class Asignatura(db.Model):
    __tablename__ = "asignatura"

    cod_asignatura = db.Column(db.Integer, primary_key=True)
    cod_titulacion = db.Column(db.Integer, db.ForeignKey('titulacion.cod_titulacion'))
    nombre = db.Column(db.String(64))
    curso = db.Column(db.Integer)
    cuatrimestre = db.Column(db.Integer)
    tipo = db.Column(db.String(64))

    pda = db.relationship('PDA', backref='asignatura', lazy='dynamic')

    areas_conocimientos = db.relationship('Area_conocimiento', secondary=asignatura_area, backref="asignatura")
    asignaturas_grupos = db.relationship('Grupo', secondary=asignatura_grupo, backref="asignatura")
    asignaturas_profesores = db.relationship('Profesor', secondary=asignatura_profesor, backref="asignatura")

    def __repr__(self):
        return '< Asignatura: {} // {} // {} >'.format(self.cod_titulacion, self.nombre, self.cod_asignatura)

class PDA(db.Model):
    __tablename__ = "PDA"

    id = db.Column(db.Integer, primary_key=True)
    cod_asig = db.Column(db.Integer, db.ForeignKey('asignatura.cod_asignatura'), unique=True)
    estado = db.Column(db.String(64))
    observaciones = db.Column(db.String(64))


class Profesor(db.Model):
    __tablename__ = "profesor"

    DNI = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64))
    apellidos = db.Column(db.String(64))
    tutorias = db.Column(db.String(140))
    potencial_docente = db.Column(db.String(64))
    horas_preasignadas = db.Column(db.Integer)

    asignatura_profesor = db.relationship('Asignatura', backref='profesor', lazy='dynamic')


class AreaConocimiento(db.Model):
    __tablename__ = "area_conocimiento"

    cod_area = db.Column(db.String(64), primary_key=True)
    nombre = db.Column(db.String(64), index=True, unique=True)
    asignaturas = db.relationship('asignatura', secondary=asignatura_area, backref="areas_conocimiento")

class Grupo (db.Model):
    __tablename__ = "grupo"

    cod_grupo = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(64))
    asignaturas_grupos = db.relationship('asignatura', secondary=asignatura_grupo, backref="grupo")

