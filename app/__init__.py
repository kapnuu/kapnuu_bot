import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

settings = os.environ.get('APP_SETTINGS')
if settings is None:
    settings = 'DevelopConfig'
app.logger.info('Loading %s' % settings)
app.config.from_object('config.' + settings)

db = SQLAlchemy(app)

if os.environ.get('HEROKU') is None:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/kapnuu_bot.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('kapnuu_bot startup @ localhost')
else:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('kapnuu_bot startup @ heroku')

from app import views
