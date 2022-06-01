import os

from flask import Blueprint, request, send_from_directory, abort
from werkzeug.exceptions import NotFound

from common.config import config

xml = Blueprint("xml", __name__)


@xml.route('/xml', methods=['GET'])
def download():
    filename = request.args.get('filename')
    if filename.startswith("\\") or filename.startswith("\\\\"):
        abort(404)

    try:
        return send_from_directory(os.path.join(config.OUTPUT_FOLDER, os.path.dirname(filename)),
                                   os.path.basename(filename),
                                   as_attachment=True)
    except NotFound:
        abort(404)
