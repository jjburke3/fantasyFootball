import sys
sys.path.insert(0,'..')

from security import mysqlConn

import pymysql


sql_host = mysqlConn['host']
sql_user = mysqlConn['user']
sql_pw = mysqlConn['passwd']
sql_db = mysqlConn['db']

def connection(tunnel):
    conn = pymysql.connect(host=sql_host,
                               user=sql_user,
                               passwd=sql_pw,
                               db=sql_db,
                               port=tunnel.local_bind_port)

    c = conn.cursor()

    return c, conn
