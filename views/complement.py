import copy
import os

from flask import Blueprint, request, redirect, url_for, abort
from jinja2 import TemplateNotFound

import common.db as db
import common.utils as utils
from common.config import config
from common.logger import log
from common.misc import fields
from common.user_session import manager as session_manager

complement = Blueprint('complement', __name__)


@complement.route('/complement', methods=['GET'])
def do():
    filename = request.args.get('filename')
    file = os.path.join(config.INPUT_FOLDER, filename)
    database = request.args.get('database')

    log.info('Running complementary search for file {f} in {d}'.format(f=filename, d=database))

    session_restored_footnotes = session_manager.get_footnotes_for(filename)
    session_restored_outfile, session_restored_xml_update = session_manager.get_outfile_for(filename)

    if session_restored_footnotes is None:
        return redirect(url_for('home'))

    footnotes = copy.deepcopy(session_restored_footnotes)
    footnotes = utils.extract_citations(footnotes)

    # since this is a complementary search, we want to keep the citations already matched using
    # some other service, hence after extracting the citations info from the restored footnotes,
    # we manually insert the ones already matched.
    for footnote, citations in footnotes.items():
        for citation in citations:
            for restored_values in session_restored_footnotes[footnote]:
                if fields.TITLE in citation and utils.similar_titles(citation[fields.TITLE],
                                                                     restored_values[fields.TITLE]):
                    footnotes[footnote].remove(citation)
                    footnotes[footnote].append(restored_values)

    footnotes = db.check(database, footnotes)
    enriched_xml_path = session_restored_xml_update(session_restored_outfile,
                                                    [ref for key, value in footnotes.items() for ref in value])

    session_manager.set_footnotes_for(file, footnotes)

    try:
        return redirect(url_for('results.show', filename=filename, database=database,
                                xml=os.path.relpath(enriched_xml_path, config.OUTPUT_FOLDER)))
    except TemplateNotFound:
        abort(404)
