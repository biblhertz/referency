from flask import Blueprint, abort
from flask import render_template
from jinja2 import TemplateNotFound

from common.config import config

home = Blueprint('home', __name__, template_folder='templates')


@home.route('/', methods=['GET'])
def show():
    try:
        return render_template('home.html', endpoints=config.ENDPOINTS)
    except TemplateNotFound:
        abort(404)
