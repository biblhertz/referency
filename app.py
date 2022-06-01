import os
import sys

import flask

import common.utils as utils
from common.config import config
from common.logger import log
from flask_session import Session

sess = Session()
sys.setrecursionlimit(100_000)

def create_app():
    app = flask.Flask(__name__, instance_relative_config=False)
    log.info('User configuration will be read from %s', os.path.expanduser(config.CFG_FILE_USER))
    log.info('Environment: ' + app.config['ENV'])

    app.config.update(
        SESSION_PERMANENT=config.SESSION_PERMANENT,
        PERMANENT_SESSION_LIFETIME=config.PERMANENT_SESSION_LIFETIME,
        SESSION_TYPE=config.SESSION_TYPE,
        SECRET_KEY=config.SECRET_KEY
    )

    if config.SESSION_PERMANENT:
        log.info('Session: permanent')
        sess.init_app(app)
    else:
        log.info('Session: non permanent')

    from views.home import home
    from views.results import results
    from views.upload import upload
    from views.complement import complement
    from views.harmonize import harmonize
    from views.xml import xml
    from views.rdf import rdf
    from views.bib import bib

    app.register_blueprint(home)
    app.register_blueprint(results)
    app.register_blueprint(upload)
    app.register_blueprint(complement)
    app.register_blueprint(harmonize)
    app.register_blueprint(xml)
    app.register_blueprint(rdf)
    app.register_blueprint(bib)

    if app.config['ENV'] != 'development':
        utils.NameDatasetSingleton.get_instance()

    utils.create_workspace()

    log.info('RefHar setup was successful')
    return app
