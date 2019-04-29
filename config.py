import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # La base de dato estará generada en la raiz del proyecto.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'disManagerApp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True