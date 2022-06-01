import configparser
import os
import tempfile
from datetime import timedelta

from environs import Env

env = Env()
env.read_env()

CFG_FILE_USER = env.str("REFCY_CONF", default="config.ini")
SECRET_KEY = env.str('REFCY_SECRET_KEY', default='dev')

# raw config parser so as not to format config's keys
config = configparser.RawConfigParser()
config.optionxform = str

# application level config
config.read('dev.config.ini')
# user level config
config.read(CFG_FILE_USER)

if config['LOGGING'].getboolean('UseOsTempFolder'):
    TEMP_FOLDER = os.path.join(tempfile.gettempdir(), config['LOGGING']['LogsFolderName'])
else:
    TEMP_FOLDER = os.path.join(os.path.abspath(config['APP']['ProjectRoot']), config['LOGGING']['LogsFolderName'])

LOG_FILE = os.path.join(TEMP_FOLDER, config['LOGGING']['LogsFileName'])
LOG_LEVEL = config['LOGGING']['LogLevel']

METYPESET_BIN_PATH = os.path.abspath(config['APP']['MeTypesetPath'])
X3ML_BIN_PATH = os.path.abspath(config['APP']['X3mlPath'])

X3ML_MAPPINGS_FILE = os.path.join(os.path.abspath(config['APP']['ProjectRoot']), 'x3ml', 'mappings.x3ml')
X3ML_POLICY_FILE = os.path.join(os.path.abspath(config['APP']['ProjectRoot']), 'x3ml', 'generator-policy.xml')

WORKSPACE = os.path.abspath(config['APP']['Workspace'])

INPUT_FOLDER = os.path.join(WORKSPACE, config['WORKSPACE']['InputFolderName'])
OUTPUT_FOLDER = os.path.join(WORKSPACE, config['WORKSPACE']['OutputFolderName'])
INTER_FOLDER = os.path.join(WORKSPACE, config['WORKSPACE']['InterFolderName'])

JATS_FOLDER = config['WORKSPACE']['JatsFolderName']
TEI_FOLDER = config['WORKSPACE']['TeiFolderName']

TEI_FOOTNOTE_TAG = config['TEI_PARSE']['NodeTagName']
TEI_ITALICS_NODE_TAG = config['TEI_PARSE']['ItalicsTag']

JATS_FOOTNOTE_TAG = config['JATS_PARSE']['NodeTagName']
JATS_PARAGRAPH_TAG = config['JATS_PARSE']['ParagraphNode']
JATS_EXT_LINK_TAG = config['JATS_PARSE']['ExtLinkNode']

ALLOWED_DOC_FORMATS = config['WORKSPACE']['SupportedDocumentFormats'].split(',')

OPENCITATIONS_ENDPOINT = config['OPENCITATIONS']['SparqlEndpoint']
OPENCITATIONS_TITLE_VAR = config['OPENCITATIONS']['TitleVariable']

BVB_ENDPOINT = config['BVB']['SparqlEndpoint']
BVB_TITLE_VAR = config['BVB']['TitleVariable']
BVB_NAME = config['BVB']['Name']

ENDPOINTS = {k: v for k, v in config['ENDPOINT_NAME_ABBREVIATIONS_PAIRS'].items()}

KUBIKAT_NAME = config['KUBIKAT']['Name']
WORLDCAT_NAME = config['WORLDCAT']['Name']

DOI_URL = config['DOI']['LookupServiceURL']

STOPWORDS_FILE = os.path.join(
    config['WORKSPACE']['DictionariesFolder'],
    config['WORKSPACE']['StopwordsFile']
)

WORLD_CITIES = os.path.join(
    config['WORKSPACE']['DictionariesFolder'],
    config['WORKSPACE']['WorldCities']
)

CACHE_SIZE = int(config['CACHE']['MaxEntries'])

SESSION_PERMANENT = config['SESSION'].getboolean('Permanent')
PERMANENT_SESSION_LIFETIME = timedelta(hours=int(config['SESSION']['LifetimeInHours']))
SESSION_TYPE = config['SESSION']['Type']