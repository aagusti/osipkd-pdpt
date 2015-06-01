import os
import sys
import transaction
from shutil import copyfile
from sqlalchemy import (
    engine_from_config,
    select,
    )
from sqlalchemy.schema import CreateSchema
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    init_model,
    DBSession,
    Base,
    )

from ..models.apbd_anggaran import *
from ..models.apbd import *
from ..models.apbd_tu import *

from ..models.gaji import *
from ..models.pemda_model import *    
from ..models.eis import *    
from ..models.aset_models import *    
from ..models.efiling_models import *   
import initial_data
from tools import mkdir


ALEMBIC_CONF = """    
[alembic]
script_location = ziggurat_foundations:migrations
sqlalchemy.url = {{db_url}}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""    
    


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def create_schema(engine, schema):
    sql = select([('schema_name')]).\
          select_from('information_schema.schemata').\
          where("schema_name = '%s'" % schema)
    q = engine.execute(sql)
    if not q.fetchone():
        engine.execute(CreateSchema(schema))

def create_schemas(engine):
    for schema in ['efiling', 'admin', 'aset', 'eis', 'gaji', 'apbd']:
        create_schema(engine, schema)

def copy_logo(settings):
    target_dir = os.path.realpath(settings['static_files'])
    target_file = os.path.join(target_dir, 'logo.png')
    if os.path.exists(target_file):
        return
    source_dir = os.path.join(os.path.split(__file__)[0], '..', '..', 'docs')
    source_dir = os.path.realpath(source_dir)
    source_file = os.path.join(source_dir, 'logo.png')
    copyfile(source_file, target_file)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    mkdir(settings['static_files'])
    copy_logo(settings)
    # Create Ziggurat tables
    alembic_ini_file = 'alembic.ini'
    if not os.path.exists(alembic_ini_file):
        alembic_ini = ALEMBIC_CONF.replace('{{db_url}}',
                                           settings['sqlalchemy.url'])
        f = open(alembic_ini_file, 'w')
        f.write(alembic_ini)
        f.close()
    bin_path = os.path.split(sys.executable)[0]
    alembic_bin = os.path.join(bin_path, 'alembic')
    command = '%s upgrade head' % alembic_bin
    os.system(command)
    os.remove(alembic_ini_file)
    # Insert data
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    init_model()
    create_schemas(engine)
    Base.metadata.create_all(engine)
    initial_data.insert()
    transaction.commit()
