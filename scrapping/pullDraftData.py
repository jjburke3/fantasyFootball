
import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')
sys.path.insert(0,'./espnLeagueData')
from datetime import date, datetime, timedelta
import calendar

import pandas as pd

import traceback


from DOConn import connection
from DOsshTunnel import DOConnect


from leagueDraft import pullDraftData
from leagueMatchups import pullMatchupData

now = datetime.utcnow() - timedelta(hours=4)

year = (now - timedelta(days=60)).year



with DOConnect() as tunnel:
    c, conn = connection(tunnel)
    try:
        sql = pullDraftData(year,conn)
        for statement in sql:
            try:
                c.execute(statement)
            except:
                print(statement)
                traceback.print_exc()

        conn.commit()
        sql = pullMatchupData(year)
        for statement in sql:
            try:
                c.execute(statement)
            except:
                print(statement)
                traceback.print_exc()

        conn.commit()
    except Exception as e:
        print(str(e))



    conn.close()
