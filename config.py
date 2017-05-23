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

    HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME')

    BOT_TZ_OFFSET = os.environ.get('BOT_TZ_OFFSET')


class ProductionConfig(Config):
    DEBUG = False


class DevelopConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    BOT_TZ_OFFSET = 3 * 60 * 60

    try:
        with open('token.txt') as f:
            BOT_TOKEN = f.readline().strip()
            REQUEST_TOKEN = f.readline().strip()
    except:
        pass
