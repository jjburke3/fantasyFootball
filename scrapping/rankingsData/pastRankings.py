import sys
sys.path.insert(0,'../..')
sys.path.insert(0,'../../dbConn')
from datetime import date, datetime, timedelta
import calendar
import pandas as pd

import traceback

from DOConn import connection
from DOsshTunnel import DOConnect

from pullRankings import pullFPRankings


now = datetime.utcnow() - timedelta(hours=4)




rankingsList = [
        {'year' : 2021,
         'link' : 'https://web.archive.org/web/20210914032218/https://www.fantasypros.com/nfl/rankings/ros-ppr-flex.php'
         }
    ]


for rankingYear in rankingsList:
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            c.execute('''select max(rankingVersion) as version
                     from scrapped_data2.fantasyProsRankings''')
            try:
                versionNo = (c.fetchone()[0]) + 1
            except:
                versionNo = 0
            print(versionNo)
            sql = pullFPRankings(conn,
                                  rankingYear['year'],
                                  2,
                                  '',
                                  '',
                                  versionNo,
                                  url=rankingYear['link'])
            for statement in sql:
                c.execute(statement)
            conn.commit()
        except Exception as e:
            traceback.print_exc() 
        conn.close()
