import sys
sys.path.insert(0,'..')

from security import server_creds, mysqlConn

from sshtunnel import SSHTunnelForwarder


ssh_host = server_creds['host']
ssh_user = server_creds['username']
ssh_pw = server_creds['password']
sql_host = mysqlConn['host']

def DOConnect():
    tunnel = SSHTunnelForwarder(
    ssh_host,
    ssh_username=ssh_user,
    ssh_password=ssh_pw,
    remote_bind_address=(sql_host, 3306))
    return tunnel
        
