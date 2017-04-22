import os


class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))

    CSRF_ENABLED = True
    SECRET_KEY = os.urandom(16)

    database_uri = os.environ.get('DATABASE_URL')
    if database_uri is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    else:
        SQLALCHEMY_DATABASE_URI = database_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    OWM_APIKEY = os.environ.get('OWM_APIKEY')
    OWM_CITYID = os.environ.get('OWM_CITYID')

    BOT_TOKEN = os.environ.get('BOT_TOKEN')

    REQUEST_TOKEN = os.environ.get('REQUEST_TOKEN')


class ProductionConfig(Config):
    DEBUG = False


class DevelopConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    REQUEST_TOKEN = '2128506'
