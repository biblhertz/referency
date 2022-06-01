import os

from flask import Blueprint, request, url_for, redirect, abort
from jinja2 import TemplateNotFound

import common.db as db
import common.jats as jats
import common.tei as tei
import common.utils as utils
from common.config import config
from common.logger import log
from common.user_session import manager as session_manager

harmonize = Blueprint('harmonize', __name__)


@harmonize.route('/harmonize', methods=['GET'])
def do():
    filename = request.args.get('filename')
    file = os.path.join(config.INPUT_FOLDER, filename)
    log.info("File uploaded: {filename}".format(filename=file))

    database = request.args.get('database')
    log.info("Searching in : {database}".format(database=database))

    is_tei, path = utils.meTypeset(file)
    log.info("Transformed file {filename} using meTypeset".format(filename=file))

    xml_update = None
    if is_tei:
        footnotes = tei.parse(path)
        log.info("Parsed TEI file {tei_path}".format(tei_path=path))
        xml_update = tei.update
    else:
        footnotes = jats.parse(path)
        log.info("Parsed JATS file {jats_path}".format(jats_path=path))
        xml_update = jats.update

    footnotes = utils.extract_citations(footnotes)
    log.info("Extracted probable titles")

    log.info("Checking References against {db}".format(db=database))
    footnotes = db.check(database, footnotes)
    session_manager.set_footnotes_for(file, footnotes, True)
    session_manager.set_outfile_for(file, path, xml_update)
    enriched_xml_path = xml_update(path, [ref for key, value in footnotes.items() for ref in value])

    try:
        return redirect(url_for('results.show', filename=filename, database=database,
                                xml=os.path.relpath(enriched_xml_path, config.OUTPUT_FOLDER)))
    except TemplateNotFound:
        abort(404)
