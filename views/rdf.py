import os
import subprocess

from flask import Blueprint, request, abort, send_from_directory
from werkzeug.exceptions import NotFound

from common.config import config
from common.logger import log

rdf = Blueprint('rdf', __name__)


@rdf.route('/rdf', methods=['GET'])
def download():
    xml = request.args.get('filename')
    if xml.startswith("\\") or xml.startswith("\\\\"):
        abort(404)
    try:
        rdf_dir = os.path.join(config.OUTPUT_FOLDER, os.path.dirname(xml), 'rdf')
        os.makedirs(rdf_dir, exist_ok=True)
        o_rdf = os.path.basename(xml).split(".")[0] + '.rdf'

        cmd = 'java -jar ' + config.X3ML_BIN_PATH + ' -i ' \
              + os.path.join(config.OUTPUT_FOLDER, xml) \
              + ' -x ' + config.X3ML_MAPPINGS_FILE + ' -p ' + config.X3ML_POLICY_FILE \
              + ' -o ' + os.path.join(rdf_dir, o_rdf)
        log.info(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        p.communicate()

        return send_from_directory(rdf_dir, o_rdf, as_attachment=True)
    except NotFound:
        abort(404)
