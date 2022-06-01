import os

from flask import Blueprint, abort, request, send_from_directory
from werkzeug.exceptions import NotFound

from common.config import config
from common.dois_utils import to_bibtex
from common.user_session import manager as session_manager

bib = Blueprint("bib", __name__)


@bib.route('/bib', methods=['GET'])
def download():
    filename = request.args.get('filename')
    xml = request.args.get('xml')

    if xml.startswith("\\") or xml.startswith("\\\\"):
        abort(404)
    try:
        bib_dir = os.path.join(config.OUTPUT_FOLDER, os.path.dirname(xml), 'bib')
        os.makedirs(bib_dir, exist_ok=True)

        footnotes = session_manager.get_footnotes_for(filename)
        o_bib = to_bibtex(bib_dir, [citation for footnote, citations in footnotes.items() for citation in citations])
        return send_from_directory(bib_dir, os.path.basename(o_bib), as_attachment=True)
    except NotFound:
        abort(404)
