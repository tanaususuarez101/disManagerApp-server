from src import db

Tiene = db.Table('Tiene', db.metadata,
                            db.Column('cod_asignatura', db.Integer, db.ForeignKey('asignatura.cod_asignatura')),
                            db.Column('cod_area', db.String(64), db.ForeignKey('areaconocimiento.cod_area'))
                           )

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

class Grupo (db.Model):
    __tablename__ = "grupo"

    cod_grupo = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(64))
    asignaturas = db.relationship('Asignado', back_populates="grupo")

class AreaConocimiento(db.Model):
    __tablename__ = "areaconocimiento"

    cod_area = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True, unique=True)

class Titulacion(db.Model):
    __tablename__ = "titulacion"

    cod_titulacion = db.Column(db.Integer, primary_key=True)
    acronimo = db.Column(db.String(64), index=True, unique=True)
    nombre = db.Column(db.String(64), index=True, unique=True)
    centro = db.Column(db.String(64))
    cod_plan = db.Column(db.String(64))
    cod_especial = db.Column(db.String(64))

    asignaturas = db.relationship('Asignatura', backref='Titulacion', lazy='dynamic')

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


