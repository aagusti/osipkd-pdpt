from urllib import quote_plus
from sqlalchemy import create_engine


#db_url = 'DRIVER={FreeTDS};Server=192.168.56.1\\sql2008;Database=gaji_pbg;UID=sa;PWD=sa;Port=1433;TDS_Version=8.0'
#print(db_url)
#db_url = 'DSN=SQLServer2008;Database=gaji_pbg;UID=sa;PWD=sa'
db_url = 'DSN=SQLServer2008;UID=sa;PWD=sa'
db_url = quote_plus(db_url)
db_url = 'mssql+pyodbc:///?odbc_connect={0}'.format(db_url)

print(db_url)
eng = create_engine(db_url)
eng.connect()
