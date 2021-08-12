
import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')
sys.path.insert(0,'./espnLeagueData')
sys.path.insert(0,'./nflLeagueData')
from datetime import date, datetime, timedelta
import calendar
import pandas as pd

import traceback


from DOConn import connection
from DOsshTunnel import DOConnect
from maddenRatings import pullMaddenRatings




year = 2021
    
with DOConnect() as tunnel:
    c, conn = connection(tunnel)
    try:
        sql = pullMaddenRatings(conn,year)
        for statement in sql:
            try:
                c.execute(statement)
            except:
                print(statement)
                traceback.print_exc()
        conn.commit()
    except Exception as e:
        print(str(e))
        traceback.print_exc() 
    conn.close()
