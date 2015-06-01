import os
import sys
import transaction
from sqlalchemy import engine_from_config
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
from ..models import DBSession
from ..models.base_model import App

MAIN_TPL = """AppsData = [
{data}
]
"""

ROW_TPL = """\
    dict(
        id={id},
        kode='{kode}',
        nama='{nama}',
        tahun={tahun},
        ),"""

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    q = DBSession.query(App).order_by('id')
    data = []
    id = 0
    for row in q:
        id += 1
        row_s = ROW_TPL.format(id=id, kode=row.kode, nama=row.nama,
                tahun=row.tahun)
        data.append(row_s)
    data_s = '\n'.join(data)
    main_s = MAIN_TPL.format(data=data_s)
    print(main_s)
