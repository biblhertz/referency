import os

from flask import session

from common.config import config

FOOTNOTES_SESSION_KEY = 'footnotes'
OUTFILE_KEY = 'outfile'
UPDATE_FN_KEY = 'update_fn'


def get_footnotes_for(filename):
    filepath = os.path.join(config.INPUT_FOLDER, filename)
    file_hash = hash(os.path.getsize(filepath))
    return session[file_hash][FOOTNOTES_SESSION_KEY] \
        if file_hash in session and FOOTNOTES_SESSION_KEY in session[file_hash] \
        else None


def set_footnotes_for(file_path, footnotes, clear=False):
    file_hash = hash(os.path.getsize(file_path))
    if clear:
        session[file_hash] = dict()
    session[file_hash][FOOTNOTES_SESSION_KEY] = footnotes


def set_outfile_for(file_path, outfile, update_fn):
    file_hash = hash(os.path.getsize(file_path))
    session[file_hash] = dict() if file_hash not in session else session[file_hash]
    session[file_hash][OUTFILE_KEY] = outfile
    session[file_hash][UPDATE_FN_KEY] = update_fn


def get_outfile_for(filename):
    filepath = os.path.join(config.INPUT_FOLDER, filename)
    file_hash = hash(os.path.getsize(filepath))
    outfile = session[file_hash][OUTFILE_KEY] if file_hash in session and OUTFILE_KEY in session[
        file_hash] else None
    xml_update = session[file_hash][UPDATE_FN_KEY] if file_hash in session and UPDATE_FN_KEY in session[
        file_hash] else None

    return outfile, xml_update
