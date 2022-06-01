import os

from flask import Blueprint, redirect, url_for, request, flash
from werkzeug.utils import secure_filename

from common.config import config
from common.logger import log

upload = Blueprint('upload', __name__)


@upload.route('/upload', methods=['POST'])
def do():
    # upload file
    if not request.files['file'].filename:
        flash('Please provide a file')
        return redirect(url_for('home.show'))

    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(config.INPUT_FOLDER, filename))
        log.info('Saved file :' + filename)
        # select database
        database = request.form.get('database')

        return redirect(url_for('harmonize.do', filename=filename, database=database))
