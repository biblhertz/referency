from flask import Blueprint, request, redirect, url_for, render_template, abort, flash
from jinja2 import TemplateNotFound

from common.config import config
from common.user_session import manager as session_manager

results = Blueprint('results', __name__, template_folder='templates')


@results.route('/results', methods=['GET'])
def show():
    filename = request.args.get('filename')
    database = request.args.get('database')
    footnotes = session_manager.get_footnotes_for(filename)
    xml = request.args.get('xml')

    if not filename:
        flash('Please provide a file!')
        return redirect(url_for('home.show'))
    elif not database:
        flash('Please specify a database!')
        return redirect(url_for('home.show'))
    elif not footnotes:
        flash('Internal Error: no footnotes!')
        return redirect(url_for('home.show'))

    footnotes_matched_num = len([f for f in footnotes.values() if f])
    refs_matched_num = len([a for f in footnotes.values() if f for a in f])

    try:
        return render_template(
            'results.html',
            filename=filename,
            endpoints=config.ENDPOINTS,
            footnotes=footnotes,
            footnotes_matched_num=footnotes_matched_num,
            refs_matched_num=refs_matched_num,
            xml=xml
        )
    except TemplateNotFound:
        abort(404)
